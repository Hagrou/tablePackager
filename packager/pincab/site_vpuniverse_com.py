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


class Site_vpuniverse_com(Site_Cab):
    def __init__(self, logger, debug_mode=False):
        super().__init__(debug_mode)
        self.__connect_url = 'https://www.vpforums.org/index.php?app=core&module=global&section=login'
        self.__search_all_VPX_table_url = 'https://vpuniverse.com/forums/files/category/82-vpx-pinball-recreations/'
        self.__search_all_ROMs_url = 'https://vpinball.com/VPBdownloads/categories/pinball-machine-roms/'
        self.__search_file_url = 'https://vpinball.com/VPBdownloads/?CMDsearch=%s'
        # self.__connect_url = 'https://www.vpforums.org/index.php?app=core&module=global&section=login&do=process'
        self.__connected = False
        self.__logger = logger

    def search_all_table(self, file_type: Pinfile_type, max_table=-1) -> list:
        """
        search all VPX table in vpuniverse
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

        http_search=None
        try:
            http_search = requests.get(search_url)
        except Exception:
            raise ConnectionException('', url=search_url, error_code=http_search.status_code)

        if http_search.status_code != 200:
            raise ConnectionException('', url=search_url, error_code=http_search.status_code)

        info_list = []
        page_number = 0
        while True:
            next_page = None
            page_number = page_number + 1
            if self.debug_mode:
                self.dump_html(http_search)

            soup = BeautifulSoup(http_search.text, 'html.parser')

            showing_node = soup.find('div', {'data-role': 'tablePagination'})

            if showing_node is not None:
                next_node = showing_node.find('a', {'rel': 'next'})
                if next_node is not None:
                    next_page = next_node.get('href')

                last_node = showing_node.find('a', {'rel': 'last'})
                if last_node is not None:
                    nb_pages_found = int(last_node.get('data-page'))

            """	
					<span class="ipsType_break ipsContained"><a href="https://vpuniverse.com/forums/files/file/5068-tron-legacy-le-hanibals-4k-edition/" title="View the file Tron Legacy LE Hanibals 4k Edition ">Tron Legacy LE Hanibals 4k Edition</a></span>
				
            """
            for items in soup.find_all('div', {'class': 'ipsDataItem_main'}):
                span_node=items.find('span', {'class':'ipsType_break ipsContained'})
                if span_node is None:
                    continue
                link = span_node.find('a')
                if link is None:
                    continue

                url = link.get('href')
                #if url is None or 'uploader' in url or 'sort=post_modified' in url:
                #    continue  # uploader url is author info, sort=post_modified for next page
                file_name = link.getText()
                info = {'type': type_name, 'url': url, 'name': file_name.strip('\n\t')}
                info_list.append(info)
                if max_table > 0 and max_table == len(info_list):
                    next_page = None
                    break

            print("Page processing %d (%d files) Dne" % (page_number, len(info_list))) # TODO: log it
            if next_page is None:
                break
            if page_number == nb_pages_found:
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

        print('\tvpuniverse: extract info from %s' % url)  # TODO:del
        http_search=None
        try:
            http_search = requests.get(url)
        except Exception:
            raise ConnectionException('', url=url, error_code=http_search.status_code)

        if http_search.status_code != 200:
            raise ConnectionException('', url=url, error_code=http_search.status_code)

        if self.debug_mode:
            self.dump_html(http_search)

        
        soup = BeautifulSoup(http_search.text, 'html.parser')
        items = soup.find('aside', {'class': 'ipsColumn ipsColumn_wide'})
        if items is None:  # bad page, no info to found
            return None

        info['size'] = ''

        """
        <li class="ipsDataItem">
								<span class="ipsDataItem_generic ipsDataItem_size3"><strong>IPDB Link</strong></span>
								<div class="ipsDataItem_generic ipsType_break cFileInfoData">
									3782
								</div>
		</li>
		"""
        for li in items.find_all('li', {'class': 'ipsDataItem'}):
            node = li.find('strong')
            if node is not None:
                if node.getText() == 'File Size':
                    value = li.find('span', {'class': 'ipsDataItem_generic cFileInfoData'})
                    info['size'] = value.getText()
                elif node.getText() == 'Created by':
                    info['Author'] = extract_text('',li.find('div').getText())
                #elif node.getText() == 'Version':
                #    info['version'] = li.find('span').getText()
                elif node.getText() == 'Submitted':
                    info['Updated'] = str_2_struct_time(li.find('time').get('datetime'))
                #elif node.getText() == 'Categories:':
                #    info['type'] = []
                #    for category in li.find_all('a'):
                #        info['type'].append(category.getText())

                elif node.getText() == 'IPDB Link':
                    ipdb_node = li.find('a', {'class':'vglnk'})
                    if ipdb_node is not None:  # <a href="#' onclick="JavaScript:newPopup('http://www.ipdb.org..
                        ipdb_url = ipdb_node.get('href')
                        if ipdb_url is not None:
                            info['ipdb'] = Site_ipdb_org.extract_ipdb_from_url(ipdb_url[21:-2])
                    else:
                        value=extract_text('',li.find('div').getText())
                        if 'http' in value:
                            info['ipdb']=Site_ipdb_org.extract_ipdb_from_url(value)
                        else:
                            info['ipdb'] = int(value)
        return info
