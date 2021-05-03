import json
from tkinter import messagebox
from packager.model.package import *
from packager.pincab.site_cab import *
from packager.tools.observer import Observable
from packager.tools.toolbox import *


class Search_Model(Observable):
    def __init__(self, baseModel):
        super().__init__()
        self.__baseModel = baseModel
        self.__pinball_machine = []
        self.__selected_pinball_machine = []

    @property
    def baseModel(self):
        return self.__baseModel

    @property
    def logger(self):
        return self.__baseModel.logger

    @property
    def pinball_machine(self):
        return self.__pinball_machine

    def update(self, contains:str='', only_with_vpx:bool=True) -> None: # TODO: better with functionnal style
        """
        Select all pinball machine for search view
        :param contains: start with 'string'
        :param only_with_vpx: True to view only Pinball Machine with VPX files
        :return:
        """
        print("update (%s)" % contains)
        self.__pincab = []
        for key, pincab in self.baseModel.database.data.items():
            selector: bool = True

            if contains != '':
                selector=selector and key.startswith(contains)
            if only_with_vpx:
                selector=selector and len(pincab['Urls'])>=1
            if selector:
                self.__pincab.append(key)
        self.notify_all(self, events=['<<UPDATE TABLES>>'],
                        pinball_machines=self.__pincab,
                        nb_result=len(self.__pincab),
                        total=len(self.baseModel.database.data))  # update listeners

    def select_pinball_machine(self, pinball_machine:dict) -> None:
        pinball_machine_data=self.baseModel.database.data[pinball_machine]
        self.notify_all(self, events=['<<PINBALL SELECTED>>'], pinball_machine=pinball_machine_data)  # update listeners

    def unselect_pinball_machine(self):
        self.__selected_pinball_machine = []
        self.notify_all(self, events=['<<PINBALL UNSELECTED>>'])  # update listeners

    def update_db(self):
        pass

    def update_database(self) -> None:
        self.notify_all(self, events=['<<DISABLE_ALL>>', '<<BEGIN_ACTION>>'])  # update listeners
        extract_thread = AsynRun(self.update_database_begin, self.update_database_end)
        extract_thread.start()

    def update_database_begin(self, context=None) -> bool:
        self.logger.info('Update Pinball Database')
        # try:
        #     self.baseModel.database.update_pinball_machine_ipdb()
        # except Exception as e:
        #     messagebox.showerror('Update Pinball Database Error %s', str(e))
        #     return False

        self.logger.info('Update vpforum vpx')
        try:
            self.baseModel.database.update_all_pincab_file_from_list(Pinfile_type.VPX_TABLE,
                                                                     self.baseModel.database.vpforum.search_all_table(Pinfile_type.VPX_TABLE))
            self.baseModel.database.update_all_pincab_file_from_list(Pinfile_type.VPX_TABLE,
                                                                     self.baseModel.database.vpuniverse.search_all_table(Pinfile_type.VPX_TABLE))
            self.logger.info('%s' % self.baseModel.database.statistics['vpforum'])
        except Exception as e:
            messagebox.showerror('Update Pinball Database Error %s', str(e))
            return False

        self.logger.info('Update vpuniverse vpx')
        try:
            self.baseModel.database.update_all_pincab_file_from_list(Pinfile_type.VPX_TABLE,
                                                                     self.baseModel.database.vpuniverse.search_all_table(Pinfile_type.VPX_TABLE))
            self.logger.info('%s' % self.baseModel.database.statistics['vpuniverse'])
        except Exception as e:
            messagebox.showerror('Update Pinball Database Error %s', str(e))
            return False


        return True

    def update_database_end(self, context=None, success=True):
        self.logger.info("--[Done]------------------")
        self.notify_all(self, events=['<<END_ACTION>>', '<<ENABLE_ALL>>'])
