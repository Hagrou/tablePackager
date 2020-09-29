import logging
import os
import collections
import json
import shutil
import os.path
import time
from pathlib import *
from pprint import pprint
import datetime

from packager.tools.exception import *
from packager.tools.toolbox import *
from packager.tablePackager import *


class Manifest:
    def __init__(self, name: str, package_version:str) -> None:
        self.__content = collections.OrderedDict()
        self.__name = name
        self.__package_version = package_version

    @property
    def content(self):
        return self.__content

    @property
    def name(self) -> str:
        return self.__name

    @property
    def package_version(self) -> str:
        return self.__package_version

    @property
    def filename(self) -> str:
        return self.name + '.manifest.json'

    def __str__(self):
        return pprint(self.__content)

    def new(self) -> None:
        self.content['info'] = collections.OrderedDict()
        self.content['info']['package name'] = self.name
        self.content['info']['package version'] = self.package_version
        self.content['info']['creation date'] = utcTime2IsoStr()
        self.content['info']['lastmod'] = self.content['info']['creation date']

        self.content['info']['version'] = ''
        self.content['info']['table designer(s)'] = ''
        self.content['info']['manufacturer'] = ''
        self.content['info']['table name'] = ''
        self.content['info']['year'] = ''
        self.content['info']['theme'] = ''
        self.content['info']['protected'] = 'False'

        self.content['visual pinball'] = collections.OrderedDict()
        self.content['visual pinball']['tables'] = []
        self.content['visual pinball']['info'] = collections.OrderedDict()
        self.content['visual pinball']['info']['romName'] = ''

        self.content['UltraDMD'] = collections.OrderedDict()
        self.content['UltraDMD']['content'] = []

        self.content['VPinMAME'] = collections.OrderedDict()
        self.content['VPinMAME']['cfg'] = []
        self.content['VPinMAME']['nvram'] = []
        self.content['VPinMAME']['roms'] = []
        self.content['VPinMAME']['memcard'] = []

        self.content['media'] = collections.OrderedDict()
        self.content['media']['Flyers Front'] = []
        self.content['media']['Flyers Back'] = []
        self.content['media']['Flyers Inside'] = []
        self.content['media']['Instruction Cards'] = []
        self.content['media']['HighScores'] = []
        self.content['media']['Backglass'] = []
        self.content['media']['PlayField'] = []
        self.content['media']['Wheel'] = []
        self.content['media']['DMD'] = []
        self.content['media']['DMDVideos'] = []
        self.content['media']['TableVideos'] = []
        self.content['media']['Audio'] = []
        self.content['media']['AudioLaunch'] = []
        self.content['media']['Topper'] = []
        self.content['media']['ScreenGrabs'] = []
        self.content['media']['TopperVideos'] = []  # new 1.1
        self.content['media']['Loading'] = []  # new 1.2

    def open(self, path: Path, installed: bool = False) -> None:
        if not os.path.exists(path):
            raise PackageException("Manifest not found at %s" % path)
        try:
            if installed:
                manifest_path = path + '/' + self.filename  # search manifest in installed table dir
            else:
                manifest_path = path + '/' + self.name + '/' + self.filename
            with open(manifest_path) as data_file:
                self.__content = json.load(data_file, object_pairs_hook=collections.OrderedDict)
        except:
            raise PackageException("Manifest not found at %s" % (path + '/' + self.name + '/' + self.filename))

    def save(self, path: Path) -> None:
        self.set_field('info/lastmod', utcTime2IsoStr())  # update last modification date
        try:
            with open(path + '/' + self.name + '/' + self.filename, 'w') as outfile:
                json.dump(self.__content, outfile)
        except IOError as e:
            raise PackageException("Manifest write error %s" % str(e))

    def save_as(self, path: Path, name: str) -> None:
        self.set_field('info/lastmod', utcTime2IsoStr())  # update last modification date
        try:
            with open(path + '/' + self.name + '/' + name + '.manifest.json', 'w') as outfile:
                json.dump(self.__content, outfile)
        except IOError as e:
            raise PackageException("Manifest write error %s" % str(e))

    def rename(self, path: Path, name: str) -> None:
        os.unlink(path + '/' + self.name + '/' + self.filename)
        self.save_as(path, name)
        self.__name = name

    def set_field(self, field_path: str, value) -> None:
        content = self.__content
        field_list = field_path.split('/')
        for field in field_list[:-1]:
            content = content[field]
        content[field_list[-1]] = value

    def get_field(self, field_path: str):
        content = self.__content
        field_list = field_path.split('/')
        for field in field_list[:-1]:
            if field == '': continue
            content = content[field]
        return content[field_list[-1]]

    def exists_field(self, field_path: str) -> bool:
        content = self.__content
        field_list = field_path.split('/')
        for field in field_list:
            if not content.get(field):
                return False
            content = content[field]
        return True

    def get_file(self, field_path: str, filename: str):
        content = self.__content
        field_list = field_path.split('/')
        for field_type in field_list:
            content = content[field_type]
        for file in content:
            if file['file']['name'] == filename:
                return file, content
        return None, None

    def prev_file_data_path(self, field_path: str, filename: str):
        prev_file = ''

        field_list = field_path.split('/')
        content = self.__content

        for key1, val1 in content.items():
            if key1 == 'info': continue
            for key2, val2 in content[key1].items():
                if key1 == field_list[0] and key2 == field_list[1]:
                    return prev_file
                if key2 == 'info': continue
                prev_file = key1 + '/' + key2
        return prev_file

    def next_file_data_path(self, field_path: str, filename: str):
        next_file = ''

        field_list = field_path.split('/')
        content = self.__content

        for key1, val1 in reversed(list(content.items())):
            if key1 == 'info': continue
            for key2, val2 in reversed(list(content[key1].items())):
                if key1 == field_list[0] and key2 == field_list[1]:
                    return next_file
                if key2 == 'info': continue
                next_file = key1 + '/' + key2
        return next_file

    def exists_file(self, field_path: str, filename: str) -> bool:
        (file, content) = self.get_file(field_path, filename)
        if file is not None:
            return True
        return False

    def del_file(self, field_path: str, filename: str) -> bool:
        (file, content) = self.get_file(field_path, filename)
        if file is not None:
            content.remove(file)
            return True
        return False

    def add_file_info(self, field_path: str, file: dict):
        field_list = field_path.split('/')
        content = self.__content
        for field_type in field_list:
            if field_type == '':
                continue
            content = content[field_type]
        content.append({'file': file})

    def add_file(self, field_path: str, full_path_src_file: str):
        manifest_file = None

        # check if file is already set in manifest
        (file, content) = self.get_file(field_path, Path(full_path_src_file).name)
        if file is not None:
            # compare sha1
            sha1=sha1sum(full_path_src_file)
            if file['file']['sha1'] != sha1:
                logging.warning("! file '%s/%s' changed" % (Path(full_path_src_file).name, field_path))
                file['file']['lastmod'] = mtime2IsoStr(os.path.getmtime(full_path_src_file))  # last modification date
                file['file']['size'] = os.path.getsize(full_path_src_file)
                file['file']['sha1'] = sha1
            return

        file = collections.OrderedDict()
        file['name'] = Path(full_path_src_file).name
        file['size'] = os.path.getsize(full_path_src_file)
        file['sha1'] = sha1sum(full_path_src_file)
        file['author(s)'] = ''
        file['version'] = ''
        file['url'] = ''
        file['lastmod'] = mtime2IsoStr(os.path.getmtime(full_path_src_file))  # last modification date

        field_list = field_path.split('/')
        content = self.__content
        for field_type in field_list:
            content = content[field_type]
        content.append({'file': file})

    def move_file(self, src_file: str, src_field_path: str, dst_field_path: str) -> None:
        (file, content) = self.get_file(src_field_path, src_file)
        if file is None:
            return

        content.remove(file)
        field_list = dst_field_path.split('/')
        content = self.__content
        for type in field_list:
            content = content[type]
        content.append(file)

    def rename_file(self, field_path: str, src_file: str, dst_file: str) -> bool:
        (file, content) = self.get_file(field_path, src_file)
        if file is not None:
            file['file']['name'] = dst_file
            return True
        return False

    def get_first_image(self) -> (str, str):
        content = self.__content
        for key, values in content['media'].items():
            if key == 'info': continue
            for value in values:
                if value.get('file'):
                    if Path(value['file']['name']).suffix == '.png' or Path(value['file']['name']).suffix == '.jpg':
                        return 'media/' + key, value['file']['name']
        return None, None


class Package:
    def __init__(self, baseModel, name):
        self.__baseModel = baseModel
        self.__name = name
        self.__directory = None
        self.__manifest = None

    @property
    def manifest(self) -> Manifest:
        return self.__manifest

    @property
    def name(self) -> str:
        return self.__name

    @property
    def directory(self):
        return self.__directory

    @property
    def baseModel(self):
        return self.__baseModel

    @property
    def logger(self):
        return self.baseModel.logger

    # create empty package
    def new(self, package_dir):
        self.__directory = package_dir
        self.__manifest = Manifest(self.name, self.baseModel.package_version)
        self.__manifest.new()  # create empty package
        self.build_tree(self.directory + '/' + self.name, self.manifest.content)
        self.__manifest.save(self.directory)

    """
    Open and read directory package
    """

    def open(self, base_dir):
        if not os.path.exists(base_dir):
            raise PackageException("Package not found at %s" % base_dir)
        self.__directory = base_dir
        self.__manifest = Manifest(self.__name, self.baseModel.package_version)
        self.manifest.open(self.__directory)
        self.check_package()

    def check_package(self) -> None:
        if not os.path.exists(self.directory):
            raise PackageException("Package not found at %s" % self.directory)

        file_in_error = self.check_files(self.manifest.content, self.directory + '/' + self.name, '')
        for (field_path, filename) in file_in_error:
            self.logger.info("Fix Package Manifest for %s/%s" % (field_path, filename))
            self.__manifest.del_file(field_path.strip('/'), filename)

        self.upgrade_package()

    def upgrade_package(self):
        major_packager_version = int(self.manifest.get_field('info/package version').split('.')[0])
        minor_packager_version = int(self.manifest.get_field('info/package version').split('.')[1])

        if major_packager_version == 1 and (minor_packager_version == 0 or minor_packager_version == 1):
            self.logger.info("Upgrade Package to 1.2 (topper/topper videos)")
            self.manifest.content['media']['TopperVideos'] = []
            self.manifest.content['info']['version'] = ''
            if not os.path.exists(self.directory + '/' + self.name + '/media/TopperVideos'):
                os.makedirs(self.directory + '/' + self.name + '/media/TopperVideos')
            self.manifest.content['media']['Loading'] = []
            if not os.path.exists(self.directory + '/' + self.name + '/media/Loading'):
                os.makedirs(self.directory + '/' + self.name + '/media/Loading')
            self.manifest.set_field('info/package version', '1.2')

    def check_files(self, content, origin_path:str, file_path:str) -> list:
        error_list = []
        if self.__directory is None or self.__manifest is None:
            raise PackageException("Package must be openned")

        for key, value in content.items():
            if key == 'info':
                continue
            elif key == 'file':
                if not os.path.exists(origin_path + '/' + file_path + '/' + value['name']):
                    self.logger.warning('File %s not found in package', file_path + '/' + value['name'])
                    error_list.append((file_path, value['name']))
            elif isinstance(value, dict):
                error_list = error_list + self.check_files(content[key], origin_path, file_path + '/' + key)
            elif type(value) is list:
                for item in value:
                    if isinstance(item, dict):
                        error_list = error_list + self.check_files(item, origin_path, file_path + '/' + key)

        return error_list

    def merge_files(self, content, origin_path: str, file_path: str) -> list:
        error_list = []
        if self.__directory is None or self.__manifest is None:
            raise PackageException("Package must be opened")

        for key, fields in content.items():
            if key == 'info':
                for field_name, value in fields.items():
                    path = 'info/' + field_name  # TODO:del
                    print("merge_files: %s=%s" % (path, value))  # TODO:del
                    if field_name != 'packager version' and field_name != 'package version':
                        self.manifest.set_field('info/' + field_name,
                                                value)  # copy all fields except packager version and package version
            elif key == 'file':
                file = collections.OrderedDict()
                for field_name, value in fields.items():
                    file[field_name] = value
                self.manifest.add_file_info(file_path, file)  # copy file info to new manifest
            elif isinstance(fields, dict):
                error_list = error_list + self.merge_files(content[key], origin_path, file_path + '/' + key)
            elif type(fields) is list:
                for item in fields:
                    if isinstance(item, dict):
                        error_list = error_list + self.merge_files(item, origin_path, file_path + '/' + key)

        return error_list

    def merge(self, installed: bool = False) -> None:
        # read installed manifest
        installed_manifest = Manifest(self.__name, self.baseModel.package_version)
        installed_manifest.open(self.__baseModel.installed_path, installed)

        self.merge_files(installed_manifest.content, self.directory + '/' + self.name, '')
        self.manifest.set_field('info/lastmod', utcTime2IsoStr())  # update last modification date

    def update(self) -> None:
        if not os.path.exists(self.directory):
            raise PackageException("Package not found at %s" % self.directory)
        self.manifest.open(self.__directory)

    def save(self) -> None:
        self.manifest.save(self.__directory)

    def rename_files(self, new_name, path, content):
        for key, value in content.items():
            if key == 'info':
                continue
            elif key == 'file':
                if value['name'].startswith(self.name, 0, len(self.name)):
                    self.logger.info("+ rename file '%s'" % (path + '/' + value['name']))
                    os.rename(self.directory + '/' + self.name + '/' + path + '/' + value['name'],
                              self.directory + '/' + self.name + '/' + path + '/' + value['name'].replace(self.name,
                                                                                                          new_name))
                    value['name'] = value['name'].replace(self.name, new_name)

            elif isinstance(value, dict):
                self.rename_files(new_name, path + '/' + key, content[key])
            elif type(value) is list:
                for item in value:
                    if isinstance(item, dict):
                        self.rename_files(new_name, path + '/' + key, item)

    def rename_package(self, new_name: str) -> None:
        if not os.path.exists(self.directory):
            raise PackageException("Package not found at %s" % self.directory)

        self.rename_files(new_name, '', self.manifest.content)

        self.manifest.rename(self.directory, new_name)
        self.logger.info("+ rename directory  '%s'" % (self.name))

        os.rename(self.directory + '/' + self.name,
                  self.directory + '/' + new_name)
        self.__name = new_name

    def build_tree(self, baseDir, content):
        if type(content) is list:
            return
        for item in content:
            if item == 'info': continue
            os.makedirs(baseDir + '/' + item, exist_ok=True)
            self.build_tree(baseDir + '/' + item, content[item])

    def set_field(self, field_path, value):
        self.manifest.set_field(field_path, value)

    def get_field(self, field_path):
        return self.manifest.get_field(field_path)

    def exists_field(self, field_path):
        return self.manifest.exists_field(field_path)

    def collision_detector(self, src_file: str, dst_file: str, check_sha1: bool = False) -> (Path, bool):
        id_file = 1
        is_same_file = False

        orig_name = Path(dst_file).stem
        orig_suffix = Path(dst_file).suffix
        while os.path.exists(dst_file):  # check if dst file already exists
            if check_sha1:
                if sha1sum(dst_file) == sha1sum(src_file):  # same files, overwrite it
                    is_same_file = True
                    break

            parent = Path(dst_file).parent
            stem = Path(dst_file).stem
            suffix = Path(dst_file).suffix
            dst_file = parent.joinpath(orig_name + ('.%d' % id_file) + orig_suffix)
            id_file = id_file + 1

        return Path(dst_file).name, is_same_file

    def add_file(self, full_path_src_file: str, dst_field_path, dst_file: str = None):
        try:
            if not os.path.exists(full_path_src_file):
                raise PackageException("File not found at '%s'" % full_path_src_file)

            if dst_file is None:
                dst_file = Path(full_path_src_file).name
            (dst_file, isSameFile) = self.collision_detector(full_path_src_file,
                                                             self.directory + '/' + self.name + '/' + dst_field_path + '/' + dst_file,
                                                             check_sha1=True)
            self.logger.info("+ add '%s' -> '%s'" % (full_path_src_file, dst_field_path + '/' + dst_file))

            shutil.copy(full_path_src_file, self.directory + '/' + self.name + '/' + dst_field_path + '/' + dst_file)
            self.manifest.add_file(dst_field_path,
                                   self.directory + '/' + self.name + '/' + dst_field_path + '/' + dst_file)
            self.save()
        except OSError as e:
            self.logger.error(str(e))
            raise e

    def remove_file(self, src_file: str, field_path: str):
        self.logger.info("+ remove '%s'" % (field_path + '/' + src_file))
        try:
            os.unlink(self.directory + '/' + self.name + '/' + field_path + '/' + src_file)
            self.manifest.del_file(field_path, src_file)
            self.save()
        except OSError as e:
            self.logger.error(str(e))
            raise e

    def rename_file(self, srcFile, field_path, dstFile):
        self.logger.info("+ rename '%s' -> '%s'" % (field_path + '/' + srcFile,
                                                    field_path + '/' + dstFile))
        try:
            os.rename(self.directory + '/' + self.name + '/' + field_path + '/' + srcFile,
                      self.directory + '/' + self.name + '/' + field_path + '/' + dstFile)
            self.manifest.rename_file(field_path, srcFile, dstFile)
            self.save()
        except OSError as e:
            self.logger.error(str(e))
            raise e

    def move_file(self, src_file, src_field_path, dst_field_path):
        self.logger.info("+ move '%s' -> '%s'" % (src_field_path + '/' + src_file,
                                                  dst_field_path + '/' + src_file))

        (dstFile, _) = self.collision_detector(self.directory + '/' + self.name + '/' + src_field_path + '/' + src_file,
                                               self.directory + '/' + self.name + '/' + dst_field_path + '/' + src_file,
                                               check_sha1=False)

        try:
            shutil.move(self.directory + '/' + self.name + '/' + src_field_path + '/' + src_file,
                        self.directory + '/' + self.name + '/' + dst_field_path + '/' + dstFile)
            if src_file != dstFile:
                self.manifest.rename_file(src_field_path, src_file, dstFile)
                src_file = dstFile

            self.manifest.move_file(src_file, src_field_path, dst_field_path)  # !! move_file -> same name
            self.save()
        except OSError as e:
            self.logger.error(str(e))
            raise e

    # zip package
    def pack(self) -> None:
        self.logger.info("* packing table '%s'" % (self.name + self.baseModel.package_extension))
        pack(self.directory + '/' + self.name,
             self.directory,
             self.name + self.baseModel.package_extension)

    # unzip package
    def unpack(self) -> None:
        self.logger.info("* unpack table '%s'" % (self.name + self.baseModel.package_extension))
        clean_dir(self.baseModel.tmp_path)
        unpack(self.baseModel.package_path + '/' + self.name + self.baseModel.package_extension,
               self.baseModel.tmp_path)

    def exists_file(self, typePath: str, filename: str) -> bool:
        return self.manifest.exists_file(typePath, filename)

    def get_first_image(self):
        return self.manifest.get_first_image()
