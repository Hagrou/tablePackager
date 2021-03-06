from __future__ import annotations
import tkinter
from packager.model.package import *
from packager.tools.observer import Observable
from packager.tools.toolbox import *


class PackagedTablesModel(Observable):
    def __init__(self, baseModel: BaseModel):
        super().__init__()
        self.__baseModel = baseModel
        self.__packages = []
        self.__selectedPackage = []

    @property
    def baseModel(self) -> BaseModel:
        return self.__baseModel

    @property
    def logger(self) -> object:
        return self.baseModel.logger

    @property
    def packages(self) -> Package:
        return self.__packages

    @property
    def selectedPackage(self):
        return self.__selectedPackage

    def update(self):
        # read Packaged Tables
        self.__packages = []
        for packages_file in Path(self.baseModel.package_path).glob('**/*' + self.baseModel.package_extension):
            if is_read_only_file(packages_file):
                self.__packages.append({'name': packages_file.stem, 'protected': True})
            else:
                self.__packages.append({'name': packages_file.stem, 'protected': False})
        self.__packages.sort(key=lambda package: package['name'].upper())
        self.notify_all(self, events=['<<UPDATE PACKAGES>>', '<<PACKAGE UNSELECTED>>'],
                        packages=self.__packages)  # update listeners

    def isExists(self, packageName):
        for packages_file in Path(self.baseModel.package_path).glob('**/*' + self.baseModel.package_extension):
            if packageName == packages_file.stem:
                return True
        return False

    def selectPackages(self, selection):
        self.__selectedPackage = []
        for index in selection:
            self.__selectedPackage.append(self.__packages[index])
        self.notify_all(self, events=['<<PACKAGE SELECTED>>'], tables=self.__packages)  # update listeners

    def unSelectPackages(self):
        self.__selectedPackage = []
        self.notify_all(self, events=['<<PACKAGE UNSELECTED>>'])  # update listeners

    def deployPackage(self, appChoice):
        self.notify_all(self, events=['<<DISABLE_ALL>>', '<<BEGIN_ACTION>>'])  # update listeners
        deployThread = AsynRun(self.deploy_tables_begin, self.deploy_tables_end, context=appChoice)
        deployThread.start()

    def deploy_tables_begin(self, context=None):
        if not self.__selectedPackage:  # empty selection
            raise ValueError('No selected package')
        try:
            for packageInfo in self.__selectedPackage:
                self.logger.info("--[Deploy '%s']------------------" % (packageInfo['name']))
                package = Package(self.baseModel, packageInfo['name'])
                package.unpack()
                package.open(self.baseModel.tmp_path)

                if context['visual_pinball'].get():
                    self.baseModel.visualPinball.deploy(package)
                    self.baseModel.vpinMame.deploy(package)
                    self.baseModel.ultraDMD.deploy(package)
                if context['pinballX'].get():
                    self.baseModel.pinballX.deploy(package)

                if context['futurPinball'].get():
                    self.logger.warning("deploy to futur Pinball is not yet implemented")
                if context['pinupSystem'].get():
                    self.baseModel.pinupSystem.deploy(package, 'visual pinball')

                shutil.copyfile(
                    self.baseModel.tmp_path + '/' + packageInfo['name'] + '/' + packageInfo['name'] + '.manifest.json',
                    self.baseModel.installed_path + '/' + packageInfo['name'] + '.manifest.json')
            clean_dir(self.baseModel.tmp_path)
            return True
        except Exception as e:
            tkinter.messagebox.showerror('Deploy Package', str(e))
            return False

    def deploy_tables_end(self, context=None, success=True):
        if success:
            self.logger.info("--[Done]------------------")
        else:
            self.logger.error("--[Failed]------------------")
        self.notify_all(self, events=['<<END_ACTION>>', '<<ENABLE_ALL>>'])  # update listeners
        self.baseModel.installedTablesModel.update()

    def deletePackages(self, viewer):
        self.notify_all(self, events=['<<DISABLE_ALL>>', '<<BEGIN_ACTION>>'])  # update listeners
        packages = ', '.join(p['name'] for p in self.selectedPackage)
        delConfirmed = tkinter.messagebox.askokcancel("Delete Package",
                                                      "Are you sure you want to delete package(s) '%s'" % (packages),
                                                      parent=viewer)
        if delConfirmed:
            self.logger.info("--[Delete Package(s=]------------------")
            for packageInfo in self.selectedPackage:
                try:
                    os.unlink(
                        self.baseModel.package_path + '/' + packageInfo['name'] + self.baseModel.package_extension)
                except OSError as e:
                    self.logger.error(str(e))
                    continue
                self.logger.info("+ del %s" % (
                            self.baseModel.package_path + '/' + packageInfo['name'] + self.baseModel.package_extension))
            self.logger.info("--[Done]------------------")
        self.notify_all(self, events=['<<END_ACTION>>', '<<ENABLE_ALL>>'])  # update listeners
        self.baseModel.packagedTablesModel.update()

    def backupPackages(self, viewer, backup_path):
        self.notify_all(self, events=['<<DISABLE_ALL>>', '<<BEGIN_ACTION>>'])  # update listeners
        backup_package = AsynRun(self.backup_package_begin, self.backup_package_end, context={'path': backup_path})
        backup_package.start()

    def backup_package_begin(self, context=None):
        if not self.__selectedPackage:  # empty selection
            raise ValueError('No selected package')
        try:
            self.logger.info("--[Backup Package]------------------")
            for packageInfo in self.__selectedPackage:
                packageFileName = '/' + packageInfo['name'] + self.baseModel.package_extension
                self.logger.info("+ copy '%s' -> '%s'" % (packageFileName, context['path']))
                shutil.copyfile(self.baseModel.package_path + '/' + packageFileName,
                                context['path'] + '/' + packageFileName)
            return True
        except Exception as e:
            tkinter.messagebox.showerror('Backup Package', str(e))
            return False

    def backup_package_end(self, context=None, success=True):
        if success:
            self.logger.info("--[Done]------------------")
        else:
            self.logger.error("--[Failed]------------------")
        self.notify_all(self, events=['<<END_ACTION>>', '<<ENABLE_ALL>>'])  # update listeners

    def restore_package(self, viewer, package_file):
        self.notify_all(self, events=['<<DISABLE_ALL>>', '<<BEGIN_ACTION>>'])  # update listeners
        restore_thread = AsynRun(self.restore_package_begin, self.restore_package_end, context={'package': package_file})
        restore_thread.start()

    def restore_package_begin(self, context=None):
        try:
            self.logger.info("--[Restore Package]------------------")
            unpack(context['package'], self.baseModel.tmp_path)
            package = Package(self.baseModel, Path(context['package']).stem)
            package.open(self.baseModel.tmp_path)
            package.save()
            package.pack()

            setReadWriteFile(self.baseModel.package_path + '/' + package.name + self.baseModel.package_extension)
            shutil.copy(self.baseModel.tmp_path + '/' + package.name + self.baseModel.package_extension,
                        self.baseModel.package_path)
            if package.get_field('info/protected') == 'True':
                self.logger.warning("Protect package with Read Only file status")
                setReadOnlyFile(
                    self.baseModel.package_path + '/' + package.name + self.baseModel.package_extension)
            clean_dir(self.baseModel.tmp_path)
            print("ici")
        except Exception as e:
            tkinter.messagebox.showerror('Restore Package', str(e))
            return False
        return True

    def restore_package_end(self, context=None, success=True):
        if success:
            self.logger.info("--[Done]------------------")
            self.update()
        else:
            self.logger.error("--[Failed]------------------")
        self.notify_all(self, events=['<<END_ACTION>>', '<<ENABLE_ALL>>'])  # update listeners
