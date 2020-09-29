from packager.tools.toolbox import *
from packager.model.package import Package
from pathlib import Path


class PinballX:
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
    def pinballX_path(self):
        return self.__baseModel.pinballX_path

    def get_product_path(self, product: str) -> str:
        if product == 'visual pinball':
            return 'Visual Pinball'
        return 'Visual Pinball'

    def extract(self, table_name, package):
        if not os.path.exists(self.pinballX_path):
            self.logger.warning('PinballX not found (%s)' % self.pinballX_path)
            return

        self.logger.info("* Pinball X files")
        for file in Path(self.pinballX_path).glob('**/*%s*' % table_name):
            if "Flyer Images\\Back" in str(file.parent):
                if is_suffix(file, '.back'):
                    package.add_file(file, 'media/Flyers Back', dst_file=file.stem + file.suffix)
                else:
                    package.add_file(file, 'media/Flyers Back', dst_file=file.stem + ".back" + file.suffix)
            elif "Flyer Images\\Front" in str(file.parent):
                if is_suffix(file, '.front'):
                    package.add_file(file, 'media/Flyers Front', dst_file=file.stem + file.suffix)
                else:
                    package.add_file(file, 'media/Flyers Front', dst_file=file.stem + ".front" + file.suffix)
            elif "Flyer Images\\Inside1" in str(file.parent):
                if is_suffix(file, '.inside1'):
                    package.add_file(file, 'media/Flyers Inside', dst_file=file.stem + file.suffix)
                else:
                    package.add_file(file, 'media/Flyers Inside', dst_file=file.stem + ".inside1" + file.suffix)
            elif "Flyer Images\\Inside2" in str(file.parent):
                if is_suffix(file, '.inside2'):
                    package.add_file(file, 'media/Flyers Inside', dst_file=file.stem + file.suffix)
                else:
                    package.add_file(file, 'media/Flyers Inside', dst_file=file.stem + ".inside2" + file.suffix)
            elif "Flyer Images\\Inside3" in str(file.parent):
                if is_suffix(file, '.inside3'):
                    package.add_file(file, 'media/Flyers Inside', dst_file=file.stem + file.suffix)
                else:
                    package.add_file(file, 'media/Flyers Inside', dst_file=file.stem + ".inside3" + file.suffix)
            elif "Flyer Images\\Inside4" in str(file.parent):
                if is_suffix(file, '.inside4'):
                    package.add_file(file, 'media/Flyers Inside', dst_file=file.stem + file.suffix)
                else:
                    package.add_file(file, 'media/Flyers Inside', dst_file=file.stem + ".inside4" + file.suffix)
            elif "Flyer Images\\Inside5" in str(file.parent):
                if is_suffix(file, '.inside5'):
                    package.add_file(file, 'media/Flyers Inside', dst_file=file.stem + file.suffix)
                else:
                    package.add_file(file, 'media/Flyers Inside', dst_file=file.stem + ".inside5" + file.suffix)
            elif "Flyer Images\\Inside6" in str(file.parent):
                if is_suffix(file, '.inside6'):
                    package.add_file(file, 'media/Flyers Inside', dst_file=file.stem + file.suffix)
                else:
                    package.add_file(file, 'media/Flyers Inside', dst_file=file.stem + ".inside6" + file.suffix)
            elif "High Scores\\Visual Pinball" in str(file.parent):
                package.add_file(file, 'media/HighScores')
            elif "Instruction Cards" in str(file.parent):
                package.add_file(file, 'media/Instruction Cards')
            elif "Backglass Images" in str(file.parent):
                package.add_file(file, 'media/Backglass')
            elif "DMD Images" in str(file.parent):
                package.add_file(file, 'media/DMD')
            elif "DMD Videos" in str(file.parent):
                package.add_file(file, 'media/DMDVideos')
            elif "Launch Audio" in str(file.parent):
                package.add_file(file, 'media/AudioLaunch')
            elif "Real DMD Color Videos" in str(file.parent):
                package.add_file(file, 'media/DMD')
            elif "Table Audio" in str(file.parent):
                package.add_file(file, 'media/Audio')
            elif "Table Videos" in str(file.parent):
                package.add_file(file, 'media/TableVideos')
            elif "Topper Images" in str(file.parent):
                package.add_file(file, 'media/Topper')
            elif "Topper Videos" in str(file.parent):
                package.add_file(file, 'media/TopperVideos')
            elif "Table Images" in str(file.parent):
                package.add_file(file, 'media/PlayField')
            elif "Wheel Images" in str(file.parent):
                package.add_file(file, 'media/Wheel')
            elif "Backglass Videos" in str(file.parent):
                package.add_file(file, 'media/Backglass')
            elif "Screen Grabs Backglass" in str(file.parent):
                package.add_file(file, 'media/Backglass')
            elif "Screen Grabs" in str(file.parent):
                package.add_file(file, 'media/ScreenGrabs')
            else:
                self.logger.error("New Case! [%s]" % file)
                break

    def deploy(self, package: Package) -> None:
        self.logger.info("* Deploy Pinball X")

        if not os.path.exists(self.pinballX_path):
            self.logger.warning('PinballX not found (%s)' % self.pinballX_path)
            return

        if not Path(self.baseModel.tmp_path + "/" + package.name).exists():
            raise ValueError('Path not found (%s)' % self.baseModel.tmp_path + "/" + package.name)

        copytree(self.logger,
                 self.baseModel.tmp_path + "/" + package.name + "/Media/Flyers Back",
                 self.baseModel.pinballX_path + "/Media/Flyer Images/Back/")
        copytree(self.logger,
                 self.baseModel.tmp_path + "/" + package.name + "/Media/Flyers Inside",
                 self.baseModel.pinballX_path + "/Media/Flyer Images/Inside1/")
        copytree(self.logger,
                 self.baseModel.tmp_path + "/" + package.name + "/Media/Flyers Front",
                 self.baseModel.pinballX_path + "/Media/Flyer Images/Front/")

        copytree(self.logger,
                 self.baseModel.tmp_path + "/" + package.name + "/Media/Instruction Cards",
                 self.baseModel.pinballX_path + "/Media/Instruction Cards/")
        copytree(self.logger,
                 self.baseModel.tmp_path + "/" + package.name + "/Media/HighScores",
                 self.baseModel.pinballX_path + "/High Scores/Visual Pinball/")
        copytree(self.logger,
                 self.baseModel.tmp_path + "/" + package.name + "/Media/Wheel",
                 self.baseModel.pinballX_path + "/Media/Visual Pinball/Wheel Images/")
        copytree(self.logger,
                 self.baseModel.tmp_path + "/" + package.name + "/Media/Audio",
                 self.baseModel.pinballX_path + "/Media/Visual Pinball/Table Audio/")
        copytree(self.logger,
                 self.baseModel.tmp_path + "/" + package.name + "/Media/AudioLaunch",
                 self.baseModel.pinballX_path + "/Media/Visual Pinball/Launch Audio/")
        copytree(self.logger,
                 self.baseModel.tmp_path + "/" + package.name + "/Media/BackGlass",
                 self.baseModel.pinballX_path + "/Media/Visual Pinball/Backglass Images/")
        copytree(self.logger,
                 self.baseModel.tmp_path + "/" + package.name + "/Media/DMD",
                 self.baseModel.pinballX_path + "/Media/Visual Pinball/DMD Images/")
        copytree(self.logger,
                 self.baseModel.tmp_path + "/" + package.name + "/Media/DMDVideos",
                 self.baseModel.pinballX_path + "/Media/Visual Pinball/DMD Videos/")
        copytree(self.logger,
                 self.baseModel.tmp_path + "/" + package.name + "/Media/PlayField",
                 self.baseModel.pinballX_path + "/Media/Visual Pinball/Table Images")
        copytree(self.logger,
                 self.baseModel.tmp_path + "/" + package.name + "/Media/Topper",
                 self.baseModel.pinballX_path + "/Media/Visual Pinball/Topper Images")
        copytree(self.logger,
                 self.baseModel.tmp_path + "/" + package.name + "/Media/TopperVideos",
                 self.baseModel.pinballX_path + "/Media/Visual Pinball/Topper Videos")
        copytree(self.logger,
                 self.baseModel.tmp_path + "/" + package.name + "/Media/TableVideos",
                 self.baseModel.pinballX_path + "/Media/Visual Pinball/Table Videos")
        copytree(self.logger,
                 self.baseModel.tmp_path + "/" + package.name + "/Media/ScreenGrabs",
                 self.baseModel.pinballX_path + "/Media/Visual Pinball/Screen Grabs")

    def delete(self, table_name: str) -> None:
        if not os.path.exists(self.pinballX_path):
            self.logger.warning('PinballX not found (%s)' % self.pinballX_path)
            return

        self.logger.info("* Pinball X files")
        for file in Path(self.pinballX_path).glob('**/%s.*' % table_name):
            self.logger.info("- delete file %s" % file)
            os.remove(file)
