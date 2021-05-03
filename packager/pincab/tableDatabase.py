import logging
import json
from io import StringIO
import csv
import os
from time import struct_time
from itertools import islice
import requests
import threading
import itertools
from multiprocessing.pool import ThreadPool
import multiprocessing.pool as mp
from packager.model.config import Config
from packager.tools.toolbox import *
from packager.pincab.site_cab import *
from packager.pincab.site_ipdb_org import Site_ipdb_org
from packager.pincab.site_vpinball_com import Site_vpinball_com
from packager.pincab.site_vpforum_org import Site_vpforum_com
from packager.pincab.site_vpuniverse_com import Site_vpuniverse_com
from packager.pincab.manufacturer import Manufacturer
from packager.pincab.statistics import Statistics

from packager.tools.exception import *


class TableDatabase:
    def __init__(self, logger, baseModel) -> None:
        self.__baseModel = baseModel
        self.__logger = logger
        self.__re_extract_year = re.compile('.*, (?P<year>\d+)')
        self.__re_extract_trade_name = re.compile('.*\[Trade Name: (?P<name>.+)\]')
        self.__manufacturer_db = Manufacturer(baseModel.config)
        self.__ipdb_site = Site_ipdb_org(logger)
        self.__vpinball = Site_vpinball_com(logger)
        self.__vpforum = Site_vpforum_com(logger)
        self.__vpuniverse = Site_vpuniverse_com(logger)
        self.__dbPath = baseModel.config.get('db_path')
        self.__manufacturer_dbPath = baseModel.config.get('manufacturer_path')

        self.__lock = threading.Lock()
        self.__data = {}
        self.__statistics = Statistics()
        self.load()

    @property
    def logger(self):
        return self.__logger

    @property
    def baseModel(self):
        return self.__baseModel

    @property
    def data(self):
        return self.__data

    @property
    def statistics(self):
        return self.__statistics

    @property
    def vpforum(self):
        return self.__vpforum

    @property
    def vpuniverse(self):
        return self.__vpuniverse

    @property
    def vpinball(self):
        return self.__vpinball

    def clear(self):
        if os.path.exists(self.__dbPath) and os.path.isfile(self.__dbPath):
            os.remove(self.__dbPath)
        self.__data = {}



    def save(self, database: dict = None) -> None:
        """
        Save table database as json file
        :param database to set database
        :return:
        """
        if database is not None:
            self.__data = database
        self.logger.debug("Saving Pincab Database")
        safe_save_json(self.__dbPath,self.__data)
        self.logger.debug("Save Done")


    def load(self) -> None:
        """
        load Pinball Machine database
        :return:
        """
        self.logger.info("Reading Pincab Database")
        self.__data=safe_load_json(self.__dbPath)
        self.__statistics.compute(self.__data)

        self.logger.info('\t%s' % self.__statistics)

    def get_all_pinball_machine_from_ipdb(self) -> None:
        """
        Get all pinball machine from ipdb.org
        :return:
        """
        try:
            pinball_machines = self.__ipdb_site.get_all_pinball_machine()
        except ConnectionException as e:
            self.logger.error(e)
            return

        for pinball_machine in pinball_machines:
            key,trade_name = self.__manufacturer_db.normalize_name(pinball_machine['Normalize Name'],
                                                                   pinball_machine['Manufacturer'],
                                                                   pinball_machine['Date Manufactured'])

            if key not in self.__data:
                self.__data[key] = self.__create_empty_pincab(pinball_machine)
                self.logger.info("Adding new pinball machine (%s) from https://www.ipdb.org" % key)
                self.__statistics.add('https://www.ipdb.org',Pinfile_type.PINBALL_MACHINE,'New')
            else:
                self.__statistics.add('https://www.ipdb.org', Pinfile_type.PINBALL_MACHINE, 'Total')

    def create_pinball_machines_db_from_scratch(self):
        """
        create a new pincab database form ipdb list
        :return:
        """
        self.clear()
        self.get_all_pinball_machine_from_ipdb()
        self.save()
        # range_size = 100
        # for i in range(0, len(self.__data), range_size):
        #     sub_data = dict(itertools.islice(self.__data.items(), i, i + range_size))
        #     self.check_all_ipdb(sub_data)
        #     for key, value in sub_data.items():
        #         self.__data[key] = value
        #     self.save()

    def add_pincab_file(self, file_type: Pinfile_type, file, max_table: int = -1):
        """
        add from vpinball and vpforum and add it to pincab_db

        :param max_table:
        :return:
        """
        try:
            self.statistics.add(file['url'], file_type, 'Total')

            pincab = self.search_url(file['url'])
            if pincab is not None:  # file already in database
                return

            info = self.extract_download_info(file['url'],
                                              {'ipdb': -1, 'version': '', 'size': '', 'Updated': '', 'Author': ''})
            if info is None:
                print("Can't found info, skip it")
                return

            file['Author'] = info['Author']
            file['version'] = info['version']
            file['size'] = info['size']
            file['Updated'] = info['Updated']

            if info['ipdb'] != -1:
                pincab = self.search(file_type, ipdb=info['ipdb'])
                if pincab is None:
                    self.logger.info('\tipdb not found for %s:%s' % (file['name'], file['url']))
            else:
                pincab = self.search(file_type, file['name'])
                if pincab is None:
                    self.logger.info("\tPincab %s not found in database" % file['name'])

            if pincab is not None:
                url_found = False
                for doc in pincab['Urls']:
                    if file['url'] == doc['url']:
                        url_found = True
                        break
                if not url_found:
                    self.logger.info('Merging (%s) into %s' % (file['name'], pincab['Table Name']))
                    pincab['Urls'].append(file)
                    self.statistics.add(file['url'], file_type, 'New')
            else:
                if file_type == Pinfile_type.VPX_TABLE:
                    name, manufacturer, year = self.extract_pincab_info_from_title(file['name'])
                elif file_type == Pinfile_type.ROM_FILE:
                    name, manufacturer, year = self.extract_pincab_info_from_rom_filename(file['name'])

                key_name, trade_name = self.__manufacturer_db.normalize_name(name, manufacturer, year)
                self.logger.info('Adding Pincab (%s/%s) ' % (key_name, file['url']))
                if year is None:
                    year == ''
                pincab = self.__create_empty_pincab({'Name': name, 'Manufacturer': trade_name, 'Date Manufactured': year})
                pincab['Urls'].append(file)
                self.data[key_name] = pincab
                self.statistics.add(file['url'], file_type, 'New')

        except ConnectionException as e:
            self.statistics.add(file['url'], file_type, 'Error')
            print('Error %s' % e)
            return

    def update_ipdb_info(self, pincab: dict) -> None:
        try:
            if pincab['IPDB Check']:  # ipdb check already done
                return
            if pincab['IPDB Number'] != -1:
                self.logger.info('\tGet info for pincab "%s" with ipdb "%d"' % (pincab['Table Name'], pincab['IPDB Number']))
                self.__ipdb_site.search_pincab_info(pincab['IPDB Number'], pincab)
            else:
                self.logger.info('\tNo ipdb, looking for [%s/%s/%s]' % (pincab['Table Name'], pincab['Year'], pincab['Manufacturer']))
                ipdb = self.__ipdb_site.search_pincab_ipdb(pincab['Table Name'], year=pincab['Year'],
                                                           manufacturer=pincab['Manufacturer'], regex=False)
                pincab['IPDB Number'] = ipdb
                if ipdb == -1:
                    ipdb = self.__ipdb_site.search_pincab_ipdb(pincab['Table Name'], year=pincab['Year'],
                                                               manufacturer=pincab['Manufacturer'], regex=True)
                    self.logger.warning('\t\tSkip "%s/%s/%s", unknwn ipdb' % (pincab['Table Name'], pincab['Year'], pincab['Manufacturer']))
                    return
                else:
                    self.logger.info('\tfound ipdb %d for pincab [%s/%s/%s] ' % (ipdb, pincab['Table Name'], pincab['Year'], pincab['Manufacturer']))
                    self.__ipdb_site.search_pincab_info(pincab['IPDB Number'], pincab)
        except ConnectionException as e:
            self.__statistics.add('https://www.ipdb.org', Pinfile_type.PINBALL_MACHINE, 'Error')
        return

    def update_pinball_machine_ipdb(self, pool_size: int = 10):
        """
        update pinball machine database
        :return:
        """
        self.logger.info('\tStart: Looking for new pinball machine from ipdb.org')
        self.get_all_pinball_machine_from_ipdb()
        self.logger.info('\t%s' % self.__statistics)
        self.save()

        range_size = 50
        for i in range(0, len(self.__data), range_size):
            sub_data = dict(itertools.islice(self.__data.items(), i,i+range_size))

            pool = ThreadPool(pool_size)
            [pool.apply_async(self.update_ipdb_info, args=(pinball_machine,)) for key, pinball_machine in sub_data.items()]
            pool.close()
            pool.join()
            self.save()
        self.logger.info('\tEnd: Looking for new pinball machine from ipdb.org')

    def update_all_pincab_file_from_list(self, file_type: Pinfile_type, pincab_files: list, pool_size: int = 10):
        """
        load all table form vpinball and vpforum and add it to pincab_db

        :param files: vpx list
        :param pool_size: number of threads
        :return: database
        """
        range_size = 50

        for i in range(0, len(pincab_files), range_size):
            pool = ThreadPool(pool_size)
            sub_list = pincab_files[i:i + range_size]
            [pool.apply_async(self.add_pincab_file, args=(file_type, file)) for file in pincab_files[i:i + range_size]]
            pool.close()
            pool.join()
            self.save()

    def extract_download_info(self, url: str, info: dict) -> dict:
        if 'https://vpinball.com' in url:
            return self.__vpinball.extract_download_info(url, info)
        elif 'https://www.vpforums.org' in url:
            return self.__vpforum.extract_download_info(url, info)
        elif 'https://vpuniverse.com' in url:
            return self.__vpuniverse.extract_download_info(url, info)
        print("Unknown site (%s)" % url)
        return None

    def __create_empty_pincab(self, pinball: dict) -> dict:
        """
        Create an empty pincab database
        :param table_name
        :return: empty pincab structure
        """
        pincab = dict()
        pincab['Table Name'] = pinball['Name']
        pincab['Manufacturer'] = pinball['Manufacturer']
        pincab['Year'] = pinball['Date Manufactured']
        pincab['Theme'] = ''
        pincab['Player(s)'] = ''
        pincab['IPDB Number'] = -1
        pincab['IPDB Check'] = False
        pincab['Description(s)'] = ''
        pincab['Type'] = ''
        pincab['Update'] = ''
        pincab['Fun Rating'] = ''
        pincab['Description(s)'] = ''
        pincab['Notes'] = ''
        pincab['Design by'] = ''
        pincab['Art by'] = ''
        pincab['Urls'] = []

        return pincab



    def reload(self) -> None:
        """
        clear database reload all database from web
        :return:
        """
        self.clear()
        self.__data = self.download()
        self.save()

    def search_url(self, url: str) -> dict:
        """
        search an url in database
        :param url: 
        :return: 
        """
        self.__lock.acquire()
        for key, pincab in self.__data.items():
            for file in pincab['Urls']:
                if url == file['url']:
                    self.__lock.release()
                    return pincab
        self.__lock.release()
        return None

    def search(self, file_type: Pinfile_type, name: str = None, ipdb: str = None) -> dict:
        """
        search table from db (return empty vector if not found)
        :param name: table to find by name (default)
        :param ipdb: find with ipdb
        :return: list of table fields
        """

        if self.__data is None:
            return None

        manufacturer = None
        year = None
        if ipdb is None:
            if file_type == Pinfile_type.VPX_TABLE:
                name, manufacturer, year = self.extract_pincab_info_from_title(name)
            elif file_type == Pinfile_type.ROM_FILE:
                name, manufacturer, year = self.extract_pincab_info_from_rom_filename(name)

            # if name is not None and manufacturer is not None and year is not None:
            #     name = (name + ' ' + '(' + manufacturer + ' ' + str(year) + ')').upper()
            # else:
            #     name = name.upper()

            key_name, trade_name=self.__manufacturer_db.normalize_name(name,manufacturer,year)
            if key_name in self.__data:
                return self.__data[key_name]

        list = []

        self.__lock.acquire()
        for key, pincab in self.__data.items():
            if ipdb is not None:
                if pincab['IPDB Number'] == ipdb:
                    list.append(pincab)
                    break
            # if name is not None and name in key:
            if name is not None and key.startswith(name):
                list.append(pincab)
        self.__lock.release()

        if len(list) == 0:
            return None

        if len(list) == 1:
            return list[0]

        for element in list:
            if manufacturer in element['Manufacturer']:
                return element
        return list[0]

    def extract_pincab_info_from_title(self, pincab_title: str) -> (str, str, int):
        return Site_Cab.extract_pincab_info_from_title(pincab_title, self.__manufacturer_db)

    def extract_pincab_info_from_rom_filename(self, rom_filename: str) -> (str, str, int):
        return Site_Cab.extract_pincab_info_from_rom_filename(rom_filename)

    def search_pincab_urls_filter(self, pincab_name: str, urls: list) -> list:
        return Site_Cab.search_pincab_urls_filter(pincab_name, urls)
