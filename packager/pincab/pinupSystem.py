from packager.tools.toolbox import *

class PinUpSystem:
    def __init__(self, logger, baseModel):
        self.__baseModel=baseModel
        self.__logger=logger

    @property
    def logger(self):
        return self.__logger

    @property
    def baseModel(self):
        return self.__baseModel

    @property
    def pinupSystem_path(self):
        return self.__baseModel.pinupSystem_path

    def getProductPath(self, product):
        if product=='visual pinball':
            return 'Visual Pinball X'
        return 'Visual Pinball X'

    def deploy(self, package, product):
        self.logger.info("* Deploy PinUp Media")
        if not Path(self.baseModel.tmp_path + "/" + package.name).exists():
            raise ValueError('Path not found (%s)' % self.baseModel.tmp_path + "/" + package.name)

        copytree(self.logger,
                 self.baseModel.tmp_path + "/" + package.name + "/Media",
                 self.baseModel.pinupSystem_path+"/POPMedia/"+self.getProductPath(product))
