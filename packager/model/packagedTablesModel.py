from tkinter import messagebox
from packager.model.package import *
from packager.tools.observer import Observable
from packager.tools.toolbox import *

class PackagedTablesModel(Observable):
    def __init__(self, baseModel):
        super().__init__()
        self.__baseModel=baseModel
        self.__packages=[]
        self.__selectedPackage = []

    @property
    def baseModel(self):
        return self.__baseModel

    @property
    def logger(self):
        return self.baseModel.logger

    @property
    def packages(self):
        return self.__packages

    @property
    def selectedPackage(self):
        return self.__selectedPackage

    def update(self):
        # read Packaged Tables
        self.__packages=[]
        for packages_file in Path(self.baseModel.package_path).glob('**/*'+self.baseModel.package_extension):
            self.__packages.append({'name':packages_file.stem})

        self.__packages.sort(key=lambda package: package['name'].upper())
        self.notify_all(self, events=['<<UPDATE PACKAGES>>','<<PACKAGE UNSELECTED>>'], packages=self.__packages) # update listeners

    def isExists(self, packageName):
        for packages_file in Path(self.baseModel.package_path).glob('**/*'+self.baseModel.package_extension):
            if packageName==packages_file.stem:
                return True
        return False

    def selectPackages(self, selection):
        self.__selectedPackage=[]
        for index in selection:
            self.__selectedPackage.append(self.__packages[index])
        self.notify_all(self, events=['<<PACKAGE SELECTED>>'],tables=self.__packages)  # update listeners

    def unSelectPackages(self):
        self.__selectedPackage = []
        self.notify_all(self, events=['<<PACKAGE UNSELECTED>>'])  # update listeners

    def deployPackage(self,appChoice):
        self.notify_all(self, events=['<<DISABLE_ALL>>','<<BEGIN_ACTION>>'])  # update listeners
        deployThread = AsynRun(self.deploy_tables_begin, self.deploy_tables_end, context=appChoice)
        deployThread.start()

    def deploy_tables_begin(self,context=None):
        if not self.__selectedPackage: # empty selection
            raise ValueError('No selected package')
        for packageInfo in self.__selectedPackage:
            self.logger.info("--[Deploy '%s']------------------" % (packageInfo['name']))
            package = Package(self.baseModel, packageInfo['name'])

            package.unpack()
            if context['visual_pinball'].get():
                self.baseModel.visualPinball.deploy(package)
                self.baseModel.vpinMame.deploy(package)  # TODO: give the product choice
            if context['pinballX'].get():
                self.logger.warning("deploy to pinballX is not yet implemented")

            if context['futurPinball'].get():
                self.logger.warning("deploy to futur Pinball is not yet implemented")
            if context['pinupSystem'].get():
                self.baseModel.pinupSystem.deploy(package,'visual pinball')

            shutil.copyfile(self.baseModel.tmp_path+'/'+packageInfo['name']+'/'+packageInfo['name']+'.manifest.json',
                            self.baseModel.installed_path+'/'+packageInfo['name']+'.manifest.json')


            self.logger.info("--['%s' Done]------------------" % (packageInfo['name']))
        clean_dir(self.baseModel.tmp_path)

    def deploy_tables_end(self,context=None):
        self.baseModel.logger.info("Extraction Ended")
        self.notify_all(self, events=['<<END_ACTION>>','<<ENABLE_ALL>>'])  # update listeners
        self.baseModel.installedTablesModel.update()

    def deletePackages(self, viewer):
        self.notify_all(self, events=['<<DISABLE_ALL>>', '<<BEGIN_ACTION>>'])  # update listeners
        packages=', '.join(p['name'] for p in self.selectedPackage)
        delConfirmed=messagebox.askokcancel("Delete Package", "Are you sure you want to delete package(s) '%s'" % (packages),
                               parent=viewer)
        if delConfirmed:
            self.logger.info("--[Delete Package(s=]------------------")
            for packageInfo in self.selectedPackage:
                os.unlink(self.baseModel.package_path + '/' + packageInfo['name'] + self.baseModel.package_extension)
                self.logger.info("+ del %s" % (self.baseModel.package_path+'/'+packageInfo['name']+self.baseModel.package_extension))
            self.logger.info("--[Done]------------------")
        self.notify_all(self, events=['<<END_ACTION>>', '<<ENABLE_ALL>>'])  # update listeners
        self.baseModel.packagedTablesModel.update()
