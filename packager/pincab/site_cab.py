from packager.tools.toolbox import *
from packager.pincab.manufacturer import Manufacturer
from abc import ABCMeta, abstractmethod
from enum import Enum, unique

title_pattern_1 = re.compile('(?P<title>.*) \((?P<manufacturer>.*) (?P<year>[1-3][0-9]{3})?\)?')
title_pattern_2 = re.compile('(?P<title>.*) - (?P<year>[1-3][0-9]{3}) - .*')
title_pattern_3 = re.compile('(?P<title>.*) - (?P<manufacturer>.*) (?P<year>[1-3][0-9]{3}) - .*')
rom_pattern_1 = re.compile('(?P<title>.*).*\((?P<manufacturer>.*)\) - ROM .*')
rom_pattern_2 = re.compile('(?P<title>.*) - ROM .*')


@unique
class Pinfile_type(Enum):
    PINBALL_MACHINE=1
    VPX_TABLE = 2
    ROM_FILE = 3
    UNKN_FILE = 10

    def __str__(self):
        return self.name


    @staticmethod
    def value(type_str:str) -> int:
        if type_str == 'PINBALL_MACHINE':
            return Pinfile_type.PINBALL_MACHINE
        if type_str == 'VPX_TABLE':
            return Pinfile_type.VPX_TABLE
        if type_str == 'ROM_FILE':
            return Pinfile_type.ROM_FILE
        print('Invalid type (%s)' % type_str)
        return Pinfile_type.UNKN_FILE

class Site_Cab:
    def __init__(self, debug_mode=False):
        self.__cookies = None
        self.__cache = {}
        self.__debug_mode = debug_mode

    @property
    def debug_mode(self):
        return self.__debug_mode

    @debug_mode.setter
    def debug_mode(self, value:bool):
        self.__debug_mode=value


    @abstractmethod
    def search_pincab_urls(self, table_name: str, max_result: int = 200) -> list:
        pass

    @abstractmethod
    def extract_download_info(self, url: str, info: dict) -> dict:
        pass


    @staticmethod
    def search_pincab_urls_filter(pincab_name: str, urls: list, filter_value: int = 2) -> list:
        """
        try to reduce search list
        :param pincab_name
        :param urls first result list
        :param filter_value max levenshtein distance
        :return: short list
        """
        short_list = []
        pincab_name, pincab_manufacturer, pincab_year = Site_Cab.extract_pincab_info_from_title(pincab_name)
        for url in urls:
            name, manufacturer, year = Site_Cab.extract_pincab_info_from_title(url['name'])
            if iterative_levenshtein(pincab_name, name) <= filter_value:
                short_list.append(url)
        return short_list

    @staticmethod
    def strip_pincab_name(name: str, strip_str_list: list = None) -> str:
        tmp_str = name
        if strip_str_list is None:
            strip_str_list = ['mp3', 'Table Audio', 'Pinball VPX', 'vp9.1.x', 'VP9.', '1.1', '1.2', 'FS', 'SS']
        for strip_str in strip_str_list:
            pos = tmp_str.rfind(strip_str)
            if pos != -1:
                tmp_str = tmp_str[:pos] + tmp_str[pos + len(strip_str):]
        tmp_str = tmp_str.strip(' .-')
        return tmp_str

    @staticmethod
    def extract_pincab_info_from_title(pincab_title: str, manufacturer_db:Manufacturer) -> (str, str, int):
        """
        TODO: check case with lot of parenthesis
        Gottlieb Premier Cactus Jack's - 1991 - VP8 to VPX conversion

        1-2-3... (Automaticos 1973) -> ('1-2-3',1973)
        :param pincab_title:
        :return:
        """
        pincab_title = pincab_title.replace('_', ' ')
        pos = pincab_title.find(')')
        if pos != -1:  # close parenthesis found
            pincab_title = pincab_title[:pos + 1]
            sub_table_name = title_pattern_1.search(pincab_title)
            if sub_table_name is None:
                pos = pincab_title.find('(')
                if pos != -1:
                    return pincab_title[:pos - 1], None, None
                return pincab_title, None, None

            table_name = Site_Cab.strip_pincab_name(sub_table_name.group('title'))
            table_manufacturer = sub_table_name.group('manufacturer')
            table_year = sub_table_name.group('year')
            return table_name, table_manufacturer, table_year
        pos = pincab_title.find('(')
        if pos != -1:
            return Site_Cab.strip_pincab_name(pincab_title[:pos]), None, None
        else:
            manufacturer = None
            sub_table_name = title_pattern_2.search(pincab_title)
            if sub_table_name is not None:
                table_name = Site_Cab.strip_pincab_name(sub_table_name.group('title'))
                table_year = sub_table_name.group('year')
                pos = table_name.find(' ')
                if pos != -1:
                    manufacturer=manufacturer_db.get_trade_name(table_name[:pos])
                    if manufacturer != '':
                        return table_name[pos+1:], manufacturer, table_year
                return table_name, None, table_year
            else:
                sub_table_name = title_pattern_3.search(pincab_title)
                if sub_table_name is not None:
                    table_name = Site_Cab.strip_pincab_name(sub_table_name.group('title'))
                    table_manufacturer = Site_Cab.strip_pincab_name(sub_table_name.group('manufacturer'))
                    table_year = sub_table_name.group('year')
                    return table_name, table_manufacturer, table_year
        return Site_Cab.strip_pincab_name(pincab_title), None, None

    def extract_pincab_info_from_rom_filename(self, rom_filename: str) -> (str, str, int):
        """
        Addams Family Values (L-4) - ROM - afv_l4.zip
        Alley Cats (L-7) - ROM - alcat_l7.zip
        Allied Leisure - ROM - allied.zip
        Aristocrat - ROM - arist_l1.zip
        Atlantis (LTD) - ROM - atla_ltd.zip
        Ator (Videodens) - ROM - ator.zip
        Beat the Clock - ROM - beatclck.zip
        Big Ball Bowling - ROM - bbbowlin.zip
        Big Strike - ROM - bstrk_l1.zip
        Black Beauty - ROM - blbeauty.zip
        Black Hole (LTD) - ROM - bhol_ltd.zip
        Brooklyn - ROM - brooklyn.zip
        Continental - ROM - cntinntl.zip
        Cut the Cheese (Data East) - ROM - ctcheese.zip
        Cut the Cheese Deluxe (Whitestar) - ROM - ctchzdlx.zip
        Data East Test Chip - ROM - detest.zip
        :param rom_filename:
        :return:
        """
        pos = rom_filename.find('(')
        if pos != -1:  # <name> (<manufacturer>) - ROM - <filename>.zip form
            sub_rom_name = rom_pattern_1.search(rom_filename)
            if sub_rom_name is not None:
                return sub_rom_name.group('title').strip(' '), sub_rom_name.group('manufacturer').strip(' '), None
        else:
            sub_rom_name = rom_pattern_2.search(rom_filename)
            if sub_rom_name is not None:
                return sub_rom_name.group('title').strip(' '), None, None
        return rom_filename, None, None

    # deprecated ?
    # def search_table_url(self, table_name: str, criteria: list) -> dict:
    #     """
    #     looking for download url of a table
    #
    #     :param table_name:
    #     :param criteria:
    #     :return:
    #     """
    #     # search download info in cache
    #     search_level = 1
    #     while search_level <= 2:
    #         results = {'max_score': 0.0, 'min_score': sys.float_info.max, 'count': 0, 'list': []}
    #         print('%d: searching url for table \'%s\'' % (search_level, table_name))
    #
    #         if table_name in self.__cache:
    #             print('\tin cache !')
    #             pages_info = self.__cache[table_name]
    #         else:  # not in cache, search it on the net
    #             print('\tnot in cache, search on the net')
    #             try:
    #                 pages_info = self.search_download_info(table_name)
    #             except Exception as e:
    #                 pages_info['error'] = self.compute_score(pages_info, criteria)
    #                 continue
    #
    #             self.__cache[table_name] = pages_info  # store result in cache
    #
    #         # compute score for each page
    #         for page_info in pages_info:
    #             page_info['score'] = self.compute_score(page_info, criteria)
    #             if results['max_score'] < page_info['score']:
    #                 results['max_score'] = page_info['score']
    #             if results['min_score'] > page_info['score']:
    #                 results['min_score'] = page_info['score']
    #             results['list'].append(page_info)
    #
    #         # no result? search with part of table_name
    #         if results['max_score'] == 0.0:
    #             sub_table_name = self.title_pattern.search(table_name)
    #             if sub_table_name is not None:
    #                 table_name = sub_table_name.group('title')
    #                 search_level = search_level + 1
    #                 continue
    #         break
    #
    #     results['count'] = len(results['list'])
    #     results['list'] = sorted(results['list'], reverse=True, key=lambda x: x['score'])
    #     return results

    def dump_html(self, html_page: object) -> None:
        """
        dump html page into file (for debug purpose)
        :return:
        """
        filepath = '%s/page.html' % os.getcwd()
        file = open(filepath, 'wb')
        file.write(html_page.content)
        file.close()
        # webbrowser.open_new_tab('file:///%s' % filepath)
