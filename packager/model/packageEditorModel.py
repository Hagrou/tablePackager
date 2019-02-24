from tkinter import messagebox
from packager.model.package import *
from packager.tools.observer import Observable
from packager.tools.toolbox import *

class PackageEditorModel(Observable):
    def __init__(self, baseModel):
        super().__init__()
        self.__baseModel=baseModel
        self.__currentPackage={}
        self.__package=None

    @property
    def baseModel(self):
        return self.__baseModel

    @property
    def logger(self):
        return self.__baseModel.logger

    @property
    def currentPackage(self):
        return self.__currentPackage

    @property
    def package(self):
        return self.__package

    @currentPackage.setter
    def currentPackage(self, package):
        self.__currentPackage=package

    def edit_package(self, package):
        self.currentPackage=package
        self.notify_all(self, events=['<<DISABLE_ALL>>', '<<BEGIN_ACTION>>'])  # update listeners
        unpackThread = AsynRun(self.edit_package_begin, self.edit_package_end)
        unpackThread.start()

    def edit_package_begin(self,context=None):
        self.logger.info("--[Edit Package '%s']------------------" % (self.currentPackage['name']))
        self.__package = Package(self.baseModel, self.currentPackage['name'])
        self.package.unpack()
        self.package.open(self.baseModel.tmp_path)

    def edit_package_end(self,context=None):
        self.logger.info("* Unpack Done")
        self.notify_all(self, events=['<<END_ACTION>>','<<VIEW EDITOR>>'])  # update listeners

    def new_package(self):
        self.currentPackage = {'name':'John Doe'}
        self.logger.info("--[New Package '%s']------------------" % (self.currentPackage['name']))
        self.notify_all(self, events=['<<DISABLE_ALL>>', '<<BEGIN_ACTION>>'])  # update listeners
        self.__package = Package(self.baseModel, 'John Doe')
        self.package.new(self.baseModel.tmp_path)
        self.package.save()
        self.notify_all(self, events=['<<END_ACTION>>', '<<VIEW EDITOR>>'])  # update listeners

    def save_package(self,info):
        self.logger.info("--[Save Package]-----------------------")
        self.notify_all(self, events=['<<BEGIN_ACTION>>', '<<HIDE EDITOR>>'])  # update listeners
        packThread = AsynRun(self.pack_package_begin, self.pack_package_end, context=info)
        packThread.start()

    def pack_package_begin(self,context=None):
        for key, val in context.items():
            self.package.set_field(key,val)

        self.package.save()
        self.package.pack()
        shutil.copy(self.baseModel.tmp_path + '/' + self.package.name + self.baseModel.package_extension,
                    self.baseModel.package_path)
        clean_dir(self.baseModel.tmp_path)

    def pack_package_end(self,context=None):
        self.logger.info("--[Edition '%s' Done]------------------" % (self.package.name))
        self.notify_all(self, events=['<<END_ACTION>>','<<PACKAGE UNSELECTED>>'])  # update listeners
        self.baseModel.packagedTablesModel.update()

    def rename_package(self, newPackageName):
        self.logger.info("--[Rename Package to '%s']----------" % newPackageName )
        self.notify_all(self, events=['<<DISABLE_ALL>>'])  # update listeners
        renameThread = AsynRun(self.rename_package_begin, self.rename_package_end, context={'newPackageName':newPackageName})
        renameThread.start()

    def rename_package_begin(self,context=None):
        try:
            self.package.rename_package(context['newPackageName'])
        except Exception as e:
            print(e)
            #essagebox.showerror('Add File Error', e.strerror, parent=viewer)

    def rename_package_end(self,context=None):
        self.logger.info("--[Rename '%s' Done]------------------" % (self.package.name))
        self.notify_all(self, events=['<<UPDATE_EDITOR>>','<<ENABLE_ALL>>'])  # update listeners
        self.baseModel.packagedTablesModel.update()

    def cancel_edition(self):
        if not self.__currentPackage:  # empty selection
            raise ValueError('No selected package')
        self.logger.info("--[Edition '%s' Canceled]------------------" % (self.package.name))
        clean_dir(self.baseModel.tmp_path)
        self.notify_all(self, events=['<<END_ACTION>>', '<<PACKAGE UNSELECTED>>', '<<HIDE EDITOR>>'])  # update listeners

    def update_package(self):
        self.package.update()
        self.notify_all(self, events=['<<UPDATE_EDITOR>>'])  # update listeners

    def add_file(self, viewer, dataPath, srcFile, requiredName):
        try:
            filename = Path(srcFile).name
            targetFile=srcFile

            if Path(filename).stem != requiredName:
                suffixes = Path(filename).suffixes
                newName = requiredName + ''.join(suffixes)
                if not messagebox.askokcancel("Renaming File","The name of the file must be the same as package name. New name file will be %s." % newName,
                                              parent=viewer):
                    self.logger.info('* add file canceled')
                    return
                targetFile=newName

            filename = Path(targetFile).name
            if self.package.exists_file(dataPath, filename):
                if not viewer.askokcancel('File already in Package','overwrite it?',parent=viewer):
                    self.logger.info('* add file canceled')
                    return

            self.package.add_file(srcFile, dataPath, dstFile=targetFile)
            a=Path(targetFile).suffix
            if Path(targetFile).suffix=='.vpx':
                romName=self.baseModel.visualPinball.extract_rom_name(self.package.directory+'/'+self.package.name+'/'+dataPath+'/'+targetFile)
                self.logger.info('+ updating rom name [%s]' % romName)
                self.package.set_field('visual pinball/info/romName', romName)
                self.package.save()
            self.update_package()

        except Exception as e:
            messagebox.showerror('Add File Error', e.strerror, parent=viewer)

    def del_file(self,viewer, dataPath, srcFile):
        try:
            self.package.remove_file(srcFile, dataPath)
            self.update_package()
        except Exception as e:
            messagebox.showerror('Delete File Error', e.strerror, parent=viewer)

    def get_fileInfo(self, viewer, dataPath, srcFile):
        return self.package.manifest.get_file(dataPath, srcFile)

    def edit_file(self, viewer, dataPath, srcFile):
        fileInfo=self.package.manifest.get_file(dataPath, srcFile)
        print(fileInfo)
