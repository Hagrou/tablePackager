import json
from tkinter import messagebox
#from packager.model.manifest import Manifest
from packager.model.package import *

from packager.tools.observer import Observable
from packager.tools.toolbox import *

class InstalledTablesModel(Observable):
    def __init__(self, baseModel):
        super().__init__()
        self.__baseModel=baseModel
        self.__tables=[]
        self.__selectedTable = []

    @property
    def baseModel(self):
        return self.__baseModel

    @property
    def logger(self):
        return self.__baseModel.logger

    @property
    def tables(self):
        return self.__tables

    def update(self):
        # read Visual Pinball Tables
        self.__tables = []
        for vpx_file in Path(self.baseModel.visual_pinball_path + "/tables").glob('**/*.vpx'):
            self.__tables.append({'type':'vpx','name':vpx_file.stem})
        self.__tables.sort(key=lambda table: table['name'].upper())
        self.notify_all(self,events=['<<UPDATE TABLES>>'],tables=self.__tables) # update listeners

        
    def selectTable(self, selection):
        self.__selectedTable=[]
        for index in selection:
            self.__selectedTable.append(self.__tables[index])
        self.notify_all(self, events=['<<TABLE SELECTED>>'],tables=self.__selectedTable)  # update listeners

    def unSelectTable(self):
        self.__selectedTable = []
        self.notify_all(self, events=['<<TABLE UNSELECTED>>'])  # update listeners

    def extract_tables(self, tableChoice):
        self.notify_all(self, events=['<<DISABLE_ALL>>','<<BEGIN_ACTION>>'], tables=self.__selectedTable)  # update listeners
        extractThread = AsynRun(self.extract_tables_begin, self.extract_tables_end,context=tableChoice)
        extractThread.start()

    def extract_tables_begin(self,context=None):
        if not self.__selectedTable: # empty selection
            raise ValueError('No selected table')

        self.baseModel.logger.info("Begin Extraction")
        for table in self.__selectedTable:
            if Path(self.baseModel.package_path + '/' + table['name'] + self.baseModel.package_extension).exists():
                result = messagebox.askokcancel("Extraction",
                                                "Table package already extracted, would you like to overwrite it ?")
                if result:
                    os.remove(self.baseModel.package_path + '/' + table['name'] + self.baseModel.package_extension)
                else:
                    self.logger.info("Extraction canceled")
                    continue
            clean_dir(self.baseModel.tmp_path)
            self.logger.info("--[Working on '%s']------------------" % (table['name']))
            package=Package(self.baseModel, table['name'])
            package.new(self.baseModel.tmp_path)

            if context['visual_pinball'].get():
                self.baseModel.visualPinball.extract(package)
                self.baseModel.vpinMame.extract(package)
                self.baseModel.ultraDMD.extract(table['name'],package)
            if context['pinballX'].get():
                self.baseModel.pinballX.extract(table['name'], package)
            if context['futurPinball'].get():
                self.logger.warning("extract from futurPinball is not yet implemented")
            if context['pinupSystem'].get():
                self.logger.warning("extract from pinupSystem is not yet implemented")

            package.save()
            package.pack() # zip package
            shutil.move(self.baseModel.tmp_path + '/' + table['name'] + self.baseModel.package_extension,
                        self.baseModel.package_path)

        clean_dir(self.baseModel.tmp_path)

    def extract_tables_end(self,context=None):
        self.logger.info("--[Done]------------------")
        self.notify_all(self, events=['<<END_ACTION>>','<<ENABLE_ALL>>'], tables=self.__selectedTable)  # update listeners
        self.baseModel.packagedTablesModel.update()

    def delete_Tables(self, viewer):
        self.notify_all(self, events=['<<DISABLE_ALL>>', '<<BEGIN_ACTION>>'])  # update listeners
        tables=', '.join(p['name'] for p in self.__selectedTable)
        delConfirmed=messagebox.askokcancel("Delete Table(s)", "Are you sure you want to delete table(s) '%s'" % (tables),
                               parent=viewer)
        if not delConfirmed:
            self.notify_all(self, events=['<<END_ACTION>>', '<<ENABLE_ALL>>'])  # update listeners
            return

        deleteTableThread = AsynRun(self.delete_tables_begin, self.delete_tables_end)
        deleteTableThread.start()


    def delete_tables_begin(self,context=None):
        if not self.__selectedTable: # empty selection
            raise ValueError('No selected table')

        self.logger.info("--[Delete Table(s)]------------------")
        for table in self.__selectedTable:
            self.logger.info("--[Working on '%s']------------------" % (table['name']))

            ultraDMD=''
            romName=''
            isPackage=False
            manifest=Manifest(table['name'])
            try:
                manifest.open(self.baseModel.installed_path, installed=True)
                isPackage=True
                if manifest.exists_field('visual pinball/info/romName'):
                    romName=manifest.get_field('visual pinball/info/romName')
                if manifest.exists_field('visual pinball/info/ultraDMD'):
                    ultraDMD=manifest.get_field('visual pinball/info/ultraDMD')
            except:
                romName=self.baseModel.visualPinball.getRomName(table['name']) # use package.manifest if exists

            self.baseModel.visualPinball.delete(table['name'])

            self.baseModel.vpinMame.delete(table['name'],romName)
            if isPackage:
                if ultraDMD!='':
                    self.baseModel.ultraDMD.delete(table['name'],dirName=ultraDMD)  # use package.manifest if exists
            else:
                self.baseModel.ultraDMD.delete(table['name']) # use package.manifest if exists
            self.baseModel.pinballX.delete(table['name'])
            self.baseModel.pinupSystem.delete(table['name'],'visual pinball')
            self.logger.warning("delete on futurPinball is not yet implemented")


    def delete_tables_end(self,context=None):
        self.logger.info("--[Done]------------------")
        self.update()
        self.notify_all(self, events=['<<END_ACTION>>', '<<ENABLE_ALL>>'])  # update listeners

