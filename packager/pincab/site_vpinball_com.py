import requests

import re
import os

import webbrowser
import sys
import traceback
from bs4 import BeautifulSoup
from packager.tools.toolbox import *
from packager.pincab.site_cab import *
from packager.pincab.site_ipdb_org import Site_ipdb_org
from packager.tools.exception import *
import time

re_pages_found = re.compile('Showing \d+-\d+ of (?P<number>\d+)')


class Site_vpinball_com(Site_Cab):
    def __init__(self,logger):
        super().__init__()
        self.__connect_url = 'https://www.vpforums.org/index.php?app=core&module=global&section=login'
        self.__search_all_VPX_table_url = 'https://vpinball.com/VPBdownloads/categories/vpx-tables/'
        self.__search_all_ROMs_url = 'https://vpinball.com/VPBdownloads/categories/pinball-machine-roms/'
        self.__search_file_url = 'https://vpinball.com/VPBdownloads/?CMDsearch=%s'
        # self.__connect_url = 'https://www.vpforums.org/index.php?app=core&module=global&section=login&do=process'
        self.__connected = False
        self.__logger = logger

    def is_connected(self):
        return self.__cookies is not None

    # def connect(self, username: str, password: str) -> bool:
    #     """
    #     connect to vpforum.org
    #     :param username:
    #     :param password:
    #     :return:
    #     """
    #     http_req_login = requests.post(self.__connect_url)
    #     html_page = http_req_login.text
    #     referer = extract_value(html_page, '<input type="hidden" name="referer"', around_size=+200,
    #                             regexp='.*name="referer" value="(.*)".*')
    #     action_url = extract_value(html_page, 'method="post" id=\'login\'', around_size=-200,
    #                                regexp='.*action="(.*)"')
    #     auth_key = extract_value(html_page, 'method="post" id=\'login\'', around_size=+150,
    #                              regexp='.*name=\'auth_key\' value=\'([0-9a-f]{32})\'.*')
    #     params = {'referer': referer, 'auth_key': auth_key, 'ips_username': username, 'ips_password': password}
    #     http_connect = requests.post(action_url, params, cookies=http_req_login.cookies)
    #
    #     if http_connect.status_code != 200:
    #         return False
    #
    #     """
    #         <noscript>
    # 				<div class='message error'>
    # 					<strong>Javascript Disabled Detected</strong>
    # 					<p>You currently have javascript disabled. Several functions may not work. Please re-enable javascript to access full functionality.</p>
    # 				</div>
    # 				<br />
    # 			</noscript>\
    #     """
    #     self.__cookies = http_connect.cookies
    #     show_html(http_connect)
    #     return True

    # try to download a file...
    # def get_file(self, url_file):
    #     # step1: open download page ang get md5_hash
    #     print("Open page: " + url_file)
    #     http_req_file_info = requests.get(url_file, cookies=self.__cookies)
    #     if http_req_file_info.status_code != 200:
    #         print("Get Error status code =%d\n" % http_req_file_info.status_code)
    #         return
    #
    #     # todo: extract file information
    #     # Submitted: File Author(s) # Last Updated
    #
    #     # md5_hash = get_md5_hash(http_request1.text)
    #     md5_hash = extract_value(http_req_file_info.text, 'do=confirm_download', around_size=+100,
    #                              regexp='.*;hash=([0-9a-f]{32}).*')
    #
    #     # step2: Click on download button
    #     download_url = 'https://www.vpforums.org/index.php?app=downloads&module=display&section=download&do=confirm_download&hash=' + md5_hash
    #     print("Click on Download: [%s] " % download_url)
    #     http_req_download = requests.post(download_url,
    #                                       cookies=self.__cookies)
    #     Site_Cab.show_html(http_req_download) # TODO:del
    #     if http_req_download.status_code != 200:
    #         print("Get Error status code =%d\n" % http_req_download.status_code)
    #         return
    #     html_page = http_req_download.text
    #
    #     # md5_hash = get_md5_hash(http_req_file_info.text)
    #     download_url = 'https://www.vpforums.org/index.php?app=downloads&module=display&section=download&do=confirm_download&hash=' + md5_hash + '&agreed=1'
    #     # step3: download file
    #     print("Download File %s " % download_url)

    # def search_all_VPX_table(self, max_table=-1) -> list:
    #     """
    #     search all VPX table in vpinball site
    #     :param max_table: max table to found (-1: no limit)
    #     :return: list of info with the better url or None for error
    #     """
    #     http_search = requests.get(self.__search_all_VPX_table)
    #     if http_search.status_code != 200:
    #         raise Exception('%s error (%d) ' % (self.__search_all_VPX_table, http_search.status_code))
    #
    #     info_list = []
    #     while True:
    #         next_page = None
    #         self.dump_html(http_search)
    #         soup = BeautifulSoup(http_search.text, 'html.parser')
    #
    #         showing_node = soup.find('div', {'class': 'searchTitle'})
    #         if showing_node is not None:
    #             pages_found_str = showing_node.getText()
    #             grp_nb_pages_found = re_pages_found.search(pages_found_str)
    #             if grp_nb_pages_found is not None:
    #                 nb_pages_found = int(grp_nb_pages_found.group('number'))
    #
    #         for pages_url in soup.find_all('a', {'class': 'next'}):
    #             if pages_url is not None:
    #                 next_page = pages_url.get('href')
    #
    #         for items in soup.find_all('div', {"class": "cmdm-archive-items CMDM-list-view"}):
    #             for link in items.find_all('a'):
    #                 url = link.get('href')
    #                 if url is None or 'uploader' in url or 'sort=post_modified' in url:
    #                     continue  # uploader url is author info, sort=post_modified for next page
    #                 file_name = link.getText()
    #                 info = {'type': 'VPX Tables', 'url': url, 'name': file_name.strip('\n\t')}
    #                 info_list.append(info)
    #                 if max_table > 0 and max_table == len(info_list):
    #                     next_page = None
    #                     break
    #
    #         if next_page is None:
    #             break
    #         http_search = requests.post(next_page)
    #
    #         if http_search.status_code != 200:
    #             raise Exception(self.__search_url + ' error (%d) ' % http_search.status_code)
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
            search_url = self.__search_all_VPX_table_url
        elif Pinfile_type.ROM_FILE == file_type:
            type_name = file_type.name
            search_url = self.__search_all_ROMs_rul

        """
          search all VPX table in vpinball site
          :param max_table: max table to found (-1: no limit)
          :return: list of info with the better url or None for error
          """
        http_search=None
        try:
            http_search = requests.get(search_url)
        except Exception:
            raise ConnectionException('', url=search_url, error_code=http_search.status_code)

        if http_search.status_code != 200:
            raise ConnectionException('', url=search_url, error_code=http_search.status_code)

        info_list = []
        while True:
            next_page = None

            if self.debug_mode:
                self.dump_html(http_search)

            soup = BeautifulSoup(http_search.text, 'html.parser')

            showing_node = soup.find('div', {'class': 'searchTitle'})
            if showing_node is not None:
                pages_found_str = showing_node.getText()
                grp_nb_pages_found = re_pages_found.search(pages_found_str)
                if grp_nb_pages_found is not None:
                    nb_pages_found = int(grp_nb_pages_found.group('number'))

            for pages_url in soup.find_all('a', {'class': 'next'}):
                if pages_url is not None:
                    next_page = pages_url.get('href')

            for items in soup.find_all('div', {"class": "cmdm-archive-items CMDM-list-view"}):
                for link in items.find_all('a'):
                    url = link.get('href')
                    if url is None or 'uploader' in url or 'sort=post_modified' in url:
                        continue  # uploader url is author info, sort=post_modified for next page
                    file_name = link.getText()
                    info = {'type': type_name, 'url': url, 'name': file_name.strip('\n\t')}
                    info_list.append(info)
                    if max_table > 0 and max_table == len(info_list):
                        next_page = None
                        break

            if next_page is None:
                break
            try:
                http_search = requests.post(next_page)
            except Exception as e:
                raise ConnectionException('', url=http_search, error_code=http_search.status_code)
            if http_search.status_code != 200:
                raise ConnectionException('', url=http_search, error_code=http_search.status_code)

        return info_list

    def search_pincab_urls(self, pincab_name: str, max_result: int = 120) -> list:
        """
        search all urls for a table
        :param pincab_name: the table to find
        :param max_result to take into account
        :return: list of info with the better url or None for error
        """

        http_search=None
        name, year = Site_Cab.extract_pincab_info_from_title(pincab_name)
        try:
            http_search = requests.get(self.__search_file_url % name)
        except Exception:
            raise ConnectionException('', url=self.__search_file_url % name, error_code=http_search.status_code)

        if http_search.status_code != 200:
            raise ConnectionException('', url=self.__search_file_url % name, error_code=http_search.status_code)


        info_list = []
        while True:
            next_page = None
            self.dump_html(http_search)
            soup = BeautifulSoup(http_search.text, 'html.parser')

            showing_node = soup.find('div', {'class': 'searchTitle'})
            if showing_node is not None:
                pages_found_str = showing_node.getText()
                grp_nb_pages_found = re_pages_found.search(pages_found_str)
                if grp_nb_pages_found is not None:
                    nb_pages_found = int(grp_nb_pages_found.group('number'))

            for pages_url in soup.find_all('a', {'class': 'next'}):
                if pages_url is not None:
                    next_page = pages_url.get('href')

            for items in soup.find_all('div', {"class": "cmdm-archive-items CMDM-list-view"}):
                for link in items.find_all('a'):
                    url = link.get('href')
                    if url is None or 'uploader' in url or 'sort=post_modified' in url:
                        continue  # uploader url is author info, sort=post_modified for next page
                    file_name = link.getText()
                    info = {'type': None, 'url': url, 'name': file_name.strip('\n\t')}
                    info_list.append(info)
                    if max_result == len(info_list):
                        next_page = None
                        break

            if next_page is None:
                break
            try:
                http_search = requests.post(next_page)
            except Exception:
                raise ConnectionException('', url=next_page, error_code=http_search.status_code)

            if http_search.status_code != 200:
                raise ConnectionException('', url=next_page, error_code=http_search.status_code)

        return info_list

    def extract_download_info(self, url: str, info: dict) -> dict:
        """
        Grab some info from download page
        :param url: download url to grab
        :param info: (optional) used when some info are available in upper page
        :return: dict or None if url is invalid
        """
        """
        Grab some info from download page
        :param url: download url to grab
        :return: dict or None if url is invalid
        """

        print('\tvpinball: extract info from %s' % url)  # TODO:del
        http_search=None
        try:
            http_search = requests.get(url)
        except Exception:
            raise ConnectionException('', url=url, error_code=http_search.status_code)

        if http_search.status_code != 200:
            raise ConnectionException('', url=url, error_code=http_search.status_code)

        if self.debug_mode:
            self.dump_html(http_search)

        # TODO: add exception treatment for invalid url & no download info
        soup = BeautifulSoup(http_search.text, 'html.parser')
        items = soup.find('div', {'class': 'cmdm-download-details'})
        if items is None:  # bad page, no info to found
            return None
        info['Author'] = items.find('a', {'class': 'CMDM-author-link'}).getText()
        info['size'] = ''

        for li in items.find_all('li'):
            node = li.find('strong')
            if node is not None:
                if node.getText() == 'File size:':
                    info['size'] = li.find('span').getText()
                elif node.getText() == 'Version:':
                    info['version'] = li.find('span').getText()
                elif node.getText() == 'Updated:':
                    info['Updated'] = str_2_struct_time(li.find('span').getText())
                elif node.getText() == 'Categories:':
                    info['type'] = []
                    for category in li.find_all('a'):
                        info['type'].append(category.getText())
                elif node.getText() == 'IPDB link::':
                    info['ipdb'] = Site_ipdb_org.extract_ipdb_from_url(li.find('span').getText())
        return info
