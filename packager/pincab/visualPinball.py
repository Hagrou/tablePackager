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
            raise Directb2sException(vpx_file.stem)
        package.add_file(directb2s_file, 'visual pinball/tables')

        # looking for ultra dmd
        """
        isUltraDMD = self.extract_ultraDMD(vpx_file)
        if isUltraDMD == '':
            self.logger.info("- no ultra DMD in vpx file")
        else:
            self.logger.info("+ ultra DMD found '%s'" % (isUltraDMD))
        """
        # search table name in vpx
        table_name = self.extract_table_name(vpx_file) # TODO: implement ultradmd case
        if table_name is not None:
            # TODO: Check SetController = CreateObject("DMD Object")
            if Path(self.visual_pinball_path + "/tables/" + table_name + '.UltraDMD').exists():
                self.logger.info("+ UltraDMD files found %s" % self.visual_pinball_path + "/tables/" + table_name + '.UltraDMD')

                #shutil.copytree(self.visual_pinball_path + "/tables/" + table_name + '.UltraDMD',
                #                target_dir + "visual pinball/tables" + table_name + '.UltraDMD')
                raise PackageException("UltraDMD found but not implemented")

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


    def import_table_file(self, table_file, target_dir, content, dstName=None): # TODO: deprecated?
        if dstName!=None:
            mkdir_and_rename(self.logger, Path(table_file), dstName, target_dir+'/visual pinball', 'tables',content['visual pinball'])
        else:
            mkdir_and_copy_file(self.logger, Path(table_file), target_dir+'/visual pinball', 'tables',content['visual pinball'])

    def remove_table_file(self, table_file, target_dir, content): # TODO: deprecated?
        path=target_dir+'/visual pinball/tables/'+table_file
        os.remove(path)

    def extract_ultraDMD(self, vpx_file): # TODO: deprecated?
        return extract_string_from_binary_file(vpx_file, br'(UltraDMD.DMDObject)')

    def extract_rom_name(self,vpx_file):
        return extract_string_from_binary_file(vpx_file, br'cGameName[ ]*=[ ]*"([a-zA-Z0-9_]+)"')

    def extract_table_name(self,vpx_file):
        return extract_string_from_binary_file(vpx_file, br'TableName[ ]*=[ ]*"([a-zA-Z0-9_]+)"')
