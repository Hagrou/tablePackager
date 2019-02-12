import os
import shutil

from packager.model.package import Package
from packager.tools.exception import *
from packager.tools.toolbox import *
from pathlib import Path

class VisualPinball:
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
    def visual_pinball_path(self):
        return self.baseModel.visual_pinball_path

    def getRomName(self,tableName):
        if not os.path.exists(self.visual_pinball_path):
            raise ValueError('Visual Pinball not found(%s)' % self.visual_pinball_path)

        vpx_file = Path(self.visual_pinball_path + '/tables/' + tableName + '.vpx')
        return self.extract_rom_name(vpx_file)

    def extract(self, package):
        if not os.path.exists(self.visual_pinball_path):
            raise ValueError('Visual Pinball not found(%s)' % self.visual_pinball_path)

        self.logger.info("* Visual Pinball X files")
        vpx_file        = Path(self.visual_pinball_path + '/tables/' + package.name + '.vpx')
        directb2s_file  = Path(self.visual_pinball_path + "/tables/" + vpx_file.stem + '.directb2s')
        music_file      = Path(self.visual_pinball_path + "/Music/" + vpx_file.stem + '.mp3') # TODO: store music into media/Audio?
        if not os.path.exists(vpx_file):
            raise ValueError('table not found (%s)' % vpx_file)

        rom=self.extract_rom_name(vpx_file)
        if rom=='':
            self.logger.info("- no rom found in vpx file")
        else:
            self.logger.info("+ rom name is '%s'" % rom)
            package.set_field('visual pinball/info/romName', rom)

        package.add_file(vpx_file, 'visual pinball/tables')  # Add vpx file
        if not directb2s_file.exists():                      # Add directb2s file
            self.logger.warning("* no directb2s found")
        else:
            package.add_file(directb2s_file, 'visual pinball/tables')

        if music_file.exists():
            package.add_file(music_file, 'media/Audio')

    def deploy(self, package):
        self.logger.info("* Visual Pinball X files")
        if not os.path.exists(self.visual_pinball_path):
            raise ValueError('Visual Pinball not found(%s)' % self.visual_pinball_path)

        if not Path(self.baseModel.tmp_path+ "/" + package.name).exists():
            raise ValueError('Package Tree not found (%s)' % (self.baseModel.tmp_path+ "/" + package.name))

        copytree(self.logger,
                 self.baseModel.tmp_path+ "/" + package.name+ "/visual pinball/tables",
                 self.baseModel.visual_pinball_path+"/tables")
        return True

    def delete(self, tableName):
        if not os.path.exists(self.visual_pinball_path):
            raise ValueError('Visual Pinball not found(%s)' % self.visual_pinball_path)

        self.logger.info("* Visual Pinball X files")
        vpx_file        = Path(self.visual_pinball_path + '/tables/' + tableName + '.vpx')
        directb2s_file  = Path(self.visual_pinball_path + "/tables/" + vpx_file.stem + '.directb2s')
        music_file      = Path(self.visual_pinball_path + "/Music/" + vpx_file.stem + '.mp3') # TODO: store music into media/Audio?

        if vpx_file.exists():
            self.logger.info("- remove %s file" % vpx_file)
            os.remove(vpx_file)
        if directb2s_file.exists():
            self.logger.info("- remove %s file" % directb2s_file)
            os.remove(directb2s_file)
        if music_file.exists():
            self.logger.info("- remove %s file" % music_file)
            os.remove(music_file)


    def extract_ultraDMD(self, vpx_file): # TODO: deprecated?
        str=extract_string_from_binary_file(vpx_file, br'cAssetsFolder[ ]*=[ ]*"([a-zA-Z0-9_]+)"')
        str =extract_string_from_binary_file(vpx_file, br'TableName[ ]*=[ ]*"([a-zA-Z0-9_]+)"')

    def extract_rom_name(self,vpx_file):
        return extract_string_from_binary_file(vpx_file, br'cGameName[ ]*=[ ]*"([a-zA-Z0-9_]+)"')

    def extract_table_name(self,vpx_file):
        return extract_string_from_binary_file(vpx_file, br'TableName[ ]*=[ ]*"([a-zA-Z0-9_]+)"')
