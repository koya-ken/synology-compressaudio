#!/bin/python
# coding: UTF-8

import sys
import glob
import contextlib
import os
import re
import logging
import shutil

from subprocess import call
from mutagen.id3 import ID3, TIT2, TALB, TPE1, TRCK, APIC, TDRC, TCON
from mutagen.mp3 import MP3
from mutagen.flac import FLAC

logger = logging.getLogger("compressaudio")
logger.addHandler(logging.StreamHandler())

@contextlib.contextmanager
def pushd(new_dir):
    previous_dir = os.getcwd()
    os.chdir(new_dir)
    yield
    os.chdir(previous_dir)

def getfiles() :
    get = glob.glob
    files = get(u'**/*.flac')

    for f in files :
        logger.info(f)

def mkdir_or_none(filename) :
    target = os.path.dirname(filename)
    if os.path.exists(target) :
        logger.info(target)
    else :
        os.makedirs(target)
        logger.info((target , 'not exists'))

def compress(left,right) :
    if os.path.exists(right) :
        logger.info((right, ' is exists'))
        return
    
    cmd = 'ffmpeg'
    cmd += ' -i "%s"' % left
    cmd += ' -b:a 320k -vn'
    cmd += ' -acodec libmp3lame -f mp3 -map_metadata 0'
    cmd += ' "%s"' % right
    logger.error(cmd)
    call(cmd,shell=True)

    flac = FLAC(left)
    p = flac.pictures[0]
    mp3  = MP3(right)
    mp3.tags.add(
            APIC(
                encoding=3,
                mime=p.mime,
                type=3,
                desc=u'Cover',
                data=p.data
            )
        )
    mp3.save()
    pass

def find_all_files(dir,filter="*") :
    pattern = re.compile(filter)

    for dirpath,dirnames,filenames in os.walk(dir) :
        if '@eaDir' in dirpath :
            continue
        
        for f in filenames :
            fullpath = os.path.join(dirpath,f)
            if pattern.match(fullpath):
                yield fullpath

# メイン処理
def main() :
    # logger.setLevel(10)
    if len(sys.argv) != 3 :
        logger.warning("invalid argument")
        return 1
    
    left_path  = sys.argv[1]
    right_path = sys.argv[2]
    
    with pushd(left_path) :
        getfiles()
    for f in find_all_files(left_path,'.*.flac$') :
        replaced_path = os.path.splitext(f.replace(left_path,right_path))[0] + '.mp3'
        mkdir_or_none(replaced_path)
        compress(f,replaced_path)
    for f in find_all_files(left_path,'.*.mp4$') :
        replaced_path = f.replace(left_path,right_path)
        replaced_path = os.path.splitext(f.replace(left_path,right_path))[0] + '.m4a'
        mkdir_or_none(replaced_path)
        if not os.path.exists(replaced_path) :
            shutil.copy2(f,replaced_path)
    return 0

if __name__ == '__main__' :
    sys.exit(main())
