from audible_series import seriesutil
from collections import namedtuple
from parameterized import parameterized
from datetime import date
import unittest


class LibraryBookTestCase(unittest.TestCase):

    def testrow(self, **opts):
        row = {
            'asin': 'ASIN',
            'title': 'title',
            'series_title': 'series_title',
            'release_date': '2021-07-01',
            'series_sequence': '1'
        }
        row.update(opts)
        return row

    def test_creates_valid_row(self):
        book = seriesutil.LibraryBook.from_row(self.testrow())
        expected = seriesutil.LibraryBook(
            asin='ASIN',
            title='title',
            series_title='series_title',
            release_date=date(2021, 7, 1),
            book_num=1
        )
        self.assertEqual(expected, book)

    def test_creates_valid_row_strips_space(self):
        book = seriesutil.LibraryBook.from_row({
            k: f' {v} ' for k, v in self.testrow().items()
        })
        expected = seriesutil.LibraryBook(
            asin='ASIN',
            title='title',
            series_title='series_title',
            release_date=date(2021, 7, 1),
            book_num=1
        )
        self.assertEqual(expected, book)

    @parameterized.expand([(None,), ('Alex',)])
    def test_from_row_handles_invalid_sequence(self, sequence):
        row = self.testrow(series_sequence=sequence)
        book = seriesutil.LibraryBook.from_row(row)
        self.assertEqual(0, book.book_num)

    def test_parses_compilation_sequence_num(self):
        row = self.testrow(series_sequence='1-3')
        book = seriesutil.LibraryBook.from_row(row)
        self.assertEqual(3, book.book_num)

    def test_create_from_product(self):
        # We also test that it strips whitespace just in case
        product = {
            'asin': ' asin ',
            'title': ' title ',
            'release_date': ' 2021-07-01 '
        }
        book = seriesutil.LibraryBook.from_product(product, ' series ')
        expected = seriesutil.LibraryBook(
            asin='asin',
            title='title',
            series_title='series',
            release_date=date(2021, 7, 1),
            book_num=0
        )
        self.assertEqual(expected, book)

    def test_create_from_external(self):
        book = seriesutil.LibraryBook.external('asin', 'series')
        expected = seriesutil.LibraryBook(
            asin='asin',
            title='Unknown',
            series_title='series',
            release_date=date.today(),
            book_num=0
        )
        self.assertEqual(expected, book)


FakeConfig = namedtuple('FakeConfig', ['disallowed_asins', 'preordered_asins'])

BOOK1 = seriesutil.LibraryBook.external('asin', 'series')
BOOK2 = seriesutil.LibraryBook.external('asin2', 'series2')
BOOK3 = seriesutil.LibraryBook.external('asin3', 'series3')


class LibrarianTestCase(unittest.TestCase):

    def classifybooks(self, options):
        l = seriesutil.Librarian.create()
        for book in [BOOK1, BOOK2, BOOK3]:
            l.classify(book.series_title, book, options)

        return l

    def test_disallow(self):
        options = FakeConfig(['asin'], [])
        l = self.classifybooks(options)
        self.assertCountEqual(l.old, ['series'])
        self.assertCountEqual(l.new, [BOOK2, BOOK3])
        self.assertCountEqual(l.preordered, [])

    def test_preorder(self):
        options = FakeConfig([], ['asin2'])
        l = self.classifybooks(options)
        self.assertCountEqual(l.old, [])
        self.assertCountEqual(l.new, [BOOK1, BOOK3])
        self.assertCountEqual(l.preordered, [BOOK2])

    def test_nonebook(self):
        options = FakeConfig([], [])
        l = self.classifybooks(options)
        l.classify('none', None, options)
        self.assertCountEqual(l.old, ['none'])
        self.assertCountEqual(l.new, [BOOK1, BOOK2, BOOK3])
        self.assertCountEqual(l.preordered, [])
