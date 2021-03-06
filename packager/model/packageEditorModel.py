import tkinter

from packager.model.baseModel import *
from packager.model.package import Package
from packager.tools.observer import Observable
from packager.tools.toolbox import *


class PackageEditorModel(Observable):
    def __init__(self, baseModel: object):
        super().__init__()
        self.__baseModel = baseModel
        self.__currentPackage = {}
        self.__package = None

    @property
    def baseModel(self) -> object:
        return self.__baseModel

    @property
    def logger(self):
        return self.__baseModel.logger

    @property
    def currentPackage(self):
        return self.__currentPackage

    @property
    def package(self) -> Package:
        return self.__package

    @currentPackage.setter
    def currentPackage(self, package):
        self.__currentPackage = package

    def edit_package(self, package):
        self.currentPackage = package
        self.notify_all(self, events=['<<DISABLE_ALL>>', '<<BEGIN_ACTION>>'])  # update listeners
        unpack_thread = AsynRun(self.edit_package_begin, self.edit_package_end)
        unpack_thread.start()

    def edit_package_begin(self, context=None):
        self.logger.info("--[Edit Package '%s']------------------" % (self.currentPackage['name']))
        try:
            self.__package = Package(self.baseModel, self.currentPackage['name'])
            self.package.unpack()
            self.package.open(self.baseModel.tmp_path)
        except Exception as e:
            tkinter.messagebox.showerror('Edit Package', str(e))
            return False
        return True

    def edit_package_end(self, context=None, success=True):
        if success:
            self.logger.info("* Unpack Done")
            self.notify_all(self, events=['<<END_ACTION>>', '<<VIEW EDITOR>>'])  # update listeners
        else:
            self.logger.error("* Unpack failed")
            self.notify_all(self, events=['<<END_ACTION>>'])  # update listeners

    def new_package(self):
        self.currentPackage = {'name': 'John Doe'}
        self.logger.info("--[New Package '%s']------------------" % (self.currentPackage['name']))
        self.notify_all(self, events=['<<DISABLE_ALL>>', '<<BEGIN_ACTION>>'])  # update listeners
        self.__package = Package(self.baseModel, 'John Doe')
        self.package.new(self.baseModel.tmp_path)
        self.package.save()
        self.notify_all(self, events=['<<END_ACTION>>', '<<VIEW EDITOR>>'])  # update listeners

    def save_package(self, info):
        self.logger.info("--[Save Package]-----------------------")
        self.notify_all(self, events=['<<BEGIN_ACTION>>', '<<HIDE EDITOR>>'])  # update listeners
        pack_thread = AsynRun(self.pack_package_begin, self.pack_package_end, context=info)
        pack_thread.start()

    def pack_package_begin(self, context=None):
        for key, val in context.items():
            self.package.set_field(key, val)

        self.package.save()
        self.package.pack()

        setReadWriteFile(self.baseModel.package_path + '/' + self.package.name + self.baseModel.package_extension)
        shutil.copy(self.baseModel.tmp_path + '/' + self.package.name + self.baseModel.package_extension,
                    self.baseModel.package_path)
        if self.package.get_field('info/protected') == 'True':
            self.logger.warning("Protect package with Read Only file status")
            setReadOnlyFile(self.baseModel.package_path + '/' + self.package.name + self.baseModel.package_extension)
        clean_dir(self.baseModel.tmp_path)
        return True

    def pack_package_end(self, context=None, success=True):
        self.logger.info("--[Edition '%s' Done]------------------" % (self.package.name))
        self.notify_all(self, events=['<<END_ACTION>>', '<<PACKAGE UNSELECTED>>', '<<ENABLE_ALL>>'])  # update listeners
        self.baseModel.packagedTablesModel.update()

    def rename_package(self, new_package_name):
        self.logger.info("--[Rename Package to '%s']----------" % new_package_name)
        self.notify_all(self, events=['<<DISABLE_ALL>>'])  # update listeners
        rename_thread = AsynRun(self.rename_package_begin, self.rename_package_end,
                                context={'newPackageName': new_package_name})
        rename_thread.start()

    def rename_package_begin(self, context=None):
        try:
            self.package.rename_package(context['newPackageName'])
            return True
        except Exception as e:
            tkinter.messagebox.showerror('rename package Error', str(e))
            return False

    def rename_package_end(self, context=None, success=True):
        if success:
            self.logger.info("--[Rename '%s' Done]------------------" % (self.package.name))
        else:
            self.logger.error("--[Rename '%s' Failed]------------------" % (self.package.name))
        self.notify_all(self, events=['<<UPDATE_EDITOR>>', '<<ENABLE_ALL>>'])  # update listeners
        self.baseModel.packagedTablesModel.update()

    def cancel_edition(self):
        if not self.__currentPackage:  # empty selection
            raise ValueError('No selected package')
        self.logger.info("--[Edition '%s' Canceled]------------------" % (self.package.name))
        clean_dir(self.baseModel.tmp_path)
        self.notify_all(self, events=['<<END_ACTION>>', '<<PACKAGE UNSELECTED>>', '<<HIDE EDITOR>>',
                                      '<<ENABLE_ALL>>'])  # update listeners

    def update_package(self, selection=None):
        self.package.update()
        self.notify_all(self, events=['<<UPDATE_EDITOR>>'], selection_set=selection)  # update listeners

    def add_ultra_dmd(self, viewer, dataPath, src_dir):
        self.logger.info("* UltraDMD files")

        ultra_dmd_dir = str(Path(src_dir).stem)
        self.package.set_field('visual pinball/info/ultraDMD', ultra_dmd_dir)
        for file in Path(src_dir).glob('**/*'):
            self.package.add_file(file, 'UltraDMD/content')

    def add_file(self, viewer, data_path, srcFile, required_name):
        rename_it = False
        try:
            filename = Path(srcFile).name
            target_file = srcFile

            if type(required_name) is list:
                if len(required_name) == 0:
                    tkinter.messagebox.showwarning("Renaming File",
                                                   "No information found for filename",
                                                   parent=viewer)
                else:
                    rename_it = [name for name in required_name if name.upper() == Path(filename).stem.upper()] == []
                    required_name=required_name[0]

            else:
                rename_it = Path(filename).stem.upper() != required_name.upper()
            if rename_it:
                suffixes = Path(filename).suffixes
                new_name = required_name + ''.join(suffixes)
                if not tkinter.messagebox.askokcancel("Renaming File",
                                                      "The name of the file must be the same as package name. New name file will be %s." % new_name,
                                                      parent=viewer):
                    self.logger.info('* add file canceled')
                    return
                target_file = new_name

            filename = Path(target_file).name
            if self.package.exists_file(data_path, filename):
                if not tkinter.messagebox.askokcancel('File already in Package', 'overwrite it?', parent=viewer):
                    self.logger.info('* add file canceled')
                    return

            self.package.add_file(srcFile, data_path, dst_file=target_file)
            if Path(target_file).suffix == '.vpx' or Path(target_file).suffix == '.vpt':
                rom_name = self.baseModel.visualPinball.extract_rom_name(srcFile)  # Bug?
                self.logger.info('+ updating rom name [%s]' % rom_name)
                self.package.set_field('visual pinball/info/romName', rom_name)
                self.package.save()
            self.update_package()

        except Exception as e:
            tkinter.messagebox.showerror('Add File Error', str(e), parent=viewer)

    def del_file(self, viewer, dataPath, srcFile):
        try:
            self.package.remove_file(srcFile, dataPath)
            self.update_package()
        except Exception as e:
            tkinter.messagebox.showerror('Delete File Error', str(e), parent=viewer)

    def get_fileInfo(self, viewer, dataPath, srcFile):
        return self.package.manifest.get_file(dataPath, srcFile)

    def up_file(self, viewer, data_path, src_file):
        dst_data_path = self.package.manifest.prev_file_data_path(data_path, src_file)
        if dst_data_path != '':
            self.package.move_file(src_file, data_path, dst_data_path)
            self.update_package(selection=(dst_data_path, src_file))

    def down_file(self, viewer, data_path, src_file):
        dst_data_path = self.package.manifest.next_file_data_path(data_path, src_file)
        if dst_data_path != '':
            self.package.move_file(src_file, data_path, dst_data_path)
            self.update_package(selection=(dst_data_path, src_file))

    def get_first_image(self):
        return self.package.manifest.get_first_image()
