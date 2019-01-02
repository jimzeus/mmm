#! /usr/bin/env python
# -*- coding: utf-8 -*-
import os
import time
import sys
import shutil
import exifread
reload(sys)
sys.setdefaultencoding('utf-8')

# for hachoir metadata
from hachoir_core.error import HachoirError
from hachoir_core.cmd_line import unicodeFilename
from hachoir_parser import createParser
from hachoir_core.tools import makePrintable
from hachoir_metadata import extractMetadata
from hachoir_core.i18n import getTerminalCharset

def get_exif_time(file_name):
    FIELD = 'EXIF DateTimeOriginal'
    fd = open(file_name, 'rb')
    tags = exifread.process_file(fd)
    fd.close()

    if FIELD in tags:
        ctime = str(tags[FIELD])
        try:
            exif_time = time.strftime("%Y_%m_%d_%H%M%S", time.strptime(ctime[0:19], "%Y:%m:%d %H:%M:%S"))
        except ValueError: # some exif use YYYY-MM-DD instead of YYYY:MM:DD
            exif_time = time.strftime("%Y_%m_%d_%H%M%S", time.strptime(ctime[0:19], "%Y-%m-%d %H:%M:%S"))
        return exif_time

    # return None if no exif original time
    return None

def get_hachoir_time(filename):
   
    filename,realname = unicodeFilename(filename), filename
    parser = createParser(filename, realname)
    if not parser:
        #print "Unable to parse file"
        return None
#    try:
    metadata = extractMetadata(parser)
#    except HachoirError, err:
        #print "Metadata extraction error: %s" % unicode(err)
#        metadata = None
    if not metadata:
        #print "Unable to extract metadata"
        return None

    text = metadata.exportPlaintext()
    charset = getTerminalCharset()
    for line in text:
        line = makePrintable(line, charset)
        if line[:16] == "- Creation date:":
            # there might be more than one "Creation date" in metadata
            # and the date might be like 1904-xx-xx, which is obviously wrong
            # so we need to find any "Creation date" later than 2000, then return
            # otherwise, return None to let the fs mtime work
            timestamp = time.mktime(time.strptime(line[17:36], "%Y-%m-%d %H:%M:%S"))
            if timestamp > time.mktime(time.strptime("2000-01-01 01:01:01", "%Y-%m-%d %H:%M:%S")):
                hachoir_time = time.strftime("%Y_%m_%d_%H%M%S",time.localtime(timestamp + 8*3600))
                return hachoir_time

    return None


def get_fs_time(filename):
    stat = os.stat(filename)
    fs_time = time.strftime("%Y_%m_%d_%H%M%S", time.localtime(stat.st_mtime))
    return fs_time

def change_name_to_time(orig_name, drill):

    # switch to absolute path in any case
    orig_name = os.path.abspath(orig_name)

    base_name = os.path.basename(orig_name)
    dir_name = os.path.dirname(orig_name)
    ext_name = base_name.split('.')[-1]
    # FIXME: in file name like "aaa.bbb.jpg", "bbb" will be abandoned
    prefix_name = base_name.split('.')[0]

    # exif time works first; if None, then hachoir metadata time; if None, then fs mtime
    new_name = get_exif_time(orig_name)
    if new_name == None:
        new_name = get_hachoir_time(orig_name)
        if new_name == None:
            new_name = get_fs_time(orig_name)
            if new_name == None:
                new_name = prefix_name
    
    full_name = dir_name + "/" + new_name + "." + ext_name
    # make sure no duplication of name
    if full_name != orig_name: # this if is to avoid no-changing-name
        repeat_time = 1
        while os.path.exists(full_name):
            full_name = dir_name + "/" + new_name + "_" + str(repeat_time) + '.' + ext_name
            repeat_time += 1
    

    if drill:
        print "orig: " + orig_name
        print "then: " + full_name
        print ""
    else:
        os.rename(orig_name, full_name)
        #shutil.move(orig_name, full_name)

    
def sanity_check():
    result = True
    recursive = False
    drill = False
    target = None
    
    if len(sys.argv) > 4 or len(sys.argv) < 2:
        return False, False, False, None
    
    for arg in sys.argv[1:]:
        if arg == "-r":
            recursive = True
        elif arg == "-n":
            drill = True
        elif os.path.exists(arg):
            target = arg
        else:
            result = False
            
    return result, recursive, drill, target
    
def print_usage():
    print "Usage:"
    print "    name2time [OPTION] FILE    : change name of FILE"
    print "    name2time [OPTION] DIR     : change name of all files in DIR"
    print "OPTIONS:"
    print "    -r  recursive"
    print "    -n  no actual rename, just show the result"
    
if __name__ == "__main__":
 
    result, recursive, drill, target = sanity_check()
    
    if not result:
        print_usage()
        exit()
 
    if os.path.isfile(target):
        change_name_to_time(target, drill)
    
    if os.path.isdir(target):
        if not recursive:
            for ff in os.listdir(target):
                if os.path.isfile(target + "/" + ff):
                    change_name_to_time(target + "/" + ff, drill)
        else: # if recursive
            for home, dirs, files in os.walk(target):
                for ff in files:
                    change_name_to_time(home + "/" + ff, drill)
                    