from tkinter import messagebox
from packager.tools.toolbox import *
from pathlib import Path


class UltraDMD:
    def __init__(self, logger, baseModel):
        self.__baseModel=baseModel
        self.__logger=logger


    @property
    def baseModel(self):
        return self.__baseModel

    @property
    def logger(self):
        return self.__logger

    def extract(self, table_name, package):
        tablePath=Path(self.baseModel.visual_pinball_path+"/tables") # TODO: give product choice
        self.logger.info("* UltraDMD files")

        for ultraDMDItem in tablePath.glob('**/*.UltraDMD'):
            ultraDMDDir=str(Path(ultraDMDItem).stem)
            score=searchSentenceInString(ultraDMDDir, table_name)
            self.logger.info("+ Looking for UltraDMD '%s' (score=%02f)" % (Path(ultraDMDItem).stem,score))
            if score>0.2: # a least 2 words found
                result = messagebox.askokcancel("Extract UltraDMD",
                                                "Found %s.UltraDMD directory, get it ?" % Path(ultraDMDItem).stem)
                if result:
                    self.logger.info("+ Ultra DMD is '%s'" % ultraDMDDir)
                    package.set_field('visual pinball/info/ultraDMD', ultraDMDDir)

                    path=tablePath.joinpath(ultraDMDItem)
                    for file in tablePath.joinpath(ultraDMDItem).glob('**/*'):
                        print("File: %s\n" % file)
                        package.add_file(file, 'UltraDMD/content')

    def delete(self, tableName, ultraDMD=None):
        tablePath = Path(self.baseModel.visual_pinball_path + "/tables")  # TODO: give product choice
        self.logger.info("* UltraDMD files")

        if ultraDMD is None:
            for ultraDMDItem in tablePath.glob('**/*.UltraDMD'):
                ultraDMDDir = str(Path(ultraDMDItem).stem)
                score = searchSentenceInString(ultraDMDDir, tableName)
                self.logger.info("+ Looking for UltraDMD '%s' (score=%02f)" % (Path(ultraDMDItem).stem, score))
                if score > 0.2:  # a least 2 words found
                    result = messagebox.askokcancel("Delete UltraDMD",
                                                    "Found %s.UltraDMD directory, delete it ?" % Path(ultraDMDItem).stem)
                    if result:
                        self.logger.info("- Remove Ultra DMD dir '%s'" % ultraDMDDir)
                        # TODO: delete dir
        else:
            self.logger.info("- Remove Ultra DMD dir '%s'" % ultraDMDDir)
            #TODO: delete dir

