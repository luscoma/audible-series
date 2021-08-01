from collections import defaultdict, namedtuple
from datetime import date
import click
import csv


class LibraryBook(
        namedtuple('LibraryBook',
                   ['asin', 'title', 'series_title', 'book_num', 'release_date'])):
    """A audible book, usually from the user's library.

    Attributes:
      asin: The audible id of this book
      title: Title of the book
      series_title: The series title of the book
      book_num: The number of this book in the series.  This can sometimes be a
                suprisingly value like 1-3 for compilations.
      release_date: The date this book was or will be released.

    Note: This data structure is reused for some API responses and config
    objects for convenience.  In certain cases fields may not be populated. For
    books parsed from the user's library file, all fields will always be
    populated.
    """

    @classmethod
    def from_row(cls, row):
        """Creates a LibraryBook from an audible-cli library file row.

        Series sequence may be some weird values so we try our best to parse it
        and otherwise fallback to pretending it's 0.
        """
        raw_sequence = row['series_sequence']
        if not raw_sequence:
            sequence = 0
        elif type(raw_sequence) == str and '-' in raw_sequence:
            sequence = float(raw_sequence.strip().partition('-')[2])
        else:
            try:
                sequence = float(raw_sequence.strip())
            except ValueError:
                # Sometimes sequence is empty or None due to weird series data
                sequence = 0
        return cls(
            row['asin'].strip(),
            row['title'].strip(),
            row['series_title'].strip(),
            sequence,
            date.fromisoformat(row['release_date'].strip())
        )

    @classmethod
    def from_product(cls, product, series_title):
        """Creates a LibraryBook from an API releated product entry.

        Only some data is provided and data like book num will not be populated.
        """
        return cls(
            product['asin'].strip(),
            product['title'].strip(),
            series_title.strip(),
            0,
            date.fromisoformat(product['release_date'].strip())
        )

    @classmethod
    def external(cls, asin, series_title):
        """Creates a stub LibraryBook based on partial config data."""
        return cls(asin, 'Unknown', series_title, 0, date.today())

    # Note: In an ideal world this would not be in this util since click is
    # really unreleatd and a cli output thing.  It's convenient though.
    def format_for_click(self):
        """Formats a book for output on the console."""
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
    """A helper for organizing LibraryBook objects.

    The Librarian utilizes passed in config data to determine the classification
    of a book in the user's library (new, preordered, or old).

    Book Types:
      new: The next book in a series not yet in the user's library.
      preordered: A new book already preordered by the user.
      old: A list of series titles which have no new books.

    Note:  In certain cases series titles may be marked as ignored which forces
    them into the old category regardless of their status in the library.
    """

    @classmethod
    def create(cls):
        return cls([], [], [])

    def classify(self, series_title, book, options):
        """Adds a book to the appropriate classification list."""
        if not book:
            self.old.append(series_title)
            return

        if book.asin in options.disallowed_asins:
            self.old.append(series_title)
        elif book.asin in options.preordered_asins:
            self.preordered.append(book)
        else:
            self.new.append(book)

    # See note on LibraryBook.format_for_click
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
