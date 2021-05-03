from packager.pincab.site_cab import Pinfile_type

class Statistics:
    def __init__(self) -> None:
        self.__stats = None
        self.clean()

    def clean(self):
        self.__stats = {'pinball machine': 0,
                        'ipdb'   : { 'Total':0, 'New':0, 'Error' : 0},
                        'vpforum': {'ROMs': {'Total': 0, 'New': 0, 'Error': 0},
                                    'VPX': {'Total': 0, 'New': 0, 'Error': 0}},
                        'vpinball': {'ROMs': {'Total': 0, 'New': 0, 'Error': 0},
                                     'VPX': {'Total': 0, 'New': 0, 'Error': 0}},
                        'vpuniverse': {'ROMs': {'Total': 0, 'New': 0, 'Error': 0},
                                       'VPX': {'Total': 0, 'New': 0, 'Error': 0}}
                        }

    def __str__(self):
        return '%s' % self.__stats

    def compute(self, database:dict):
        ipdb_count = 0

        self.clean()
        self.__stats['pinball machine']=len(database)
        for key, pincab in database.items():
            if pincab['IPDB Number'] != '-1':
                ipdb_count = ipdb_count + 1
            for file in pincab['Urls']:
                self.add(file['url'], Pinfile_type.value(file['type']), 'Total')

    def add(self, url: str, pin_type: Pinfile_type, what: str):
        stat = None

        if 'https://www.vpforums.org/' in url:
            stat = self.__stats['vpforum']
        elif 'https://vpinball.com/' in url:
            stat = self.__stats['vpinball']
        elif 'https://vpuniverse.com/' in url:
            stat = self.__stats['vpuniverse']
        elif 'https://www.ipdb.org' in url:
            stat = self.__stats['ipdb']
        else:
            return

        if pin_type == Pinfile_type.ROM_FILE:
            stat = stat['ROMs']
        elif pin_type == Pinfile_type.VPX_TABLE:
            stat = stat['VPX']
        elif pin_type == Pinfile_type.PINBALL_MACHINE:
            pass

        stat[what] = stat[what] + 1