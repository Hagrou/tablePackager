import re
import mmap
import json
from packager.tools import Directb2sException
from packager.tools import RomException

import os
import shutil
import logging
from pathlib import Path

class Extractor:
    def __init__(self, database,  visual_pinball_path, pinballX_path):
        self.__database=database
        self.__visual_pinball_path=visual_pinball_path
        self.__pinballX_path=pinballX_path
        self.__manifest={}
        if not os.path.exists(self.__visual_pinball_path):
            raise ValueError('Visual Pinball not found(%s)' % self.__visual_pinball_path)

        if not os.path.exists(self.__pinballX_path):
            raise ValueError('PinballX not found (%s)' % self.__pinballX_path)

    def copy_installed_tables_files(self, dest_dir):
        dbTable = None
        for vpx_file in Path(self.__visual_pinball_path + "/pincab").glob('**/*.vpx'):
            try:
                content = {}
                dbTable = self.search_table(vpx_file.stem)

                logging.debug("* Found Table %s (database: %s)" % (vpx_file,dbTable.get('Table Name (Manufacturer Year)')))

                content['visual pinball'] = self.copy_visual_pinball_files(dest_dir, vpx_file,dbTable)
                content['pinballX'] = self.copy_pinballX_files(dest_dir, vpx_file)

                with open(dest_dir+'/'+vpx_file.stem+'/'+vpx_file.stem+'.json', 'w') as outfile:
                    json.dump(content, outfile)
                logging.info("Extraction %s Done" % vpx_file)

            except Directb2sException as error:
                url=self.__database.get_directBS2_url(dbTable)
                logging.fatal("No directb2s found for table %s \n(you can download it at %s)" % (error.table,url))
                break

            except RomException as error:
                logging.fatal("No rom (%s) found for table %s" % (error.rom, error.table))
                url=self.__database.get_colored_rom_url(dbTable)
                if len(url)>0:
                    logging.fatal("(you can download colored rom at %s)" % (url))
                url = self.__database.get_native_rom_url(dbTable)
                if len(url)>0:
                    logging.fatal("(you can download native rom at %s)" % (url))
                break

    def search_table(self,name):
        dbTable = self.__database.search(name)
        if dbTable is not None:
            return dbTable

        dbTable = self.__database.search_fuzzy(name)
        logging.info('Table %s not found in database, try with %s' % (name, dbTable.get('Table Name (Manufacturer Year)')))
        return dbTable

    def copy_visual_pinball_files(self, dest_dir, vpx_file,dbTable):
        content = {}
        table_name = extract_table_name(vpx_file)
        if table_name is None:
            logging.debug("\tno table name found for %s", vpx_file)

        isUltraDMD = extract_ultraDMD(vpx_file)

        target_dir = dest_dir + "/" + vpx_file.stem + "/Visual Pinball/"
        shutil.rmtree(target_dir, ignore_errors=True)
        mkdir_and_copy_file2(vpx_file, target_dir, "pincab", content)

        # TODO: Check SetController = CreateObject("B2S.Server")
        if Path(self.__visual_pinball_path + "/pincab/" + vpx_file.stem + '.directb2s').exists():
            logging.debug("\tdirectb2s file found %s" % self.__visual_pinball_path + "/pincab/" + vpx_file.stem + '.directb2s')
            mkdir_and_copy_file2(Path(self.__visual_pinball_path + "/pincab/" + vpx_file.stem + '.directb2s'), target_dir,
                                 "pincab", content)
        else:
            raise Directb2sException(vpx_file.stem)

        if table_name is not None:
            # TODO: Check SetController = CreateObject("DMD Object")
            if Path(self.__visual_pinball_path + "/pincab/" + table_name + '.UltraDMD').exists():
                logging.info("\tUltraDMD files found %s" % self.__visual_pinball_path + "/pincab/" + table_name + '.UltraDMD')
                shutil.copytree(self.__visual_pinball_path + "/pincab/" + table_name + '.UltraDMD',
                                target_dir + "Tables/" + table_name + '.UltraDMD')
                content['pincab'].append(table_name + '.UltraDMD')
            elif isUltraDMD:
                print("UtlraDMD not found!!!!")
                exit()

        if Path(self.__visual_pinball_path + "/Music/" + vpx_file.stem + '.mp3').exists():
            shutil.copy(self.__visual_pinball_path + "/Music/" + vpx_file.stem + '.mp3', target_dir + "/Visual Pinball/Music")
            mkdir_and_copy_file2(Path(self.__visual_pinball_path + "/Music/" + vpx_file.stem + '.mp3'), target_dir,
                                 '/Visual Pinball/Music/' + vpx_file.stem + '.mp3', content)

        romName = extract_rom_name(vpx_file)
        isRomFound=False
        logging.debug("\tRom File %s" % romName)
        for rom_file in Path(self.__visual_pinball_path).glob('**/*%s*' % romName):
            logging.debug("\tRom %s found [%s]" % (rom_file, rom_file.parent))
            if "cfg" in str(rom_file.parent):  # .cfg
                mkdir_and_copy_file2(rom_file, target_dir, "VPinMAME/cfg", content)
            elif "nvram" in str(rom_file.parent):  # .nv
                mkdir_and_copy_file2(rom_file, target_dir, "VPinMAME/nvram", content)
            elif "roms" in str(rom_file.parent):  # .zip
                mkdir_and_copy_file2(rom_file, target_dir, "VPinMAME/roms", content)
                isRomFound=True
            elif "memcard" in str(rom_file.parent):  # .prt
                mkdir_and_copy_file2(rom_file, target_dir, "VPinMAME/memcard", content)
            elif "User" in str(rom_file.parent):  # .txt # TODO: move outside
                mkdir_and_copy_file2(rom_file, target_dir, "VPinMAME/User", content)
            else:
                if "Music" in str(rom_file.parent) or "directb2s" in str(rom_file) or "vpx" in str(rom_file) or "UltraDMD" in str(rom_file):
                    logging.warning("skip %s" % rom_file)
                else:
                    logging.error("New Case!!! [%s]" % rom_file)
                    exit(1)
        if not isRomFound:
            if self.__database.is_rom_required(dbTable):
                raise RomException(vpx_file.stem,romName)
            else:
                logging.info('\tNo rom required !?')
        return content

    def copy_pinballX_files(self, dest_dir, vpx_file):
        content={}
        target_dir = dest_dir + "/" + vpx_file.stem +"/pinballX/"
        shutil.rmtree(target_dir, ignore_errors=True)
        for file in Path(self.__pinballX_path).glob('**/*%s*' % vpx_file.stem):
            if "Flyer Images\\Back" in str(file.parent):
                mkdir_and_copy_file2(file, target_dir,"Media/Flyer Images/Back", content)
            elif "Flyer Images\\Front" in str(file.parent):
                mkdir_and_copy_file2(file, target_dir,"Media/Flyer Images/Front",content)
            elif "Flyer Images\\Inside1" in str(file.parent):
                mkdir_and_copy_file2(file, target_dir,"Media/Flyer Images/Inside1",content)
            elif "Flyer Images\\Inside2" in str(file.parent):
                mkdir_and_copy_file2(file, target_dir,"Media/Flyer Images/Inside2",content)
            elif "Flyer Images\\Inside3" in str(file.parent):
                mkdir_and_copy_file2(file, target_dir,"Media/Flyer Images/Inside3",content)
            elif "Flyer Images\\Inside4" in str(file.parent):
                mkdir_and_copy_file2(file, target_dir,"Media/Flyer Images/Inside4",content)
            elif "Flyer Images\\Inside5" in str(file.parent):
                mkdir_and_copy_file2(file, target_dir,"Media/Flyer Images/Inside5",content)
            elif "Flyer Images\\Inside6" in str(file.parent):
                mkdir_and_copy_file2(file, target_dir,"Media/Flyer Images/Inside6",content)
            elif "High Scores\\Visual Pinball" in str(file.parent):
                mkdir_and_copy_file2(file, target_dir,"High Scores\\Visual Pinball",content)
            elif "Instruction Cards" in str(file.parent):
                mkdir_and_copy_file2(file, target_dir,"Media/Instruction Cards",content)
            elif "Backglass Images" in str(file.parent):
                mkdir_and_copy_file2(file, target_dir,"Media/Visual Pinball/Backglass Images",content)
            elif "DMD Images" in str(file.parent):
                mkdir_and_copy_file2(file, target_dir,"Media/Visual Pinball/DMD Images",content)
            elif "DMD Videos" in str(file.parent):
                mkdir_and_copy_file2(file, target_dir,"Media/Visual Pinball/DMD Videos",content)
            elif "Launch Audio" in str(file.parent):
                mkdir_and_copy_file2(file, target_dir,"Media/Visual Pinball/Launch Audio",content)
            elif "Real DMD Color Videos" in str(file.parent):
                mkdir_and_copy_file2(file, target_dir,"Media/Visual Pinball/Real DMD Color Videos",content)
            elif "Table Audio" in str(file.parent):
                mkdir_and_copy_file2(file, target_dir,"Media/Visual Pinball/Table Audio",content)
            elif "Table Videos" in str(file.parent):
                mkdir_and_copy_file2(file, target_dir,"Media/Visual Pinball/Table Videos",content)
            elif "Topper Images" in str(file.parent):
                mkdir_and_copy_file2(file, target_dir,"Media/Visual Pinball/Topper Images",content)
            elif "Topper Videos" in str(file.parent):
                mkdir_and_copy_file2(file, target_dir,"Media/Visual Pinball/Topper Videos",content)
            elif "Table Images" in str(file.parent):
                mkdir_and_copy_file2(file, target_dir,"Media/Visual Pinball/Table Images",content)
            elif "Wheel Images" in str(file.parent):
                mkdir_and_copy_file2(file, target_dir,"Media/Visual Pinball/Wheel Images",content)
            elif "Backglass Videos" in str(file.parent):
                mkdir_and_copy_file2(file, target_dir,"Media/Visual Pinball/Backglass Videos",content)
            elif "Screen Grabs Backglass" in str(file.parent):
                mkdir_and_copy_file2(file, target_dir,"Media/Visual Pinball/Screen Grabs Backglass",content)
            elif "Screen Grabs" in str(file.parent):
                mkdir_and_copy_file2(file, target_dir,"Media/Visual Pinball/Screen Grabs",content)
            else:
                logging.error("New Case! [%s]" % file)
                exit(1)
        return content

def mkdir_and_copy_file2(src,target,dest, content):
    os.makedirs(target+'/'+dest, exist_ok=True)
    shutil.copy(src, target+'/'+dest+'/%s' % (src.name))
    if content.get(dest) is None:
        content[dest]=['%s' % src.name]
    else:
        content[dest].append('%s' % src.name)




def extract_ultraDMD(vpx_file):
    return extract_string_from_file(vpx_file, br'(UltraDMD.DMDObject)')

def extract_rom_name(vpx_file):
    return extract_string_from_file(vpx_file, br'cGameName[ ]*=[ ]*"([a-zA-Z0-9_]+)"')

def extract_table_name(vpx_file):
    return extract_string_from_file(vpx_file, br'TableName[ ]*=[ ]*"([a-zA-Z0-9_]+)"')

def extract_string_from_file(vpx_file, pattern):
    p=re.compile(pattern)
    with open(vpx_file, 'rb', 0) as file, mmap.mmap(file.fileno(), 0, access=mmap.ACCESS_READ) as s:
        m=p.search(s)
        if m is None:
            return None
        logging.debug("\tstring found %s" % m.group(0))
        return m.group(1).decode('ascii')




