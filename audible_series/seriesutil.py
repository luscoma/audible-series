from collections import defaultdict, namedtuple
from datetime import date
import click
import csv


class LibraryBook(
        namedtuple('LibraryBook',
                   ['asin', 'title', 'series_title', 'book_num', 'release_date'])):

    @classmethod
    def from_row(cls, row):
        raw_sequence = row['series_sequence']
        if '-' in raw_sequence:
            sequence = float(raw_sequence.partition('-')[2])
        else:
            try:
                sequence = float(raw_sequence)
            except ValueError:
                # Sometimes sequence is empty or None due to weird series data
                sequence = 0
        return cls(
            row['asin'].strip(),
            row['title'].strip(),
            row['series_title'].strip(),
            sequence,
            date.fromisoformat(row['release_date'])
        )

    @classmethod
    def from_product(cls, product, series_title):
        return cls(
            product['asin'].strip(),
            product['title'].strip(),
            series_title.strip(),
            0,
            date.fromisoformat(product['release_date'])
        )

    @classmethod
    def external(cls, asin, series_title):
        return cls(asin, 'Unknown', series_title, 0, date.today())

    def format_for_click(self):
        title = click.style(self.title, bold=True)
        if self.release_date > date.today():
            days = click.style(
                f"{(self.release_date - date.today()).days} days",
                bold=True
            )
            return '\n'.join([
                click.style(
                    f"\t{self.series_title}: {title} ({self.asin})", fg='blue'),
                f"\t\tReleases in {days} on {self.release_date}"
            ])
        else:
            return f"\t{self.series_title}: {title} ({self.asin})"


class Librarian(namedtuple('Librarian', ['new', 'preordered', 'old'])):

    @classmethod
    def create(cls):
        return cls([], [], [])

    def classify(self, series_title, book, options):
        if not book:
            self.old.append(series_title)
            return

        if book.asin in options.disallowed_asins:
            self.old.append(series_title)
        elif book.asin in options.preordered_asins:
            self.preordered.append(book)
        else:
            self.new.append(book)

    def format_for_click(self):
        output = []
        if self.new:
            output.append("New books for the following series:")
            output.extend([
                book.format_for_click()
                for book in sorted(self.new, key=lambda b: b.series_title)
            ])
            output.append('\n')

        if self.preordered:
            output.append("These books already preordered:")
            output.extend([
                book.format_for_click()
                for book in sorted(self.preordered, key=lambda b: b.series_title)
            ])
            output.append('\n')

        if self.old:
            output.append("No new books for the following series:")
            output.extend(
                [f"\t{series_title}" for series_title in sorted(self.old)])
            output.append('\n')

        return '\n'.join(output)


def parse_library(library_file, series_to_skip):
    all_series = defaultdict(list)
    with open(library_file) as f:
        reader = csv.DictReader(f, dialect='excel-tab')
        for row in reader:
            series_title = row['series_title']
            if series_title and series_title not in series_to_skip:
                all_series[series_title].append(LibraryBook.from_row(row))
    return all_series


def extract_latest_in_series(series, external_library_overrides):
    latest = {}
    for series_title, books in series.items():
        override_asin = external_library_overrides.get(series_title)
        if override_asin:
            latest[series_title] = LibraryBook.external(
                override_asin,
                series_title
            )
        else:
            latest[series_title] = max(books, key=lambda x: x.book_num)
    return latest


def parse_sims_response(response, series_title):
    products = response["similar_products"]
    if products:
        return LibraryBook.from_product(products[0], series_title)
