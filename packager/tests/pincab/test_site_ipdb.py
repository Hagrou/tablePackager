import unittest
from packager.pincab.site_ipdb_org import Site_ipdb_org
from packager.tools.toolbox import *
from packager.model.config import Config
import re

class MyTestCase(unittest.TestCase):
    def setUp(self):
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s",
            handlers=[
                # logging.FileHandler("{0}/{1}.log".format(logPath, fileName)),
                logging.StreamHandler()
            ])
        self.logger = logging.getLogger(__name__)
        self.ipdb_site = Site_ipdb_org(self.logger)

    def test_valid_ipdb(self):
        info={}
        results=self.ipdb_site.search_pincab_info(4032,info)
        self.assertTrue(results['Theme']=='Fantasy - Medieval - Wizards/Magic')


    def test_search_pincab_ipdb_with_multiple_choices(self):
        self.assertTrue(self.ipdb_site.search_pincab_ipdb('american beauty', year='March, 1945', manufacturer='Westerhaus Amusement Company')==5451,'5451 expected')
        self.assertTrue(self.ipdb_site.search_pincab_ipdb('american beauty', year='April, 1945', manufacturer='Unknown Manufacturer')==2872,'2872 expected')
        self.assertTrue(self.ipdb_site.search_pincab_ipdb('american beauty', year='June, 1934',  manufacturer='Daval Mfg Company Incorporated, G.B.')==2873,'2873 expected')
        self.assertTrue(self.ipdb_site.search_pincab_ipdb('american beauty', year='February, 1934', manufacturer='Gee Bee Manufacturing Company') == 3640, '3640 expected')

    def test_search_pincab_ipdb_with_lower_case_bug(self):
        # ipdb can't found 'Bally Hoo' but found 'bally hoo'!!!
        self.assertTrue(self.ipdb_site.search_pincab_ipdb('Bally Hoo') == 151, '151 expected')

    def test_search_pincab_ipdb_with_valid_table(self):
        self.assertTrue(self.ipdb_site.search_pincab_ipdb('twilight zone')==2684,'2684 expected')

    def test_search_pincab_ipdb_with_a_Andromeda(self):
        self.assertTrue(self.ipdb_site.search_pincab_ipdb('Andromeda', year='1985-09')==73,'73 expected')

    def test_search_pincab_ipdb_with_a_coquette(self):
        self.assertTrue(self.ipdb_site.search_pincab_ipdb('Coquette')==567,'567 expected')

    def test_search_pincab_ipdb_with_a_charleston(self):
        self.assertTrue(self.ipdb_site.search_pincab_ipdb('Charleston Turbo')==6116,'6116 expected')

    def test_search_pincab_ipdb_with_a_4_square(self):
        self.assertTrue(self.ipdb_site.search_pincab_ipdb('4 Square')==940,'940 expected')

    def test_search_pincab_ipdb_with_a_4_in_one(self):
        self.assertTrue(self.ipdb_site.search_pincab_ipdb('4-IN-1 (Willy At The Bat)', year='December 09, 1985',
                                                          manufacturer='Williams Electronics Games, Incorporated, a subsidiary of WMS Ind., Incorporated') == 6008,  '6008 expected')
        self.assertTrue(self.ipdb_site.search_pincab_ipdb('4 Square')==940,'940 expected')

    def test_search_pincab_ipdb_with_date_format_pb(self):
        self.assertTrue(self.ipdb_site.search_pincab_ipdb('4x4', year='1983',
                                                          manufacturer='Atari, Incorporated') == 3111,  '3111 expected')

    def test_search_pincab_ipdb_with_slash_in_name(self):
        self.assertTrue(self.ipdb_site.search_pincab_ipdb('ac/dc', year='2013-12',
                                                          manufacturer='Stern Pinball, Incorporated') == 6060,  '6060 expected')

    """
       	Skip "AC/DC (Pro)/2012/Stern Pinball, Incorporated", unknwn ipdb
	Skip "All Out/April, 1943/Sullivan-Nolan Advertising Company [WWII Conversions Only]", unknwn ipdb
    	Skip "Automat/1936/Bally Manufacturing Corporation", unknwn ipdb => disable
                    &nore=1
    """

    def test_search_pincab_ipdb_with_a_bingo_machine(self):
        self.assertTrue(self.ipdb_site.search_pincab_ipdb('Adventure')==5544,'5544 expected')

    def test_search_pincab_ipdb_with_unvalid_table(self):
        self.assertTrue(self.ipdb_site.search_pincab_ipdb('######')==-1,'- expected')

    def test_search_pincab_ipdb_with_japon_chars(self):
        self.assertTrue(self.ipdb_site.search_pincab_ipdb('Skill Ball (スキルボール)')==6759,'6759 expected')

    def test_search_pincab_ipdb_with_regexp_pb(self):
        self.assertTrue(self.ipdb_site.search_pincab_ipdb('Automat',year='1936',
                                                          manufacturer='Bally Manufacturing Corporation',regex=True) == 4177,  '4177 expected')
if __name__ == '__main__':
    unittest.main()
