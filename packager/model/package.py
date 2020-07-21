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
    def __init__(self, name, version, package_version):
        self.__content = collections.OrderedDict()
        self.__name = name
        self.__version = version
        self.__package_version=package_version

    @property
    def content(self):
        return self.__content

    @property
    def name(self) -> str:
        return self.__name

    @property
    def version(self) -> str:
        return self.__version

    @property
    def package_version(self) -> str:
        return self.__package_version

    @property
    def filename(self) -> str:
        return self.name + '.manifest.json'

    def __str__(self):
        return pprint(self.__content)

    def new(self):
        self.content['info'] = collections.OrderedDict()
        self.content['info']['packager version'] = self.version
        self.content['info']['package name'] = self.name
        self.content['info']['package version'] = self.package_version
        self.content['info']['creation date'] = utcTime2IsoStr()
        self.content['info']['lastmod'] = self.content['info']['creation date']

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
        self.content['media']['TopperVideos'] = []
        self.content['media']['ScreenGrabs'] = []

    def open(self, path, installed=False):
        if not os.path.exists(path):
            raise PackageException("Manifest not found at %s" % path)
        try:
            if installed:
                manifest_path = path + '/' + self.filename
            else:
                manifest_path = path + '/' + self.name + '/' + self.filename
            with open(manifest_path) as data_file:
                self.__content = json.load(data_file, object_pairs_hook=collections.OrderedDict)
        except:
            raise PackageException("Manifest not found at %s" % (path + '/' + self.name + '/' + self.filename))

    def save(self, path):
        self.set_field('info/lastmod', utcTime2IsoStr())  # update last modification date
        try:
            with open(path + '/' + self.name + '/' + self.filename, 'w') as outfile:
                json.dump(self.__content, outfile)
        except IOError as e:
            raise PackageException("Manifest write error %s" % str(e))

    def save_as(self, path, name):
        self.set_field('info/lastmod', utcTime2IsoStr())  # update last modification date
        try:
            with open(path + '/' + self.name + '/' + name + '.manifest.json', 'w') as outfile:
                json.dump(self.__content, outfile)
        except IOError as e:
            raise PackageException("Manifest write error %s" % str(e))

    def rename(self, path, name):
        os.unlink(path + '/' + self.name + '/' + self.filename)
        self.save_as(path, name)
        self.__name = name

    def set_field(self, field_path, value):
        content = self.__content
        field_list = field_path.split('/')
        for field in field_list[:-1]:
            content = content[field]
        content[field_list[-1]] = value

    def get_field(self, field_path):
        content = self.__content
        field_list = field_path.split('/')
        for field in field_list[:-1]:
            content = content[field]
        return content[field_list[-1]]

    def exists_field(self, field_path):
        content = self.__content
        field_list = field_path.split('/')
        for field in field_list:
            if not content.get(field):
                return False
            content = content[field]
        return True

    def get_file(self, field_path, filename):
        content = self.__content
        field_list = field_path.split('/')
        for type in field_list:
            content = content[type]
        for file in content:
            if file['file']['name'] == filename:
                return (file, content)
        return None, None

    def prev_file_data_path(self, field_path, filename):
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

    def next_file_data_path(self, field_path, filename):
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

    def exists_file(self, field_path, filename):
        (file, content) = self.get_file(field_path, filename)
        if file is not None:
            return True
        return False

    def del_file(self, field_path, filename):
        (file, content) = self.get_file(field_path, filename)
        if file is not None:
            content.remove(file)
            return True
        return False

    def add_file(self, field_path, fullPathSrcFile, mergeManifest=None):
        mFile = None

        if self.exists_file(field_path, Path(fullPathSrcFile).name):
            return

        file = collections.OrderedDict()
        file['name'] = Path(fullPathSrcFile).name
        file['size'] = os.path.getsize(fullPathSrcFile)
        file['sha1'] = sha1sum(fullPathSrcFile)

        # looking for an 'installed' manifest info
        if mergeManifest != None:
            (mFile, _) = mergeManifest.get_file(field_path, Path(fullPathSrcFile).name)
        if (mFile != None):
            if file['sha1'] != mFile['file']['sha1']:
                logging.warning("! file '%s/%s' changed" % (Path(fullPathSrcFile).name, field_path))
                file['lastmod'] = mtime2IsoStr(os.path.getmtime(fullPathSrcFile))  # last modification date
            else:
                file['lastmod'] = mFile['file']['lastmod']
            file['author(s)'] = mFile['file']['author(s)']
            file['version'] = mFile['file']['version']
            file['url'] = mFile['file']['url']
        else:
            file['author(s)'] = ''
            file['version'] = ''
            file['url'] = ''
            file['lastmod'] = mtime2IsoStr(os.path.getmtime(fullPathSrcFile))  # last modification date

        field_list = field_path.split('/')
        content = self.__content
        for type in field_list:
            content = content[type]
        content.append({'file': file})

    def move_file(self, srcFile, src_field_path, dst_field_path):
        (file, content) = self.get_file(src_field_path, srcFile)
        if file is None:
            return

        content.remove(file)

        field_list = dst_field_path.split('/')
        content = self.__content
        for type in field_list:
            content = content[type]
        content.append(file)

    def rename_file(self, field_path, srcFile, dstFile):
        (file, content) = self.get_file(field_path, srcFile)
        if file is not None:
            file['file']['name'] = dstFile
            return True
        return False

    def get_first_image(self):
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
        self.__mergeManifest = None

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
    def baseModel(self) :
        return self.__baseModel

    @property
    def logger(self):
        return self.baseModel.logger

    # create empty package
    def new(self, packageDir):
        self.__directory = packageDir
        self.__manifest = Manifest(self.name, self.baseModel.version, self.baseModel.package_version)
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
        self.__manifest = Manifest(self.__name,self.baseModel.version, self.baseModel.package_version)
        self.manifest.open(self.__directory)
        if not self.is_compatible():
            raise PackageException("Packager version is too old, please update it to use this packages")

        self.check_package()

    def check_package(self):
        if not os.path.exists(self.directory):
            raise PackageException("Package not found at %s" % self.directory)

        fileInError = self.check_files(self.manifest.content, self.directory + '/' + self.name, '')
        for (field_path, filename) in fileInError:
            self.logger.info("Fix Package Manifest for %s/%s" % (field_path, filename))
            self.__manifest.del_file(field_path.strip('/'), filename)

        self.upgrade_package()

    def upgrade_package(self):
        majorPackagerVersion = int(self.manifest.get_field('info/packager version').split('.')[0])
        minorPackagerVersion = int(self.manifest.get_field('info/packager version').split('.')[1])

        if majorPackagerVersion == 1 and minorPackagerVersion == 1:
            self.logger.info("Upgrade Package to 1.1.x (topper/topper videos)")
            self.manifest.content['media']['TopperVideos'] = []
            if not os.path.exists(self.directory + '/' + self.name + '/media/TopperVideos'):
                os.makedirs(self.directory + '/' + self.name + '/media/TopperVideos')
            self.manifest.set_field('info/packager version', '1.1.0')

    def check_files(self, content, originPath, filePath):
        errorList = []
        if self.__directory == None or self.__manifest == None:
            raise PackageException("Package must be openned")

        for key, value in content.items():
            if key == 'info':
                continue
            elif key == 'file':
                if not os.path.exists(originPath + '/' + filePath + '/' + value['name']):
                    self.logger.warning('File %s not found in package', filePath + '/' + value['name'])
                    errorList.append((filePath, value['name']))
            elif isinstance(value, dict):
                errorList = errorList + self.check_files(content[key], originPath, filePath + '/' + key)
            elif type(value) is list:
                for item in value:
                    if isinstance(item, dict):
                        errorList = errorList + self.check_files(item, originPath, filePath + '/' + key)

        return errorList

    def merge(self, installed=False):
        # read installed manifest
        self.__mergeManifest = Manifest(self.__name,self.baseModel.version, self.baseModel.package_version)
        self.__mergeManifest.open(self.__baseModel.installed_path, installed)

        # build new manifest
        self.manifest.set_field('info/package version', self.__mergeManifest.get_field('info/package version'))
        self.manifest.set_field('info/creation date', self.__mergeManifest.get_field('info/creation date'))
        self.manifest.set_field('info/lastmod', utcTime2IsoStr())

        self.manifest.set_field('info/table designer(s)', self.__mergeManifest.get_field('info/table designer(s)'))
        self.manifest.set_field('info/manufacturer', self.__mergeManifest.get_field('info/manufacturer'))
        self.manifest.set_field('info/table name', self.__mergeManifest.get_field('info/table name'))
        self.manifest.set_field('info/year', self.__mergeManifest.get_field('info/year'))
        self.manifest.set_field('info/theme', self.__mergeManifest.get_field('info/theme'))

    def update(self):
        if not os.path.exists(self.directory):
            raise PackageException("Package not found at %s" % self.directory)
        self.manifest.open(self.__directory)

    def save(self):
        self.manifest.save(self.__directory)

    def rename_files(self, newName, path, content):
        for key, value in content.items():
            if key == 'info':
                continue
            elif key == 'file':
                if value['name'].startswith(self.name, 0, len(self.name)):
                    self.logger.info("+ rename file '%s'" % (path + '/' + value['name']))
                    os.rename(self.directory + '/' + self.name + '/' + path + '/' + value['name'],
                              self.directory + '/' + self.name + '/' + path + '/' + value['name'].replace(self.name,
                                                                                                          newName))
                    value['name'] = value['name'].replace(self.name, newName)

            elif isinstance(value, dict):
                self.rename_files(newName, path + '/' + key, content[key])
            elif type(value) is list:
                for item in value:
                    if isinstance(item, dict):
                        self.rename_files(newName, path + '/' + key, item)

    def rename_package(self, newName):
        if not os.path.exists(self.directory):
            raise PackageException("Package not found at %s" % self.directory)

        self.rename_files(newName, '', self.manifest.content)

        self.manifest.rename(self.directory, newName)
        self.logger.info("+ rename directory  '%s'" % (self.name))

        os.rename(self.directory + '/' + self.name,
                  self.directory + '/' + newName)
        self.__name = newName

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

    def collision_detector(self, src_file: str, dst_file: str, check_sha1: bool= False) -> (Path,bool):
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

    def add_file(self, fullPathSrcFile, dst_field_path, dstFile=None):
        try:
            if not os.path.exists(fullPathSrcFile):
                raise PackageException("File not found at '%s'" % fullPathSrcFile)

            if dstFile == None:
                dstFile = Path(fullPathSrcFile).name
            (dstFile, isSameFile) = self.collision_detector(fullPathSrcFile,
                                                            self.directory + '/' + self.name + '/' + dst_field_path + '/' + dstFile,
                                                            check_sha1=True)
            self.logger.info("+ add '%s' -> '%s'" % (fullPathSrcFile, dst_field_path + '/' + dstFile))

            shutil.copy(fullPathSrcFile, self.directory + '/' + self.name + '/' + dst_field_path + '/' + dstFile)
            self.manifest.add_file(dst_field_path,
                                   self.directory + '/' + self.name + '/' + dst_field_path + '/' + dstFile,
                                   self.__mergeManifest)
            self.save()
        except OSError as e:
            self.logger.error(str(e))
            raise e

    def remove_file(self, srcFile, field_path):
        self.logger.info("+ remove '%s'" % (field_path + '/' + srcFile))
        try:
            os.unlink(self.directory + '/' + self.name + '/' + field_path + '/' + srcFile)
            self.manifest.del_file(field_path, srcFile)
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

    def move_file(self, srcFile, src_field_path, dst_field_path):
        self.logger.info("+ move '%s' -> '%s'" % (src_field_path + '/' + srcFile,
                                                  dst_field_path + '/' + srcFile))

        (dstFile, _) = self.collision_detector(self.directory + '/' + self.name + '/' + src_field_path + '/' + srcFile,
                                               self.directory + '/' + self.name + '/' + dst_field_path + '/' + srcFile,
                                               check_sha1=False)

        try:
            shutil.move(self.directory + '/' + self.name + '/' + src_field_path + '/' + srcFile,
                        self.directory + '/' + self.name + '/' + dst_field_path + '/' + dstFile)
            if srcFile != dstFile:
                self.manifest.rename_file(src_field_path, srcFile, dstFile)
                srcFile = dstFile

            self.manifest.move_file(srcFile, src_field_path, dst_field_path)  # !! move_file -> same name
            self.save()
        except OSError as e:
            self.logger.error(str(e))
            raise e

    def is_compatible(self) -> bool:
        major_version = int(self.baseModel.version.split('.')[0])
        minor_version = int(self.baseModel.version.split('.')[1])
        major_packager_version = int(self.manifest.get_field('info/packager version').split('.')[0])
        minor_packager_version = int(self.manifest.get_field('info/packager version').split('.')[1])
        return major_version >= major_packager_version and minor_version >= minor_packager_version

    # zip package
    def pack(self):
        self.logger.info("* packing table '%s'" % (self.name + self.baseModel.package_extension))
        pack(self.directory + '/' + self.name,
             self.directory,
             self.name + self.baseModel.package_extension)

    # unzip package
    def unpack(self):
        self.logger.info("* unpack table '%s'" % (self.name + self.baseModel.package_extension))
        clean_dir(self.baseModel.tmp_path)
        unpack(self.baseModel.package_path + '/' + self.name + self.baseModel.package_extension,
               self.baseModel.tmp_path)

    def exists_file(self, typePath, filename):
        return self.manifest.exists_file(typePath, filename)

    def get_first_image(self):
        return self.manifest.get_first_image()
