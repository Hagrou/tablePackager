from packager.tools.toolbox import *
from packager.model.package import Package


class PinUpSystem:
    def __init__(self, logger, baseModel):
        self.__baseModel = baseModel
        self.__logger = logger

    @property
    def logger(self):
        return self.__logger

    @property
    def baseModel(self):
        return self.__baseModel

    @property
    def pinupSystem_path(self):
        return self.__baseModel.pinupSystem_path

    def get_product_path(self, product: str) -> str:
        if product == 'visual pinball':
            return 'Visual Pinball X'
        return 'Visual Pinball X'

    def extract_file(self, package: Package, product: str, media, dataPath, extension='') -> None:
        for file in Path(
                self.baseModel.pinupSystem_path + "/POPMedia/" + self.get_product_path(product) + '/' + media)\
                .glob('**/%s%s*' % (package.name, extension)):
            package.add_file(file, dataPath)  # Add vpx file

    def extract(self, package: Package, product: str) -> None:
        if not os.path.exists(self.pinupSystem_path):
            self.logger.warning('PinupSystem not found(%s)' % self.pinupSystem_path)
            return

        self.logger.info("* PinupSystem files")
        self.extract_file(package, product, 'Audio', 'media/Audio')
        self.extract_file(package, product, 'AudioLaunch', 'media/AudioLaunch')
        self.extract_file(package, product, 'BackGlass', 'media/Backglass')
        self.extract_file(package, product, 'DMD', 'media/DMD')
        self.extract_file(package, product, 'DMDVideos', 'media/DMDVideos')
        self.extract_file(package, product, 'HighScores', 'media/HighScores')
        self.extract_file(package, product, 'GameHelp', 'media/Instruction Cards')
        self.extract_file(package, product, 'PlayField', 'media/PlayField')
        self.extract_file(package, product, 'Topper', 'media/Topper')
        self.extract_file(package, product, 'Wheel', 'media/Wheel')
        self.extract_file(package, product, 'ScreenGrabs', 'media/ScreenGrabs')
        self.extract_file(package, product, 'TableVideos', 'media/TableVideos')
        self.extract_file(package, product, 'GameInfo', 'media/Flyers Inside', extension='.inside')
        self.extract_file(package, product, 'GameInfo', 'media/Flyers Front', extension='.front')
        self.extract_file(package, product, 'GameInfo', 'media/Flyers Back', extension='.back')
        self.extract_file(package, product, 'Loading', 'media/Loading')

    def deploy(self, package: Package, product: str) -> None:
        self.logger.info("* Deploy PinUp Media")

        if not os.path.exists(self.pinupSystem_path):
            self.logger.warning('PinupSystem not found(%s)' % self.pinupSystem_path)
            return

        if not Path(self.baseModel.tmp_path + "/" + package.name).exists():
            raise ValueError('Path not found (%s)' % self.baseModel.tmp_path + "/" + package.name)

        copytree(self.logger,
                 self.baseModel.tmp_path + "/" + package.name + "/Media/Audio",
                 self.baseModel.pinupSystem_path + "/POPMedia/" + self.get_product_path(product) + '/Audio')
        copytree(self.logger,
                 self.baseModel.tmp_path + "/" + package.name + "/Media/AudioLaunch",
                 self.baseModel.pinupSystem_path + "/POPMedia/" + self.get_product_path(product) + '/AudioLaunch')
        copytree(self.logger,
                 self.baseModel.tmp_path + "/" + package.name + "/Media/BackGlass",
                 self.baseModel.pinupSystem_path + "/POPMedia/" + self.get_product_path(product) + '/BackGlass')
        copytree(self.logger,
                 self.baseModel.tmp_path + "/" + package.name + "/Media/DMD",
                 self.baseModel.pinupSystem_path + "/POPMedia/" + self.get_product_path(product) + '/DMD')
        copytree(self.logger,
                 self.baseModel.tmp_path + "/" + package.name + "/Media/DMDVideos",
                 self.baseModel.pinupSystem_path + "/POPMedia/" + self.get_product_path(product) + '/DMDVideos')
        copytree(self.logger,
                 self.baseModel.tmp_path + "/" + package.name + "/Media/HighScores",
                 self.baseModel.pinupSystem_path + "/POPMedia/" + self.get_product_path(product) + '/HighScores')
        copytree(self.logger,
                 self.baseModel.tmp_path + "/" + package.name + "/Media/Instruction Cards",
                 self.baseModel.pinupSystem_path + "/POPMedia/" + self.get_product_path(product) + '/GameHelp')
        copytree(self.logger,
                 self.baseModel.tmp_path + "/" + package.name + "/Media/PlayField",
                 self.baseModel.pinupSystem_path + "/POPMedia/" + self.get_product_path(product) + '/PlayField')
        copytree(self.logger,
                 self.baseModel.tmp_path + "/" + package.name + "/Media/Topper",
                 self.baseModel.pinupSystem_path + "/POPMedia/" + self.get_product_path(product) + '/Topper')
        copytree(self.logger,
                 self.baseModel.tmp_path + "/" + package.name + "/Media/TopperVideos",
                 self.baseModel.pinupSystem_path + "/POPMedia/" + self.get_product_path(product) + '/Topper')
        copytree(self.logger,
                 self.baseModel.tmp_path + "/" + package.name + "/Media/Wheel",
                 self.baseModel.pinupSystem_path + "/POPMedia/" + self.get_product_path(product) + '/Wheel')
        copytree(self.logger,
                 self.baseModel.tmp_path + "/" + package.name + "/Media/ScreenGrabs",
                 self.baseModel.pinupSystem_path + "/POPMedia/" + self.get_product_path(product) + '/ScreenGrabs')
        copytree(self.logger,
                 self.baseModel.tmp_path + "/" + package.name + "/Media/TableVideos",
                 self.baseModel.pinupSystem_path + "/POPMedia/" + self.get_product_path(product) + '/TableVideos')
        copytree(self.logger,
                 self.baseModel.tmp_path + "/" + package.name + "/Media/Flyers Inside",
                 self.baseModel.pinupSystem_path + "/POPMedia/" + self.get_product_path(product) + '/GameInfo')
        copytree(self.logger,
                 self.baseModel.tmp_path + "/" + package.name + "/Media/Flyers Front",
                 self.baseModel.pinupSystem_path + "/POPMedia/" + self.get_product_path(product) + '/GameInfo')
        copytree(self.logger,
                 self.baseModel.tmp_path + "/" + package.name + "/Media/Flyers Back",
                 self.baseModel.pinupSystem_path + "/POPMedia/" + self.get_product_path(product) + '/GameInfo')
        copytree(self.logger,
                 self.baseModel.tmp_path + "/" + package.name + "/Media/Loading",
                 self.baseModel.pinupSystem_path + "/POPMedia/" + self.get_product_path(product) + '/Loading')

    def delete(self, table_name: str, product: str):
        self.logger.info("* Delete PinUp Media")

        if not os.path.exists(self.pinupSystem_path):
            self.logger.warning('PinupSystem not found(%s)' % self.pinupSystem_path)
            return
        pop_media = self.baseModel.pinupSystem_path + "/POPMedia/" + self.get_product_path(product)
        if not Path(pop_media).exists():
            raise ValueError('Path not found (%s)' % pop_media + "/" + table_name)

        for file in Path(pop_media).glob('**/%s.*' % table_name):
            self.logger.info("- delete file %s" % file)
            os.remove(file)
