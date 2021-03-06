import json
from tkinter import messagebox
from packager.model.package import *

from packager.tools.observer import Observable
from packager.tools.toolbox import *


class InstalledTablesModel(Observable):
    def __init__(self, baseModel):
        super().__init__()
        self.__baseModel = baseModel
        self.__tables = []
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
            self.__tables.append({'type': 'vpx', 'name': vpx_file.stem})
        for vpt_file in Path(self.baseModel.visual_pinball_path + "/tables").glob('**/*.vpt'):
            self.__tables.append({'type': 'vpt', 'name': vpt_file.stem})
        self.__tables.sort(key=lambda table: table['name'].upper())
        self.notify_all(self, events=['<<UPDATE TABLES>>'], tables=self.__tables)  # update listeners

    def selectTable(self, selection):
        self.__selectedTable = []
        for index in selection:
            self.__selectedTable.append(self.__tables[index])
        self.notify_all(self, events=['<<TABLE SELECTED>>'], tables=self.__selectedTable)  # update listeners

    def unSelectTable(self):
        self.__selectedTable = []
        self.notify_all(self, events=['<<TABLE UNSELECTED>>'])  # update listeners

    def extract_tables(self, table_choice) -> None:
        self.notify_all(self, events=['<<DISABLE_ALL>>', '<<BEGIN_ACTION>>'],
                        tables=self.__selectedTable)  # update listeners
        extract_thread = AsynRun(self.extract_tables_begin, self.extract_tables_end, context=table_choice)
        extract_thread.start()

    def extract_tables_begin(self, context=None) -> bool:
        to_overwrite = False
        if not self.__selectedTable:  # empty selection
            raise ValueError('No selected table')

        self.baseModel.logger.info("Begin Extraction")
        for table in self.__selectedTable:
            try:
                # check if table is already a package
                if Path(self.baseModel.package_path + '/' + table['name'] + self.baseModel.package_extension).exists():
                    if (is_read_only_file(
                            self.baseModel.package_path + '/' + table['name'] + self.baseModel.package_extension)):
                        result = messagebox.showerror("Extraction",
                                                      "A protected table package already exist.");
                        continue
                    result = messagebox.askokcancel("Extraction",
                                                    "Table package already extracted, would you like to merge it ?")
                    if result:
                        to_overwrite = True
                    else:
                        self.logger.info("Extraction canceled")
                        continue
                clean_dir(self.baseModel.tmp_path)
                self.logger.info("--[Working on '%s']------------------" % (table['name']))

                package = Package(self.baseModel, table['name'])
                package.new(self.baseModel.tmp_path)
                # TODO: besoin de copier les manifests ici pour la comparer les infos de fichiers
                if os.path.exists(self.baseModel.installed_path + '/' + table['name'] + '.manifest.json'):
                    self.logger.info("package found, use it")
                    package.merge(installed=True)
                else:
                    self.logger.info("no package found, create it")

                if context['visual_pinball'].get():
                    self.baseModel.visualPinball.extract(package)
                    self.baseModel.vpinMame.extract(package)
                    self.baseModel.ultraDMD.extract(table['name'], package)
                    if context['pinupSystem'].get():
                        self.baseModel.pinupSystem.extract(package, 'visual pinball')
                if context['pinballX'].get():
                    self.baseModel.pinballX.extract(table['name'], package)
                if context['futurPinball'].get():
                    self.logger.warning("extract from futurPinball is not yet implemented")
                    if context['pinupSystem'].get():
                        self.logger.warning("extract from pinupSystem is not yet implemented")
                package.save()
                package.pack()  # zip package

                if to_overwrite:
                    os.remove(self.baseModel.package_path + '/' + table['name'] + self.baseModel.package_extension)

                shutil.move(self.baseModel.tmp_path + '/' + table['name'] + self.baseModel.package_extension,
                            self.baseModel.package_path)

            except Exception as e:
                messagebox.showerror('Backup Package', str(e))
                return False
        clean_dir(self.baseModel.tmp_path)
        return True

    def extract_tables_end(self, context=None, success=True):
        self.logger.info("--[Done]------------------")
        self.notify_all(self, events=['<<END_ACTION>>', '<<ENABLE_ALL>>'],
                        tables=self.__selectedTable)  # update listeners
        self.baseModel.packagedTablesModel.update()

    def delete_tables(self, viewer):
        self.notify_all(self, events=['<<DISABLE_ALL>>', '<<BEGIN_ACTION>>'])  # update listeners
        tables = ', '.join(p['name'] for p in self.__selectedTable)
        del_confirmed = messagebox.askokcancel("Delete Table(s)",
                                               "Are you sure you want to delete table(s) '%s'" % tables,
                                               parent=viewer)
        if not del_confirmed:
            self.notify_all(self, events=['<<END_ACTION>>', '<<ENABLE_ALL>>'])  # update listeners
            return

        delete_table_thread = AsynRun(self.delete_tables_begin, self.delete_tables_end)
        delete_table_thread.start()

    def delete_tables_begin(self, context=None):
        if not self.__selectedTable:  # empty selection
            raise ValueError('No selected table')

        self.logger.info("--[Delete Table(s)]------------------")
        for table in self.__selectedTable:
            self.logger.info("--[Working on '%s']------------------" % (table['name']))

            ultraDMD = ''
            rom_list = []
            isPackage = False
            manifest = Manifest(table['name'], self.baseModel.package_version)
            try:
                manifest.open(self.baseModel.installed_path, installed=True)
                isPackage = True
                if manifest.exists_field('visual pinball/info/romName'):
                    rom_list = manifest.get_field('visual pinball/info/romName')
                if manifest.exists_field('visual pinball/info/ultraDMD'):
                    ultraDMD = manifest.get_field('visual pinball/info/ultraDMD')
            except:
                rom_list = self.baseModel.visualPinball.get_rom_name(table['name'])  # use package.manifest if exists

            self.baseModel.visualPinball.delete(table['name'])

            self.baseModel.vpinMame.delete(table['name'], rom_list)
            if isPackage:
                if ultraDMD != '':
                    self.baseModel.ultraDMD.delete(table['name'], dir_name=ultraDMD)  # use package.manifest if exists
            else:
                self.baseModel.ultraDMD.delete(table['name'])  # use package.manifest if exists
            self.baseModel.pinballX.delete(table['name'])
            self.baseModel.pinupSystem.delete(table['name'], 'visual pinball')
            self.logger.warning("delete on futurPinball is not yet implemented")
            if isPackage:
                os.unlink(self.baseModel.installed_path + '/' + manifest.filename)

        return True

    def delete_tables_end(self, context=None, success=True):
        self.logger.info("--[Done]------------------")
        self.update()
        self.notify_all(self, events=['<<END_ACTION>>', '<<ENABLE_ALL>>'])  # update listeners
