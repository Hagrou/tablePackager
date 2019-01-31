import logging
import re
import mmap
import os
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


# https://stackoverflow.com/questions/1868714/how-do-i-copy-an-entire-directory-of-files-into-an-existing-directory-using-pyth
def copytree(logger, src, dst, symlinks=False, ignore=None):
    if not os.path.exists(dst):
        os.makedirs(dst)
    for item in os.listdir(src):
        srcPath = src+'/'+item #os.path.join(src, item)
        dstPath = dst+'/'+item # os.path.join(dst, item)
        logger.info("+ deploy %s" % (dstPath))
        if os.path.isdir(srcPath):
            copytree(logger, srcPath, dstPath, symlinks, ignore)
        else:
            if not os.path.exists(dstPath) or os.stat(srcPath).st_mtime - os.stat(dstPath).st_mtime > 1:
                shutil.copy2(srcPath, dstPath)

def extract_string_from_binary_file(vpx_file, pattern):
    p = re.compile(pattern)
    with open(vpx_file, 'rb', 0) as file, mmap.mmap(file.fileno(), 0, access=mmap.ACCESS_READ) as s:
        m = p.search(s)
        if m is None:
            return None
        logging.debug("\tstring found %s" % m.group(0))
        return m.group(1).decode('ascii')

"""
def mkdir_and_copy_file(logger, src,target,dest,content):
    os.makedirs(target+'/'+dest, exist_ok=True)
    shutil.copy(src, target+'/'+dest+'/%s' % (src.name))
    file={}
    file['name']=src.name
    file['size'] = os.path.getsize(src)
    file['sha1']=sha1sum(target+'/'+dest+'/%s' % (src.name))
    file['author(s)'] = ''
    file['version'] = ''
    file['lastmod']=mtime2IsoStr(os.path.getmtime(src)) # last modification date

    if content.get(dest) is None:
        content[dest] = [{'file':file}]
    else:
        content[dest].append({'file':file})
    logger.info('+ copy "%s"' % (src.name))

def mkdir_and_rename(logger, src,dst, target,dest_path, content):
    os.makedirs(target+'/'+dest_path, exist_ok=True)
    shutil.copy(src, target+'/'+dest_path+'/%s' % (dst))

    file = {}
    file['name'] = src.name
    file['size'] = os.path.getsize(src)
    file['sha1'] = sha1sum(src)
    file['author(s)'] = ''
    file['version'] = ''
    file['lastmod'] = mtime2IsoStr(os.path.getmtime(src))  # last modification date

    if content.get(dest_path) is None:
        content[dest_path] = [{'file':file}]
    else:
        content[dest_path].append({'file':file})
    logger.info('+ copy "%s"' % (dst))
"""
def sha1sum(filename):
    h  = hashlib.sha1()
    b  = bytearray(128*1024)
    mv = memoryview(b)
    with open(filename, 'rb', buffering=0) as f:
        for n in iter(lambda : f.readinto(mv), 0):
            h.update(mv[:n])
    return h.hexdigest()

def zipdir(path, ziph):
    for root, dirs, files in os.walk(path):
        for dir in dirs:
            ziph.write(os.path.join(root, dir),
                       Path(os.path.join(root, dir)).relative_to(Path(path).parents[0]))
        for file in files:
            ziph.write(os.path.join(root,file),
                                    Path(os.path.join(root,file)).relative_to(Path(path).parents[0]))

def pack(src, dest, pack_name):
    zipf = zipfile.ZipFile(dest+'/'+pack_name, 'w')
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
    tzInfo=strIsoTime.rsplit(':',1)
    strIsoTime=''.join(tzInfo)
    stime=time.strptime(strIsoTime, "%Y-%m-%dT%H:%M:%S.%f%z")
    return datetime.datetime.fromtimestamp(time.mktime(stime))

# mtime2IsoStr(os.path.getmtime('c:/test.txt'))- > '2019-01-08T00:09:17.682425+00:00'
def mtime2IsoStr(mtime):
    date=datetime.datetime.fromtimestamp(mtime)
    return date.replace(tzinfo=datetime.timezone.utc).isoformat()

# UtcTime->'2019-01-08T00:09:17'
def utcTime2Str(utcTime):
    return utcTime.strftime("%Y-%m-%d %H:%M:%S")


class AsynRun(threading.Thread):
    def __init__ (self, method_begin, method_end, context=None):
        threading.Thread.__init__ (self)
        self.context=context
        self.method_begin= method_begin
        self.method_end=method_end

    def run(self) :
        self.method_begin(self.context)
        self.method_end(self.context)

