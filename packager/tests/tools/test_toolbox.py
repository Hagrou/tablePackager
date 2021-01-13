import unittest
from packager.tools.toolbox import *


class Toolbox_TestCase(unittest.TestCase):
    def test_iterative_levenshtein(self):
        self.assertTrue(iterative_levenshtein('flaw', 'lawn') == 2)

    def test_str_2_date(self):
        self.assertTrue(struct_time_2_datetime(str_2_struct_time('2019-01-16')).strftime('%Y-%m-%d') == '2019-01-16', 'Wrong format for 2019-08-16')
        self.assertTrue(struct_time_2_datetime(str_2_struct_time('01-16-2019')).strftime('%Y-%m-%d') == '2019-01-16', 'Wrong format for 08-16-2019')
        self.assertTrue(struct_time_2_datetime(str_2_struct_time('January 16, 2019')).strftime('%Y-%m-%d') == '2019-01-16',
                        'Wrong format for January 16, 2019')
        self.assertTrue(str_2_struct_time('blabla') == None, 'Error if not a date')





if __name__ == '__main__':
    unittest.main()
