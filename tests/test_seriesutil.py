from audible_series import __version__
from parameterized import parameterized
import unittest


class LibraryBookTestCase(unittest.TestCase):

    @parameterized([ None, 'Alex' ])
    def test_from_row_handles_invalid_sequence(self, sequence):
        row = {
            'asin': 'ASIN',
            'title': 'title',
            'series_title': 'series_title',
            'release_data': '2021-07-01',
            'series_sequence': sequence
        }
        book = LibraryBook.from_row( row )
        self.assertEquals( 0, book.book_num )

def test_version():
    assert __version__ == '0.1.0'
