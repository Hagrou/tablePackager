import os

class Config:
    def __init__(self):
        self.__data={
            'working_dir': os.path.expanduser("~/tablePackager"),
            'visual_pinball_path':'c:/visual pinball',
            'pinballX_path':'c:/pinballX',
            'pinupSystem_path':'c:/PinUPSystem',
            'font':("Helvetica", 10)
        }

    def get(self,var_name):
        if var_name=='package_extension':
            return '.zip'
        return self.__data[var_name]

