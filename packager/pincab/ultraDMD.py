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
                        package.add_file(file, 'UltraDMD/content')

    def deploy(self, package):
        if not os.path.exists(self.baseModel.visual_pinball_path):
            raise ValueError('Visual Pinball not found(%s)' % self.baseModel.visual_pinball_path)

        if not Path(self.baseModel.tmp_path+ "/" + package.name).exists():
            raise ValueError('Package Tree not found (%s)' % (self.baseModel.tmp_path+ "/" + package.name))

        if not package.exists_field('visual pinball/info/ultraDMD'):
            self.logger.info("* No Ultra DMD files")
            return True

        self.logger.info("* Ultra DMD files")
        ultraDMD=package.get_field('visual pinball/info/ultraDMD')

        copytree(self.logger,
                 self.baseModel.tmp_path+ "/" + package.name+ "/UltraDMD/content",
                 self.baseModel.visual_pinball_path+"/tables/"+ultraDMD+".UltraDMD")
        return True

    def delete(self, tableName, dirName=None):
        tablePath = Path(self.baseModel.visual_pinball_path + "/tables")  # TODO: give product choice
        self.logger.info("* UltraDMD files")

        if dirName is None:
            for ultraDMDItem in tablePath.glob('**/*.UltraDMD'):
                ultraDMDDir = str(Path(ultraDMDItem).stem)
                score = searchSentenceInString(ultraDMDDir, tableName)
                self.logger.info("+ Looking for UltraDMD '%s' (score=%02f)" % (Path(ultraDMDItem).stem, score))
                if score > 0.2:  # a least 2 words found
                    result = messagebox.askokcancel("Delete UltraDMD",
                                                    "Found %s.UltraDMD directory, delete it ?" % Path(ultraDMDItem).stem)
                    if result:
                        self.logger.info("- Remove Ultra DMD dir '%s'" % ultraDMDDir)
                        shutil.rmtree(dirName)
        else:
            self.logger.info("- Remove Ultra DMD dir '%s'" % dirName)
            delPath=self.baseModel.visual_pinball_path + '/tables/'+dirName+'.UltraDMD'
            shutil.rmtree(delPath)


