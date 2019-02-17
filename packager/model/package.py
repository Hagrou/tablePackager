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

#from packager.tablePackager import version
version='1.0'
class Manifest:
    def __init__(self, name):
        self.__content=collections.OrderedDict()
        self.__name=name

    @property
    def content(self):
        return self.__content

    @property
    def name(self):
        return self.__name

    @property
    def filename(self):
        return self.name+'.manifest.json'

    def __str__(self):
        return pprint(self.__content)

    def new(self):
        self.content['info']=collections.OrderedDict()
        self.content['info']['packager version']=version
        self.content['info']['package name']=self.name
        self.content['info']['package version'] = '1.0'
        self.content['info']['creation date']=utcTime2IsoStr()
        self.content['info']['lastmod']=self.content['info']['creation date']

        self.content['info']['table designer(s)'] = ''
        self.content['info']['manufacturer'] = ''
        self.content['info']['table name'] = ''
        self.content['info']['year'] = ''
        self.content['info']['theme'] = ''

        self.content['visual pinball'] = collections.OrderedDict()
        self.content['visual pinball']['tables']=[]
        self.content['visual pinball']['info'] = collections.OrderedDict()
        self.content['visual pinball']['info']['romName']=''

        self.content['UltraDMD'] = collections.OrderedDict()
        self.content['UltraDMD']['content'] = []

        self.content['VPinMAME'] = collections.OrderedDict()
        self.content['VPinMAME']['cfg']=[]
        self.content['VPinMAME']['nvram'] = []
        self.content['VPinMAME']['roms'] = []
        self.content['VPinMAME']['memcard'] = []

        self.content['media'] = collections.OrderedDict()
        self.content['media']['Flyers Front']=[]
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

    def open(self, path, installed=False):
        if not os.path.exists(path):
            raise PackageException("Manifest not found at %s" % path)
        try:
            if installed:
                manifestPath=path+'/'+self.filename
            else:
                manifestPath=path+'/'+self.name+'/'+self.filename
            with open(manifestPath) as data_file:
                    self.__content = json.load(data_file,object_pairs_hook=collections.OrderedDict)
        except:
            raise PackageException("Manifest not found at %s" % (path+'/'+self.name+'/'+self.filename))


    def save(self, path):
        self.set_field('info/lastmod',utcTime2IsoStr()) # update last modification date
        try:
            with open(path+'/'+self.name+'/'+self.filename, 'w') as outfile:
                json.dump(self.__content, outfile)
        except IOError as e:
            raise PackageException("Manifest write error %s" % e.strerror)

    def saveAs(self, path,name):
        self.set_field('info/lastmod', utcTime2IsoStr())  # update last modification date
        try:
            with open(path+'/'+self.name+'/'+name+'.manifest.json', 'w') as outfile:
                json.dump(self.__content, outfile)
        except IOError as e:
            raise PackageException("Manifest write error %s" % e.strerror)

    def rename(self, path, name):
        os.unlink(path+'/'+self.name+'/'+self.filename)
        self.saveAs(path, name)
        self.__name = name

    def set_field(self, field_path, value):
        content = self.__content
        field_list=field_path.split('/')
        for field in field_list[:-1]:
            content = content[field]
        content[field_list[-1]]=value

    def get_field(self, field_path):
        content = self.__content
        field_list=field_path.split('/')
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
                return (file,content)
        return (None,None)

    def exists_file(self, type_path, filename):
        (file, content)=self.get_file(type_path, filename)
        if file!=None:
            return True
        return False

    def del_file(self, type_path, filename):
        (file, content) = self.get_file(type_path, filename)
        if file != None:
            content.remove(file)
            return True
        return False

    def add_file(self, field_path, srcFile):
        file = collections.OrderedDict()
        file['name'] = Path(srcFile).name
        file['size'] = os.path.getsize(srcFile)
        file['sha1'] = sha1sum(srcFile)
        file['author(s)'] = ''
        file['version'] = ''
        file['url']=''
        file['lastmod'] = mtime2IsoStr(os.path.getmtime(srcFile))  # last modification date

        field_list = field_path.split('/')
        content = self.__content
        for type in field_list:
            content = content[type]
        content.append({'file':file})


class Package:
    def __init__(self, baseModel, name):
        self.__baseModel=baseModel
        self.__name=name
        self.__directory=None
        self.__manifest=None

    @property
    def manifest(self):
        return self.__manifest

    @property
    def name(self):
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

    def new(self, packageDir):
        self.__directory=packageDir
        self.__manifest=Manifest(self.name)
        self.__manifest.new() # create empty package
        self.build_tree(self.directory+'/'+self.name, self.manifest.content)
        self.__manifest.save(self.directory)

    """
    Open and read directory package
    """
    def open(self, baseDir):
        if not os.path.exists(baseDir):
            raise PackageException("Package not found at %s" % baseDir)
        self.__directory=baseDir
        self.__manifest=Manifest(self.__name)
        self.manifest.open(self.__directory)

    def update(self):
        if not os.path.exists(self.directory):
            raise PackageException("Package not found at %s" % self.directory)
        self.manifest.open(self.__directory)

    def save(self):
        self.manifest.save(self.__directory)

    def rename_files(self, newName, path, content):
        for key, value  in content.items():
            if key=='info':
                continue
            elif key=='file':
                if value['name'].startswith(self.name, 0,len(self.name)):
                    self.logger.info("+ rename file '%s'" % (path+'/'+value['name']))
                    os.rename(self.directory+'/'+self.name+'/'+path+'/'+value['name'],
                                                     self.directory +'/'+self.name+'/'+path+'/'+value['name'].replace(self.name,newName))
                    value['name']=value['name'].replace(self.name,newName)

            elif isinstance(value, dict):
                self.rename_files(newName, path+'/'+key, content[key])
            elif type(value) is list:
                for item in value:
                    if isinstance(item, dict):
                        self.rename_files(newName,path+'/'+key, item)

    def rename(self, newName):
        if not os.path.exists(self.directory):
            raise PackageException("Package not found at %s" % self.directory)

        self.rename_files(newName, '', self.manifest.content)

        self.manifest.rename(self.directory, newName)
        self.logger.info("+ rename directory  '%s'" % (self.name))

        os.rename(self.directory + '/' + self.name,
                  self.directory + '/' + newName)
        self.__name=newName


    def build_tree(self, baseDir, content):
        for item in content:
            if item == 'info': continue
            os.makedirs(baseDir+'/'+item, exist_ok=True)
            self.build_tree(baseDir+'/'+item, content[item])


    def set_field(self, field_path, value):
        self.manifest.set_field(field_path, value)

    def get_field(self, field_path):
        return self.manifest.get_field(field_path)

    def exists_field(self, field_path):
        return self.manifest.exists_field(field_path)

    def add_file(self, srcFile, field_path, dstFile=None):
        try:
            if not os.path.exists(srcFile):
                raise PackageException("File not found at '%s'" % srcFile)
            if dstFile==srcFile or dstFile==None: # same name
                self.logger.info("+ add '%s' -> '%s'" % (Path(srcFile).name,field_path))
                dstFile=self.directory+'/'+self.name + '/' + field_path + '/%s' % (Path(srcFile).name)
            else: # rename file
                self.logger.info("+ radd '%s' -> '%s'" % (Path(dstFile).name,field_path))
                dstFile = self.__directory + '/' + self.name + '/' + field_path + '/%s' %(Path(dstFile).name)
            shutil.copy(srcFile, dstFile)
            self.manifest.add_file(field_path,dstFile)
            self.save()
        except OSError as e:
            self.logger.error(e.strerror)
            raise e

    def remove_file(self, srcFile, field_path):
        self.logger.info("+ remove '%s'" % (field_path + '/'+ srcFile))
        try:
            os.unlink(self.directory+'/'+self.name+'/'+field_path + '/'+ srcFile)
            self.manifest.del_file(field_path, srcFile)
            self.save()
        except OSError as e:
            self.logger.error(e.strerror)
            raise e

    # zip package
    def pack(self):
        self.logger.info("* packing table '%s'" % (self.name+ self.baseModel.package_extension))
        pack(self.directory+'/'+self.name,
             self.directory,
             self.name+ self.baseModel.package_extension)
    # unzip package
    def unpack(self):
        self.logger.info("* unpack table '%s'" % (self.name + self.baseModel.package_extension))
        clean_dir(self.baseModel.tmp_path)
        unpack(self.baseModel.package_path+'/'+self.name + self.baseModel.package_extension,self.baseModel.tmp_path)

    def exists_file(self, typePath, filename):
        return self.manifest.exists_file(typePath, filename)
