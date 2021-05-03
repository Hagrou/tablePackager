import json
import os
from packager.model.config import Config
from packager.tools.toolbox import *

class Manufacturer:
    def __init__(self, config: Config) -> None:
        self.__manufacturer_path = config.get('manufacturer_path')
        self.__manufacturer = []

        if os.path.exists(self.__manufacturer_path) and os.path.isfile(self.__manufacturer_path):
            with open(self.__manufacturer_path, 'r') as file:
                self.__manufacturer = json.load(file)

    def get_trade_name(self, manufacturer: str) -> str:
        """
        get trade_name of a manufacturer
        :param manufacturer
        :return: trade_name
        """

        if manufacturer is None or manufacturer == '':
            return ''

        for db_manufacturer in self.__manufacturer:
            if manufacturer in db_manufacturer['Manufacturer']:
                return db_manufacturer['Trade Name']

        print('Warning, unkwnon manufacturer (%s)' % manufacturer)
        return ''

    def normalize_name(self, name, manufacturer, date) -> (str, str):
        trade_name = self.get_trade_name(manufacturer)

        if trade_name == '':
            return name.upper(),''

        if date is None or date == '':
            return (name + ' (' + trade_name + ')').upper(), trade_name
        year = struct_time_2_datetime(str_2_struct_time(date)).strftime('%Y')
        return (name + ' (' + trade_name + ' ' + year + ')').upper(), trade_name

