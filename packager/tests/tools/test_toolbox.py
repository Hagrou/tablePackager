import unittest
import traceback
import sys
from packager.tools.toolbox import *
from packager.tools.exception import *

class Toolbox_TestCase(unittest.TestCase):
    def test_iterative_levenshtein(self):
        self.assertTrue(iterative_levenshtein('flaw', 'lawn') == 2)

    def test_str_2_date(self):
        self.assertTrue(struct_time_2_datetime(str_2_struct_time('2021-04-03T23:01:06Z')).strftime('%Y-%m-%d') == '2021-04-03',
                        'Wrong format for 2021-04-03T23:01:06Z')
        self.assertTrue(struct_time_2_datetime(str_2_struct_time('1934-02')).strftime('%Y-%m-%d') == '1934-02-01',
                        'Wrong format for 1934-02')
        self.assertTrue(struct_time_2_datetime(str_2_struct_time('2019-01-16')).strftime('%Y-%m-%d') == '2019-01-16',
                        'Wrong format for 2019-08-16')
        self.assertTrue(struct_time_2_datetime(str_2_struct_time('01-16-2019')).strftime('%Y-%m-%d') == '2019-01-16',
                        'Wrong format for 08-16-2019')
        self.assertTrue(
            struct_time_2_datetime(str_2_struct_time('January 16, 2019')).strftime('%Y-%m-%d') == '2019-01-16',
            'Wrong format for January 16, 2019')

        self.assertTrue(
            struct_time_2_datetime(str_2_struct_time('Jan 14 2021 10:12 PM')).strftime('%Y-%m-%d') == '2021-01-14',
            'Wrong format for Jan 14 2021 10:12 PM')
        self.assertTrue(struct_time_2_datetime(str_2_struct_time('March, 1932')).strftime('%Y-%m-%d') == '1932-03-01',
                        'Wrong format for March, 1932')
        self.assertTrue(struct_time_2_datetime(str_2_struct_time('1983')).strftime('%Y-%m') == '1983-01',
                        'Wrong format for 1983')
        self.assertTrue(struct_time_2_datetime(str_2_struct_time('1932')).strftime('%Y-%m-%d') == '1932-01-01',
                        'Wrong format for 1932')

        self.assertTrue(str_2_struct_time('blabla') == None, 'Error if not a date')

    def test_exception(self):
        try:
            error=traceback.format_exc()
            raise ConnectionException(url='url')
        except Exception as ex:
            print(ex)

if __name__ == '__main__':
    unittest.main()
