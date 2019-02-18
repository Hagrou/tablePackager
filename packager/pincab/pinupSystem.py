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


    def extractFile(self, package, product, media, dataPath, extension=''):
        for file in Path(self.baseModel.pinupSystem_path + "/POPMedia/" + self.getProductPath(product) + '/'+ media).glob('**/%s%s*' % (package.name, extension)):
            package.add_file(file, dataPath)  # Add vpx file

    def extract(self, package, product):
        if not os.path.exists(self.pinupSystem_path):
            raise ValueError('PinupSystem not found(%s)' % self.pinupSystem_path)

        self.logger.info("* PinupSystem files")
        self.extractFile(package, product,'Audio','media/Audio')
        self.extractFile(package, product, 'AudioLaunch', 'media/AudioLaunch')
        self.extractFile(package, product, 'BackGlass', 'media/Backglass')
        self.extractFile(package, product, 'DMD', 'media/DMD')
        self.extractFile(package, product, 'DMDVideos', 'media/DMDVideos')
        self.extractFile(package, product, 'HighScores', 'media/HighScores')
        self.extractFile(package, product, 'GameHelp', 'media/Instruction Cards')
        self.extractFile(package, product, 'PlayField', 'media/PlayField')
        self.extractFile(package, product, 'Topper', 'media/Topper')
        self.extractFile(package, product, 'Wheel', 'media/Wheel')
        self.extractFile(package, product, 'ScreenGrabs', 'media/ScreenGrabs')
        self.extractFile(package, product, 'TableVideos', 'media/TableVideos')
        self.extractFile(package, product, 'GameInfo', 'media/Flyers Inside', extension='.inside')
        self.extractFile(package, product, 'GameInfo', 'media/Flyers Front', extension='.front')
        self.extractFile(package, product, 'GameInfo', 'media/Flyers Back', extension='.back')

    def deploy(self, package, product):
        self.logger.info("* Deploy PinUp Media")
        if not Path(self.baseModel.tmp_path + "/" + package.name).exists():
            raise ValueError('Path not found (%s)' % self.baseModel.tmp_path + "/" + package.name)

        copytree(self.logger,
                 self.baseModel.tmp_path + "/" + package.name + "/Media/Audio",
                 self.baseModel.pinupSystem_path + "/POPMedia/" + self.getProductPath(product)+'/Audio')
        copytree(self.logger,
                 self.baseModel.tmp_path + "/" + package.name + "/Media/AudioLaunch",
                 self.baseModel.pinupSystem_path + "/POPMedia/" + self.getProductPath(product) + '/AudioLaunch')
        copytree(self.logger,
                 self.baseModel.tmp_path + "/" + package.name + "/Media/BackGlass",
                 self.baseModel.pinupSystem_path + "/POPMedia/" + self.getProductPath(product) + '/BackGlass')
        copytree(self.logger,
                 self.baseModel.tmp_path + "/" + package.name + "/Media/DMD",
                 self.baseModel.pinupSystem_path + "/POPMedia/" + self.getProductPath(product) + '/DMD')
        copytree(self.logger,
                 self.baseModel.tmp_path + "/" + package.name + "/Media/DMDVideos",
                 self.baseModel.pinupSystem_path + "/POPMedia/" + self.getProductPath(product) + '/DMDVideos')
        copytree(self.logger,
                 self.baseModel.tmp_path + "/" + package.name + "/Media/HighScores",
                 self.baseModel.pinupSystem_path + "/POPMedia/" + self.getProductPath(product) + '/HighScores')
        copytree(self.logger,
                 self.baseModel.tmp_path + "/" + package.name + "/Media/Instruction Cards",
                 self.baseModel.pinupSystem_path + "/POPMedia/" + self.getProductPath(product) + '/GameHelp')
        copytree(self.logger,
                 self.baseModel.tmp_path + "/" + package.name + "/Media/PlayField",
                 self.baseModel.pinupSystem_path + "/POPMedia/" + self.getProductPath(product) + '/PlayField')
        copytree(self.logger,
                 self.baseModel.tmp_path + "/" + package.name + "/Media/Topper",
                 self.baseModel.pinupSystem_path + "/POPMedia/" + self.getProductPath(product) + '/Topper')
        copytree(self.logger,
                 self.baseModel.tmp_path + "/" + package.name + "/Media/Wheel",
                 self.baseModel.pinupSystem_path + "/POPMedia/" + self.getProductPath(product) + '/Wheel')
        copytree(self.logger,
                 self.baseModel.tmp_path + "/" + package.name + "/Media/ScreenGrabs",
                 self.baseModel.pinupSystem_path + "/POPMedia/" + self.getProductPath(product) + '/ScreenGrabs')
        copytree(self.logger,
                 self.baseModel.tmp_path + "/" + package.name + "/Media/TableVideos",
                 self.baseModel.pinupSystem_path + "/POPMedia/" + self.getProductPath(product) + '/TableVideos')
        copytree(self.logger,
                 self.baseModel.tmp_path + "/" + package.name + "/Media/Flyers Inside",
                 self.baseModel.pinupSystem_path + "/POPMedia/" + self.getProductPath(product) + '/GameInfo')
        copytree(self.logger,
                 self.baseModel.tmp_path + "/" + package.name + "/Media/Flyers Front",
                 self.baseModel.pinupSystem_path + "/POPMedia/" + self.getProductPath(product) + '/GameInfo')
        copytree(self.logger,
                 self.baseModel.tmp_path + "/" + package.name + "/Media/Flyers Back",
                 self.baseModel.pinupSystem_path + "/POPMedia/" + self.getProductPath(product) + '/GameInfo')

    def delete(self, table_name,product):
        self.logger.info("* Delete PinUp Media")

        popMedia=self.baseModel.pinupSystem_path + "/POPMedia/" + self.getProductPath(product)
        if not Path(popMedia).exists():
            raise ValueError('Path not found (%s)' % popMedia + "/" + table_name)

        for file in Path(popMedia).glob('**/%s.*' % table_name):
            self.logger.info("- delete file %s" % file)
            os.remove(file)