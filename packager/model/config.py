import os
import json

class Config:
    def __init__(self):
        self.__data={
            'working_dir': os.path.expanduser("~/tablePackager"),
            'visual_pinball_path':'c:/visual pinball',
            'pinballX_path':'c:/pinballX',
            'pinupSystem_path':'c:/PinUPSystem',
            'font':("Helvetica", 10)
        }

        self.load()

    def get(self,var_name):
        if var_name=='package_extension':
            return '.zip'
        return self.__data[var_name]

    def set(self, var_name, value):
        self.__data[var_name]=value

    def load(self):


        working_dir=self.get('working_dir')
        if not os.path.exists(working_dir):
            os.makedirs(working_dir, exist_ok=True)

        path = working_dir + '/config.json'
        if not os.path.exists(path): # no config? write it with default values
            self.save()
            return
        try:
            with open(path) as data_file:
                self.__data = json.load(data_file)
        except:
            raise Exception("Manifest not found at %s" % (path + '/' + self.name + '/' + self.filename))

    def save(self):
        try:
            with open(self.get('working_dir')+ '/config.json', 'w') as outfile:
                json.dump(self.__data, outfile)
        except IOError as e:
            raise Exception("Config write error %s" % e.strerror)

