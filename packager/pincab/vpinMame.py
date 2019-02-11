from packager.tools.toolbox import *


class VPinMame:
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

    def extract(self, package): # TODO: give the choice of product
        romName=package.get_field('visual pinball/info/romName')
        if romName == '': # nothing to do
            return
        self.logger.info("* VPinMame files '%s'" % romName)

        for rom_file in Path(self.visual_pinball_path+'/VPinMAME').glob('**/*%s*' % romName):
            if "cfg" in str(rom_file.parent):  # .cfg
                package.add_file(rom_file, 'VPinMAME/cfg')
            elif "nvram" in str(rom_file.parent):  # .nv
                package.add_file(rom_file, 'VPinMAME/nvram')
            elif "roms" in str(rom_file.parent):  # .zip
                package.add_file(rom_file, 'VPinMAME/roms')
            elif "memcard" in str(rom_file.parent):  # .prt
                package.add_file(rom_file, 'VPinMAME/memcard')
            else:
                self.logger.error("New Case!!! [%s]" % rom_file)
                exit(1)  # TODO: remove it


    def deploy(self,package): # TODO: give the choice of product
        self.logger.info("* VPinMame files")
        if not Path(self.baseModel.tmp_path + "/" + package.name).exists():
            raise ValueError('path not found (%s)' % (self.baseModel.tmp_path + "/" + package.name))

        copytree(self.logger,
                 self.baseModel.tmp_path + "/" + package.name + "/VPinMAME",
                 self.baseModel.visual_pinball_path + "/VPinMAME")

    def delete(self, tableName, romName): # TODO: give the choice of product
        if romName == '': # nothing to do
            return
        self.logger.info("* VPinMame files '%s'" % romName)

        for rom_file in Path(self.visual_pinball_path+'/VPinMAME').glob('**/*%s*' % romName):
            self.logger.info("- remove %s file" % rom_file)
