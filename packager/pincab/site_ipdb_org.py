import requests
import unicodedata
import traceback
import re
import os

import webbrowser
import sys
from bs4 import BeautifulSoup
from packager.tools.toolbox import *
from packager.pincab.site_cab import *
from packager.tools.exception import *

import time



class Site_ipdb_org(Site_Cab):
    re_extract_ipdb = re.compile('.*id=(?P<ipdb>\d+)')

    def __init__(self, logger, debug_mode=False):
        self.__ipdb_url = 'https://www.ipdb.org/machine.cgi?id=%d'
        self.__ipdb_search_url = 'https://www.ipdb.org/search.pl?any=%s&sortby=name&search=Search+Database&searchtype=quick'
        self.__ipdb_full_list = 'https://www.ipdb.org/lists.cgi?anonymously=true&list=games'
        self.__re_extract_rating = re.compile('.*(?P<rate>\d+\.\d+).*')
        self.__debug_mode = debug_mode
        self.__logger = logger

    @property
    def debug_mode(self):
        return self.__debug_mode

    @debug_mode.setter
    def debug_mode(self, value: bool):
        self.__debug_mode = value

    def __extract_rate(self, value: str) -> float:
        """
        extract rating value, ie: 7.6/10  (40 ratings/30 comments)        [ Add Your Rating! ] -> 7.6
        :param value:
        :return: rate value, of <0 for no rating value
        """
        match = self.__re_extract_rating.search(value)
        if match is not None:
            return float(match.group('rate'))
        return -1.0

    def search_pincab_info(self, ipdb: int, pincab: dict) -> dict:
        """
        search ipdb info
        :param ipdb: ipdb number
        :param pincab: pincab info
        :return:
        """
        try:
            http_search = requests.get(self.__ipdb_url % ipdb)
        except Exception as e:
            raise ConnectionException('', url=self.__ipdb_url % ipdb, error_code=http_search.status_code)

        if http_search.status_code != 200:
            raise ConnectionException('', url=self.__ipdb_url % ipdb, error_code=http_search.status_code)

        pincab['IPDB Number'] = ipdb
        soup = BeautifulSoup(http_search.text, 'html.parser')
        for items in soup.find_all('table'):
            for line_tag in items.find_all('tr'):
                column = line_tag.find('td')
                txt = column.getText()
                if txt == 'Average Fun Rating: ':
                    column = column.findNext('td')
                    pincab['Fun Rating'] = self.__extract_rate(unicodedata.normalize("NFKD", column.getText()))
                elif txt == 'Manufacturer: ':
                    column = column.findNext('td')
                    pincab['Manufacturer'] = unicodedata.normalize("NFKD", column.getText())
                elif txt == 'Date Of Manufacture: ':
                    column = column.findNext('td')
                    pincab['Year'] = unicodedata.normalize("NFKD", column.getText())
                elif txt == 'Theme: ':
                    column = column.findNext('td')
                    pincab['Theme'] = unicodedata.normalize("NFKD", column.getText())
                elif txt == 'Design by: ':
                    column = column.findNext('td')
                    pincab['Design by'] = unicodedata.normalize("NFKD", column.getText())
                elif txt == 'Art by: ':
                    column = column.findNext('td')
                    pincab['Art by'] = unicodedata.normalize("NFKD", column.getText())
                elif txt == 'Notes: ':
                    column = column.findNext('td')
                    pincab['Notes'] = unicodedata.normalize("NFKD", column.getText())
        pincab['IPDB Check'] = True
        return pincab

    def search_pincab_ipdb(self, pincab_name: str, year: str = '', manufacturer:str = '', regex:bool=False) -> int:
        """
        search ipdb info from pincab_name
        :param pincab_name:
        :param year:
        :param manufacturer:
        :return: ipdb number (or 0 if not found)
        """
        if regex:
            url = (self.__ipdb_search_url + '&nore=1') % pincab_name.lower().replace('/', '')
        else:
            url = self.__ipdb_search_url % pincab_name.lower().replace('/', '')

        try:
            http_search = requests.get(url)
        except Exception:
            raise ConnectionException('', url=url, error_code=http_search.status_code)

        if http_search.status_code != 200:
            raise ConnectionException('', url=url, error_code=http_search.status_code)

        if self.debug_mode:
            self.dump_html(http_search)

        try:
            soup = BeautifulSoup(http_search.text, 'html.parser')
            items = soup.find('table', {'id': 'gamelist'})
            if items is None: # 1 record match
                tables = soup.find_all('table')
                items=tables[3]
                raw_item=items.find('tr')
                col_item = list(raw_item.find_all('td'))
                if len(col_item) == 0:
                    return -1
                if 'The following names did not match' in raw_item.getText(): # Not found, but similar
                    for col_item in list(items.find_all('td')):
                        flipper_item = col_item.find('a')
                        if flipper_item is None:
                            continue
                        if flipper_item.getText()==pincab_name:
                            return Site_ipdb_org.extract_ipdb_from_url(flipper_item.get('href'))
                    return -1
                flipper_item = col_item[1].find('a')
                if flipper_item is None or flipper_item.get('name') is None:
                    return -1
                return int(flipper_item.get('name'))

            else: # multiple records matches
                date=year
                mfg=manufacturer
                for raw_item in items.find_all('tr'):
                    col_item = list(raw_item.find_all('td'))
                    if len(col_item) == 0: # table headers, skit it
                        continue

                    if year != '':
                        date=str_2_struct_time(col_item[0].get_text().strip(' '))
                        if date is not None:
                            date =struct_time_2_datetime(date).strftime('%Y-%m')
                        year=str_2_struct_time(year)
                        if year is not None:
                            year =struct_time_2_datetime(year).strftime('%Y-%m')

                    if manufacturer != '':
                        mfg_node= col_item[2].find('span')
                        if mfg_node is not None:
                            mfg=mfg_node.get('title')

                    flipper_item = col_item[1].find('a', {'class': 'linkid'})
                    if flipper_item is None:
                        continue
                    if pincab_name.upper() in flipper_item.get_text().upper() and mfg == manufacturer and date==year:
                        href=flipper_item.get('href')
                        if href[0]=='#':
                            return int(href[1:])
                        else:
                            ipdb=Site_ipdb_org.extract_ipdb_from_url(flipper_item.get('href'))
                            if ipdb == -1:
                                print('Error, Invalid id for "%s"' % flipper_item.get('href'))
                            return ipdb
        except ValueError as e:
            print('Value Error with pinball machine [%s]' % pincab_name)
        except IndexError as e:
            print('Error: Index out of range for [%s]' % pincab_name)
        return -1

    def get_all_pinball_machine(self) -> list:
        """
        get all Machine Data Base
        :return: list of machines
        """
        try:
            http_search = requests.get(self.__ipdb_full_list)
        except Exception:
            raise ConnectionException('', url=self.__ipdb_full_list, error_code=http_search.status_code)

        if http_search.status_code != 200:
            raise ConnectionException('', url=self.__ipdb_full_list, error_code=http_search.status_code)

        soup = BeautifulSoup(http_search.text, 'html.parser')
        pinball_machines = []
        items = soup.find('table')
        for raw_item in items.find_all('tr'):
            col_item = list(raw_item.find_all('td'))
            if len(col_item) == 0:
                continue

            name=col_item[0].getText()
            if 'Unknown' in name:
                continue
            normalize_name = name
            normalize_name = normalize_name.replace('\x92','\'')
            normalize_name = normalize_name.replace('®', '')
            normalize_name = normalize_name.replace('·', '-')
            normalize_name = normalize_name.replace('\x95', ' ')
            normalize_name = normalize_name.replace('...', '')
            normalize_name = normalize_name.replace('\x99', '')
            normalize_name = normalize_name.replace('\x9161', '')
            normalize_name = normalize_name.replace('\x9162', '')
            normalize_name = normalize_name.replace('(アポロボール)', '')
            normalize_name = normalize_name.replace('(アポロムーン)', '')
            normalize_name = normalize_name.replace('(ベースボール)', '')
            normalize_name = normalize_name.replace('(ベースボール2)', '')
            normalize_name = normalize_name.replace('(ビート＆スパーク)', '')
            normalize_name = normalize_name.replace('(クレイジー15)', '')
            normalize_name = normalize_name.replace('(大宇宙旅行)', '')
            normalize_name = normalize_name.replace('(インディゲーム)', '')
            normalize_name = normalize_name.replace('(ジャンボキック)', '')
            normalize_name = normalize_name.replace('(スキルボール)', '')
            normalize_name = normalize_name.strip('\'"!`. \x84\x94')
            info = {'Normalize Name': normalize_name,
                    'Name': col_item[0].getText().strip('\'"'), 'Manufacturer': col_item[1].getText(),
                    'Date Manufactured': col_item[2].getText(),
                    'Players': col_item[3].getText(), 'Type': col_item[4].getText(), 'Theme': col_item[5].getText()}
            pinball_machines.append(info)
        return pinball_machines

    @staticmethod
    def extract_ipdb_from_url(url:str) -> int:
        match = Site_ipdb_org.re_extract_ipdb.search(url)
        if match is None:
            return -1
        return int(match.group('ipdb'))

        