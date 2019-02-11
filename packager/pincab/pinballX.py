from packager.tools.toolbox import *
from pathlib import Path

class PinballX:
    def __init__(self, logger, baseModel):
        self.__baseModel=baseModel
        self.__logger=logger

    @property
    def logger(self):
        return self.__logger

    @property
    def pinballX_path(self):
        return self.__baseModel.pinballX_path

    def extract(self, table_name, package):
        if not os.path.exists(self.pinballX_path):
            raise ValueError('PinballX not found (%s)' % self.pinballX_path)

        self.logger.info("* Pinball X files")
        #target_dir = dest_dir + '/' + table_name + '/Media'
        #shutil.rmtree(target_dir, ignore_errors=True)

        for file in Path(self.pinballX_path).glob('**/*%s*' % table_name):
            if "Flyer Images\\Back" in str(file.parent):
                package.add_file(file, 'media/Flyers Back', dstFile=file.stem + ".back" + file.suffix)
            elif "Flyer Images\\Front" in str(file.parent):
                package.add_file(file, 'media/Flyers Front', dstFile=file.stem + ".front" + file.suffix)
            elif "Flyer Images\\Inside1" in str(file.parent):
                package.add_file(file, 'media/Flyers Inside', dstFile=file.stem + ".inside1" + file.suffix)
            elif "Flyer Images\\Inside2" in str(file.parent):
                package.add_file(file, 'media/Flyers Inside', dstFile=file.stem + ".inside2" + file.suffix)
            elif "Flyer Images\\Inside3" in str(file.parent):
                package.add_file(file, 'media/Flyers Inside', dstFile=file.stem + ".inside3" + file.suffix)
            elif "Flyer Images\\Inside4" in str(file.parent):
                package.add_file(file, 'media/Flyers Inside', dstFile=file.stem + ".inside4" + file.suffix)
            elif "Flyer Images\\Inside5" in str(file.parent):
                package.add_file(file, 'media/Flyers Inside', dstFile=file.stem + ".inside5" + file.suffix)
            elif "Flyer Images\\Inside6" in str(file.parent):
                package.add_file(file, 'media/Flyers Inside', dstFile=file.stem + ".inside6" + file.suffix)
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
                package.add_file(file, 'media/Topper')
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
