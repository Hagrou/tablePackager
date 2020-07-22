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

from pathlib import Path


def clean_dir(dir):
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
        if (not fileAtt & stat.S_IWRITE):  # File is read-only, so make it writeable
            os.chmod(file, stat.S_IWRITE)


def isReadOnlyFile(file):
    if os.path.exists(file):
        fileAtt = os.stat(file)[0]
        return not fileAtt & stat.S_IWRITE
    return False


# https://stackoverflow.com/questions/1868714/how-do-i-copy-an-entire-directory-of-files-into-an-existing-directory-using-pyth
def copytree(logger, src, dst, symlinks=False, ignore=None):
    if not os.path.exists(dst):
        os.makedirs(dst)
    for item in os.listdir(src):
        srcPath = src + '/' + item  # os.path.join(src, item)
        dstPath = dst + '/' + item  # os.path.join(dst, item)
        logger.info("+ deploy %s" % (dstPath))
        if os.path.isdir(srcPath):
            copytree(logger, srcPath, dstPath, symlinks, ignore)
        else:
            if not os.path.exists(dstPath) or os.stat(srcPath).st_mtime - os.stat(dstPath).st_mtime > 1:
                shutil.copy2(srcPath, dstPath)


def extract_string_from_binary_file(vpx_file, pattern) -> object:
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


# '2019-01-28T22:16:15.631186+00:00' -> datetime
def strIsoUTCTime2DateTime(strIsoTime):
    # Fix Python 3.6- Iso Date Parsing +00:00 => +0000
    tzInfo = strIsoTime.rsplit(':', 1)
    strIsoTime = ''.join(tzInfo)
    stime = time.strptime(strIsoTime, "%Y-%m-%dT%H:%M:%S.%f%z")
    return datetime.datetime.fromtimestamp(time.mktime(stime))


# mtime2IsoStr(os.path.getmtime('c:/test.txt'))- > '2019-01-08T00:09:17.682425+00:00'
def mtime2IsoStr(mtime):
    date = datetime.datetime.fromtimestamp(mtime)
    return date.replace(tzinfo=datetime.timezone.utc).isoformat()


# UtcTime->'2019-01-08T00:09:17'
def utcTime2Str(utcTime):
    return utcTime.strftime("%Y-%m-%d %H:%M:%S")


def searchSentenceInString(string, sentence):
    score = 0.0
    words = sentence.split(' ')
    for word in words:
        if string.find(word) >= 0:
            score = score + 1.0
    return score / len(words)


def unsuffix(path):
    path = Path(path).stem
    while (path != Path(path).stem):
        path = Path(path).stem
    return path


"""
#https://stackabuse.com/levenshtein-distance-and-text-similarity-in-python/
import numpy as np
import numpy.core._methods
import numpy.lib.format

def levenshtein(seq1, seq2):
    size_x = len(seq1) + 1
    size_y = len(seq2) + 1
    matrix = np.zeros ((size_x, size_y))
    for x in range(size_x):
        matrix [x, 0] = x
    for y in range(size_y):
        matrix [0, y] = y

    for x in range(1, size_x):
        for y in range(1, size_y):
            if seq1[x-1] == seq2[y-1]:
                matrix [x,y] = min(
                    matrix[x-1, y] + 1,
                    matrix[x-1, y-1],
                    matrix[x, y-1] + 1
                )
            else:
                matrix [x,y] = min(
                    matrix[x-1,y] + 1,
                    matrix[x-1,y-1] + 1,
                    matrix[x,y-1] + 1
                )
    return (matrix[size_x - 1, size_y - 1])
"""


class AsynRun(threading.Thread):
    def __init__(self, method_begin, method_end, context=None):
        threading.Thread.__init__(self)
        self.context = context
        self.method_begin = method_begin
        self.method_end = method_end

    def run(self):
        result = self.method_begin(self.context)
        self.method_end(self.context, result)
