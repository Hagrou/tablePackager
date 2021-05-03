import requests

import re
import os

import webbrowser
import sys

from bs4 import BeautifulSoup
from packager.tools.toolbox import *
from packager.pincab.site_cab import *
from packager.pincab.site_ipdb_org import Site_ipdb_org
from packager.tools.exception import *
import time


class Site_vpforum_com(Site_Cab):
    def __init__(self, logger):
        super().__init__()
        self.__login_url = 'https://www.vpforums.org'
        self.__search_url = 'https://www.vpforums.org/index.php?app=core&module=search&section=search&do=search&fromsearch=1'
        self.__search_all_VPX_table = 'http://www.vpforums.org/index.php?app=downloads&showcat=52'
        self.__search_all_ROMs = 'http://www.vpforums.org/index.php?app=downloads&showcat=9'
        self.__logger = logger
        # self.__connected = False

    # def search_all_VPX_table(self, max_table=-1) -> list:
    #     """
    #     search all VPX table in vpforum
    #     :param max_table: max table to found (-1: no limit)
    #     :return: list of info with the better url or None for error
    #     """
    #
    #     http_search=None
    #     try:
    #         http_req_login = requests.post(self.__login_url)
    #         if http_req_login.status_code != 200:
    #            raise Exception(self.__login_url + ' error (%d) ' % http_req_login.status_code)
    #         http_search = requests.post(
    #             self.__search_all_VPX_table,
    #             cookies=http_req_login.cookies)
    #         if http_search.status_code != 200:
    #             raise Exception(self.__search_url + ' error (%d) ' % http_req_login.status_code)
    #     except Exception:
    #         print("Error Exception %s" % traceback.format_exc())  # TODO: manage exception
    #         return None
    #
    #     self.dump_html(http_search)
    #     info_list = []
    #
    #     # get all result pages urls
    #     while True:
    #         next_page = None
    #         soup = BeautifulSoup(http_search.text, 'html.parser')
    #         for pages_url in soup.find_all('li', {'class': 'next'}):
    #             if pages_url is not None:
    #                 for link in pages_url.find_all('a'):
    #                     next_page = link.get('href')
    #
    #         for items in soup.find_all('div', {'id': 'idm_category'}):
    #             # extract download type
    #             for line_tag in items.find_all('div', {'class': 'basic_info'}):
    #                 #download_type_tag = line_tag.find('span', {'class': 'desc blend_links toggle_notify_off'})
    #                 #download_type = []
    #                 #for link in download_type_tag.find_all('a'):
    #                 #    download_type.append(link.getText())
    #
    #                 info = {'type': 'VPX Tables' } # TODO
    #                 subtitle = line_tag.find('h3', {'class': 'ipsType_subtitle'})
    #                 if subtitle is None:  # bad page, no info to found
    #                     continue
    #
    #                 for link in subtitle.find_all('a'):
    #                     title = link.get('title')
    #                     if title is None or 'View file named' not in title:
    #                         continue
    #                     info['name'] = title[16:]
    #                     url = link.get('href')
    #                     text = link.getText()
    #                     if url is None or text == '': continue  # uploader url is author info
    #                     info['url'] = url
    #                     info_list.append(info)
    #                     if max_table>0 and max_table==len(info_list):
    #                         next_page=None
    #                         break
    #
    #         if next_page is None:
    #             break
    #         http_search = requests.post(next_page, cookies=http_req_login.cookies)
    #         # self.dump_html(http_search)
    #
    #         if http_search.status_code != 200:
    #             raise Exception(self.__search_url + ' error (%d) ' % http_req_login.status_code)
    #
    #     return info_list

    def search_all_table(self, file_type: Pinfile_type, max_table=-1) -> list:
        """
        search all VPX table in vpforum
        :param file_type file to found
        :param max_table: max table to found (-1: no limit)
        :return: list of info with the better url or None for error
        """

        if Pinfile_type.VPX_TABLE == file_type:
            type_name = file_type.name
            search_url = self.__search_all_VPX_table
        elif Pinfile_type.ROM_FILE == file_type:
            type_name = file_type.name
            search_url = self.__search_all_ROMs

        http_search = None
        http_req_login = None
        try:
            http_req_login = requests.post(self.__login_url)
        except Exception as e:
            raise ConnectionException(error_code=http_req_login.status_code)
        if http_req_login.status_code != 200:
            raise ConnectionException(url=self.__login_url, error_code=http_req_login.status_code)
        try:
            http_search = requests.post(search_url, cookies=http_req_login.cookies)
        except Exception as e:
            raise ConnectionException(url=search_url, error_code=http_search.status_code)
        if http_search.status_code != 200:
            raise ConnectionException(url=search_url, error_code=http_search.status_code)

        if self.debug_mode:
            self.dump_html(http_search)

        info_list = []

        # get all result pages urls
        while True:
            next_page = None
            soup = BeautifulSoup(http_search.text, 'html.parser')
            for pages_url in soup.find_all('li', {'class': 'next'}):
                if pages_url is not None:
                    for link in pages_url.find_all('a'):
                        next_page = link.get('href')

            for items in soup.find_all('div', {'id': 'idm_category'}):
                # extract download type
                for line_tag in items.find_all('div', {'class': 'basic_info'}):
                    info = {'type': type_name}
                    subtitle = line_tag.find('h3', {'class': 'ipsType_subtitle'})
                    if subtitle is None:  # bad page, no info to found
                        continue

                    for link in subtitle.find_all('a'):
                        title = link.get('title')
                        if title is None or 'View file named' not in title:
                            continue
                        info['name'] = title[16:]
                        url = link.get('href')
                        text = link.getText()
                        if url is None or text == '': continue  # uploader url is author info
                        info['url'] = url
                        info_list.append(info)
                        if max_table > 0 and max_table == len(info_list):
                            next_page = None
                            break
            if next_page is None:
                break

            try:
                http_search = requests.post(next_page, cookies=http_req_login.cookies)
            except Exception:
                raise ConnectionException(url=next_page, error_code=http_search.status_code)
            if http_search.status_code != 200:
                raise ConnectionException(url=next_page, error_code=http_search.status_code)
            if self.debug_mode:
                self.dump_html(http_search)

        return info_list

    def search_pincab_urls(self, pincab_name: str, max_result: int = 200) -> list:
        """
        search all urls for a table
        :param pincab_name: the table to find
        :param max_result to take into account
        :return: list of info with the better url or None for error
        """
        http_req_login=None
        try:
            http_req_login = requests.post(self.__login_url)
        except Exception:
            raise ConnectionException(url=self.__login_url, error_code=http_req_login.status_code)
        if http_req_login.status_code != 200:
            raise ConnectionException(url=self.__login_url, error_code=http_req_login.status_code)

        http_search = None
        try:
            http_search = requests.post(
                self.__search_url,
                self.__build_request(pincab_name),
                cookies=http_req_login.cookies)
        except Exception:
            raise ConnectionException(url=self.__search_url, error_code=http_search.status_code)

        if http_search.status_code != 200:
            raise ConnectionException(url=self.__search_url, error_code=http_search.status_code)

        if self.debug_mode:
            self.dump_html(http_search)

        info_list = []

        # get all result pages urls
        while True:
            next_page = None
            soup = BeautifulSoup(http_search.text, 'html.parser')
            for pages_url in soup.find_all('li', {'class': 'next'}):
                if pages_url is not None:
                    for link in pages_url.find_all('a'):
                        next_page = link.get('href')

            for items in soup.find_all('table', {'id': 'forum_table'}):
                # extract download type
                for line_tag in items.find_all('tr', {'class': ''}):
                    download_type_tag = line_tag.find('span', {'class': 'desc blend_links toggle_notify_off'})
                    download_type = []
                    for link in download_type_tag.find_all('a'):
                        download_type.append(link.getText())

                    info = {'type': download_type}
                    subtitle = line_tag.find('h3', {'class': 'ipsType_subtitle'})
                    if subtitle is None:  # bad page, no info to found
                        continue

                    for link in subtitle.find_all('a'):
                        title = link.get('title')
                        if title is None or 'View file named' not in title:
                            continue
                        info['name'] = title[16:]
                        url = link.get('href')
                        text = link.getText()
                        if url is None or text == '': continue  # uploader url is author info
                        info['url'] = url
                        info_list.append(info)
            if next_page is None:
                break

            try:
                http_search = requests.post(next_page, cookies=http_req_login.cookies)
            except Exception:
                raise ConnectionException(url=next_page, error_code=http_search.status_code)

            if http_search.status_code != 200:
                raise ConnectionException(url=next_page, error_code=http_search.status_code)
            if self.debug_mode:
                self.dump_html(http_search)

        return info_list

    def extract_download_info(self, url: str, info: dict) -> dict:
        """
        Grab some info from download page
        :param url: download url to grab
        :param info: (optional) used when some info are available in upper page
        :return: dict or None if url is invalid
        """

        print('\tvpforum: extract info from %s' % url)  # TODO:del

        http_search = None
        try:
            http_search = requests.get(url)
        except Exception:
            raise ConnectionException('', url=url, error_code=http_search.status_code)

        if http_search.status_code != 200:
            raise ConnectionException(url=url, error_code=http_search.status_code)

        if self.debug_mode:
            self.dump_html(http_search)

        # TODO: add exception treatment for invalid url & no download info
        soup = BeautifulSoup(http_search.text, 'html.parser')
        items = soup.find('div', {'class': 'ipsPad ipsSideBlock'})
        if items is None:  # bad page, no info to found
            return None
        for li in items.find_all('li'):
            node = li.find('strong')
            if node is not None:
                if node.getText() == 'File size:':
                    info['size'] = extract_text('File size:', li.getText())
                elif node.getText() == 'Author(s):':
                    info['Author'] = extract_text('Author(s):', li.getText())
                elif node.getText() == 'IPDB Link:':
                    ipdb_node = li.find('a')
                    if ipdb_node is not None:  # <a href="#' onclick="JavaScript:newPopup('http://www.ipdb.org..
                        ipdb = ipdb_node.get('onclick')
                        if ipdb is not None:
                            info['ipdb'] = Site_ipdb_org.extract_ipdb_from_url(ipdb[21:-2])
                    else:  # <span>https://www.ipdb.org/machine.cgi?id=527</span>
                        ipdb_node = li.find('span')
                        if ipdb_node is not None:
                            info['ipdb'] = Site_ipdb_org.extract_ipdb_from_url(ipdb_node.get_text())

                elif node.getText() == 'Last Updated:':
                    text = extract_text('Last Updated:', li.getText())
                    info['Updated'] = str_2_struct_time(text)
        return info

    def __build_request(self, table_name: str) -> dict:
        """
        build json params request
        :param table_name:
        :return: params
        """
        params = {"search_app": [
            "downloads",
            "downloads"
        ], 'search_term': table_name, "andor_type": "and", "search_content": "both", "search_tags": "",
            "search_author": "",
            "search_date_start": "", "search_date_end": "", "search_app_filters[core][sortKey]": "date",
            "search_app_filters[core][sortDir]": "0", "search_app_filters[forums][noPreview]": "1",
            "search_app_filters[forums][pCount]": "", "search_app_filters[forums][pViews]": "",
            "search_app_filters[forums][sortKey]": "date", "search_app_filters[forums][sortDir]": "0",
            "search_app_filters[tracker][contentOnly]": "0", "search_app_filters[tracker][noPreview]": "1",
            "search_app_filters[tracker][sortKey]": "date", "search_app_filters[tracker][sortDir]": "0",
            "search_app_filters[downloads][field_1]": "", "search_app_filters[downloads][field_2]": "0",
            "search_app_filters[downloads][field_3]": "", "search_app_filters[downloads][field_4]": "",
            "search_app_filters[downloads][field_5]": "", "search_app_filters[downloads][field_6]": "",
            "search_app_filters[downloads][field_7]": "0", "search_app_filters[downloads][searchInKey]": "files",
            "search_app_filters[downloads][files][sortKey]": "date",
            "search_app_filters[downloads][files][sortDir]": "0",
            "search_app_filters[downloads][comments][sortKey]": "date",
            "search_app_filters[downloads][comments][sortDir]": "0", "search_app_filters[calendar][sortKey]": "date",
            "search_app_filters[calendar][sortDir]": "0", "search_app_filters[members][searchInKey]": "members",
            "search_app_filters[members][members][sortKey]": "date",
            "search_app_filters[members][members][sortDir]": "0",
            "search_app_filters[members][comments][sortKey]": "date",
            "search_app_filters[members][comments][sortDir]": "0", "search_app_filters[ccs][searchInKey]": "pages",
            "search_app_filters[ccs][pages][sortKey]": "date", "search_app_filters[ccs][pages][sortDir]": "0",
            "search_app_filters[gallery][searchInKey]": "images",
            "search_app_filters[gallery][images][sortKey]": "date", "search_app_filters[gallery][images][sortDir]": "0",
            "search_app_filters[gallery][comments][sortKey]": "date",
            "search_app_filters[gallery][comments][sortDir]": "0",
            "search_app_filters[gallery][albums][sortKey]": "date", "search_app_filters[gallery][albums][sortDir]": "0",
            "search_app_filters[tutorials][searchInKey]": "articles",
            "search_app_filters[tutorials][articles][sortKey]": "date",
            "search_app_filters[tutorials][articles][sortDir]": "0",
            "search_app_filters[tutorials][comments][sortKey]": "date",
            "search_app_filters[tutorials][comments][sortDir]": "0", "search_app_filters[blog][searchInKey]": "entries",
            "search_app_filters[blog][entries][sortKey]": "date", "search_app_filters[blog][entries][sortDir]": "0",
            "search_app_filters[blog][comments][sortKey]": "date", "search_app_filters[blog][comments][sortDir]": "0",
            "submit": "Search+Now", }
        return params
