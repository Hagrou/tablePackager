
class PackageException(Exception):
    def __init__(self, msg):
        self.__msg = msg

    @property
    def msg(self):
        return self.__msg

class Directb2sException(Exception):
    def __init__(self, table):
        self.__table = table

    @property
    def table(self):
        return self.__table

class RomException(Exception):
    def __init__(self, table, rom):
        self.__table = table
        self.__rom = rom

    @property
    def table(self):
        return self.__table

    @property
    def rom(self):
        return self.__rom