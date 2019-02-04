import os
from packager.model.installedTablesModel import *
from packager.pincab.visualPinball import VisualPinball
from packager.pincab.vpinMame import VPinMame
from packager.pincab.pinballX import PinballX
from packager.pincab.pinupSystem import PinUpSystem
from packager.model.packageEditorModel import PackageEditorModel
from packager.model.packagedTablesModel import *


class BaseModel:
    def __init__(self, logger, config):
        if Path(os.getcwd()).name=='packager':  # running from IDE
            self.__baseDir=''
        else: # running from exe
            self.__baseDir = 'lib/packager/'

        self.__config=config
        self.__tmp_path=config.get('working_dir')+'/tmp'
        self.__package_path=config.get('working_dir')+'/packages'
        self.__installed_path=config.get('working_dir')+'/installed'
        self.__logger=logger

        self.__installedTablesModel=InstalledTablesModel(self)
        self.__packagedTablesModel = PackagedTablesModel(self)
        self.__packageEditorModel=PackageEditorModel(self)
        self.__visualPinball=VisualPinball(self.logger, self)
        self.__pinupSystem=PinUpSystem(self.logger, self)
        self.__vpinMame=VPinMame(self.logger, self)
        self.__pinballX = PinballX(self.logger, self)


    @property
    def baseDir(self):
        return self.__baseDir

    @property
    def config(self):
        return self.__config

    @property
    def logger(self):
        return self.__logger

    @property
    def btEditImage(self):
        return self.__btEditImage

    @property
    def installedTablesModel(self):
        return self.__installedTablesModel



    @property
    def packagedTablesModel(self):
        return self.__packagedTablesModel

    @property
    def packageEditorModel(self):
        return self.__packageEditorModel

    @property
    def visual_pinball_path(self):
        return self.__config.get('visual_pinball_path')

    @property
    def pinballX_path(self):
        return self.__config.get('pinballX_path')

    @property
    def pinupSystem_path(self):
        return self.__config.get('pinupSystem_path')

    @property
    def tmp_path(self):
        return self.__tmp_path

    @property
    def package_path(self):
        if not os.path.exists(self.__package_path):
            os.makedirs(self.__package_path, exist_ok=True)
        return self.__package_path

    @property
    def installed_path(self):
        if not os.path.exists(self.__installed_path):
            os.makedirs(self.__installed_path, exist_ok=True)
        return self.__installed_path

    @property
    def package_extension(self):
        return self.__config.get('package_extension')

    @property
    def visualPinball(self):
        return self.__visualPinball

    @property
    def vpinMame(self):
        return self.__vpinMame

    @property
    def pinballX(self):
        return self.__pinballX

    @property
    def pinupSystem(self):
        return self.__pinupSystem
