import traceback


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


class ConnectionException(Exception):
    def __init__(self, name: str = '', url: str = '', error_code: int = 0):
        self.__name = name
        self.__url = url
        self.__error_code = error_code
        self.__stack = ''.join(traceback.format_exception(self.__class__, self, self.__traceback__))

    def __str__(self):
        return 'Connection Error %s (%d)\n%s' % (self.__url, self.__error_code, self.__stack)

    @property
    def name(self):
        return self.__name

    @property
    def url(self):
        return self.__url

    @property
    def error_code(self):
        return self.__error_code

    @property
    def stack(self):
        return ''.join(traceback.format_exception(self.__class__, self, self.__traceback__))
