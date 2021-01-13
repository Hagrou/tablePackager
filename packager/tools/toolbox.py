import logging
import re
import mmap
import os
import stat
import shutil
import zipfile
import threading
import sys
import hashlib
import os.path
import time
import math
import datetime
import time
from datetime import datetime
from time import mktime

from pathlib import Path


def clean_dir(dir: str):
    try:
        shutil.rmtree(dir, ignore_errors=True)
        os.makedirs(dir, exist_ok=True)
    except PermissionError as err:
        print("Error (%s)" % format(err))
    except:
        print("Unexpected error:", sys.exc_info()[0])


def setReadOnlyFile(file):
    if os.path.exists(file):
        fileAtt = os.stat(file)[0]
        os.chmod(file, stat.S_IREAD)


def setReadWriteFile(file):
    if os.path.exists(file):
        fileAtt = os.stat(file)[0]
        if not fileAtt & stat.S_IWRITE:  # File is read-only, so make it writeable
            os.chmod(file, stat.S_IWRITE)


def is_read_only_file(file):
    if os.path.exists(file):
        fileAtt = os.stat(file)[0]
        return not fileAtt & stat.S_IWRITE
    return False


# https://stackoverflow.com/questions/1868714/how-do-i-copy-an-entire-directory-of-files-into-an-existing-directory-using-pyth
def copytree(logger, src, dst, symlinks=False, ignore=None):
    if not os.path.exists(dst):
        os.makedirs(dst)
    for item in os.listdir(src):
        src_path = src + '/' + item  # os.path.join(src, item)
        dst_path = dst + '/' + item  # os.path.join(dst, item)
        logger.info("+ deploy %s" % dst_path)
        if os.path.isdir(src_path):
            copytree(logger, src_path, dst_path, symlinks, ignore)
        else:
            if not os.path.exists(dst_path) or os.stat(src_path).st_mtime - os.stat(dst_path).st_mtime > 1:
                shutil.copy2(src_path, dst_path)


def extract_string_from_binary_file(vpx_file: str, pattern: str) -> list:
    roms = []
    p = re.compile(pattern)
    with open(vpx_file, 'rb', 0) as file, mmap.mmap(file.fileno(), 0, access=mmap.ACCESS_READ) as s:
        m = re.findall(p, s)
        if m is None:
            return []

        for rom in m:
            roms.append(rom.decode('ascii'))
        return roms


def sha1sum(filename):
    h = hashlib.sha1()
    b = bytearray(128 * 1024)
    mv = memoryview(b)
    with open(filename, 'rb', buffering=0) as f:
        for n in iter(lambda: f.readinto(mv), 0):
            h.update(mv[:n])
    return h.hexdigest()


def zipdir(path, ziph):
    for root, dirs, files in os.walk(path):
        for dir in dirs:
            ziph.write(os.path.join(root, dir),
                       Path(os.path.join(root, dir)).relative_to(Path(path).parents[0]))
        for file in files:
            ziph.write(os.path.join(root, file),
                       Path(os.path.join(root, file)).relative_to(Path(path).parents[0]))


def pack(src, dest, pack_name):
    zipf = zipfile.ZipFile(dest + '/' + pack_name, 'w')
    zipdir(src, zipf)
    zipf.close()


def unpack(src, dest):
    zipf = zipfile.ZipFile(src, 'r')
    zipf.extractall(dest)
    zipf.close()


def convert_size(size_bytes):
    if size_bytes == 0:
        return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return "%s %s" % (s, size_name[i])


# UTC Time -> '2019-01-28T22:16:15.631186+00:00'
def utcTime2IsoStr():
    return datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat()


def strIsoUTCTime2DateTime(strIsoTime):
    """ '2019-01-28T22:16:15.631186+00:00' -> datetime"""
    # Fix Python 3.6- Iso Date Parsing +00:00 => +0000
    tzInfo = strIsoTime.rsplit(':', 1)
    strIsoTime = ''.join(tzInfo)
    stime = time.strptime(strIsoTime, "%Y-%m-%dT%H:%M:%S.%f%z")
    return datetime.datetime.fromtimestamp(time.mktime(stime))


# mtime2IsoStr(os.path.getmtime('c:/test.txt'))- > '2019-01-08T00:09:17.682425+00:00'
def mtime2IsoStr(mtime):
    date = datetime.datetime.fromtimestamp(mtime)
    return date.replace(tzinfo=datetime.timezone.utc).isoformat()


def utcTime2Str(utcTime: datetime) -> str:
    """
    Convert utc time to string (UtcTime->'2019-01-08T00:09:17')
    :param utcTime:
    :return: string
    """
    return utcTime.strftime("%Y-%m-%d %H:%M:%S")


def try_str_2_struct_time(str_date: str, time_format: str) -> time.struct_time:
    """
        Search date format and convert it (struct_time is JSON serializable)
        :param str_date:
        :param time_format: expected date format
        :return: datetime or None if date is not recognised
        """

    try:
        return time.strptime(str_date, time_format)
    except ValueError as e:
        if time_format == '%Y-%m-%d':
            return try_str_2_struct_time(str_date, '%m-%d-%Y')
        if time_format == '%m-%d-%Y':
            return try_str_2_struct_time(str_date, '%B %d, %Y')
        return None  # date format unknown


def str_2_struct_time(str_date: str) -> time.struct_time:
    """
    Search date format and convert it (struct_time is JSON serializable)
    :param str_date:
    :return: datetime or None if date is not recognised
    """
    return try_str_2_struct_time(str_date, '%Y-%m-%d')


def struct_time_2_datetime(date: time.struct_time) -> datetime:
    """
    convert struct_time into datetime (not JSON serializable)
    :param date:
    :return:
    """
    return datetime.fromtimestamp(mktime(date))



def searchSentenceInString(string, sentence):
    score = 0.0
    words = sentence.split(' ')
    for word in words:
        if string.find(word) >= 0:
            score = score + 1.0
    return score / len(words)


def unsuffix(path):
    path = Path(path).stem
    while path != Path(path).stem:
        path = Path(path).stem
    return path


def is_suffix(filename: str, suffix: str) -> bool:
    """Test if filename contains a suffix"""
    return suffix in Path(filename).suffixes


def iterative_levenshtein(s, t, costs=(1, 1, 1)):
    """
        thanks to https://www.python-course.eu/levenshtein_distance.php
        iterative_levenshtein(s, t) -> ldist
        ldist is the Levenshtein distance between the strings
        s and t.
        For all i and j, dist[i,j] will contain the Levenshtein
        distance between the first i characters of s and the
        first j characters of t

        costs: a tuple or a list with three integers (d, i, s)
               where d defines the costs for a deletion
                     i defines the costs for an insertion and
                     s defines the costs for a substitution
    """

    rows = len(s) + 1
    cols = len(t) + 1
    deletes, inserts, substitutes = costs

    dist = [[0 for x in range(cols)] for x in range(rows)]

    # source prefixes can be transformed into empty strings
    # by deletions:
    for row in range(1, rows):
        dist[row][0] = row * deletes

    # target prefixes can be created from an empty source string
    # by inserting the characters
    for col in range(1, cols):
        dist[0][col] = col * inserts

    for col in range(1, cols):
        for row in range(1, rows):
            if s[row - 1] == t[col - 1]:
                cost = 0
            else:
                cost = substitutes
            dist[row][col] = min(dist[row - 1][col] + deletes,
                                 dist[row][col - 1] + inserts,
                                 dist[row - 1][col - 1] + cost)  # substitution

    return dist[row][col]


class AsynRun(threading.Thread):
    def __init__(self, method_begin, method_end, context=None):
        threading.Thread.__init__(self)
        self.context = context
        self.method_begin = method_begin
        self.method_end = method_end

    def run(self):
        result = self.method_begin(self.context)
        self.method_end(self.context, result)
