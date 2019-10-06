#! /usr/bin/env python
# -*- coding: utf-8 -*-
import os
import time
import sys
import shutil
import exifread
#reload(sys)
#sys.setdefaultencoding('utf-8')

# for hachoir metadata
#from hachoir_core.error import HachoirError
#from hachoir_core.cmd_line import unicodeFilename
#from hachoir_parser import createParser
#from hachoir_core.tools import makePrintable
#from hachoir_metadata import extractMetadata
#from hachoir_core.i18n import getTerminalCharset

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

    return None # hachoir_core package not installed
   
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



def get_name(prefix_name, orig_name):

    # exif time works first; if None, then hachoir metadata time; if None, then fs mtime
    # if both fs_mtime and hachoir_time exist, pick the earlier one
    new_name = get_exif_time(orig_name)
    if new_name == None:
        new_name = get_hachoir_time(orig_name)
        if new_name == None:
            new_name = get_fs_time(orig_name)
            if new_name == None:
                new_name = prefix_name
        else: # if we have hachoir time, compare it with fs time, and pick the earlier one
            fs_time = get_fs_time(orig_name)
            if new_name > fs_time:
                new_name = fs_time


    #from YYYY_MM_DD_hhmmss.JPG to YYYY_MM_DD_hh_mm_IMG_1234.JPG (same as itools import file name)
    new_name = new_name[0:13] + "_" + new_name[13:15] + "_" + prefix_name[-8:]

    return new_name

def change_name_to_time(orig_name, drill, fix):

    # switch to absolute path in any case
    orig_name = os.path.abspath(orig_name)

    base_name = os.path.basename(orig_name)
    dir_name = os.path.dirname(orig_name)
    ext_name = base_name.split('.')[-1]
    # FIXME: in file name like "aaa.bbb.jpg", "bbb" will be abandoned
    prefix_name = base_name.split('.')[0]


    new_name = get_name(prefix_name, orig_name)
    fix_name = new_name # assign fix_name no matter we do it or not, for compatibility

    if fix:
        # fix possible time error:
        # any file with larger name like IMG_XXXX : IMG_1111 > IMG_1100
        # should have later time than the current file
        # if not,


        if (fix_name[-8:-4]  == "IMG_") or (fix_name[-8:-4]  == "MG_E"):
            for other_file in os.listdir(dir_name):     # for every entry in the same dir
                if os.path.isfile(other_file):          # if it's a file
                    oo_name = os.path.abspath(other_file)
                    ob_name = os.path.basename(other_file)
                    op_name = ob_name.split('.')[0]
                    on_name = get_name(op_name, oo_name)

                    if (on_name[-8:-4] == "IMG_") or (on_name[-8:-4] == "MG_E"):        # and name like *IMG_????.* or *IMG_E????.*
                        if (on_name[-4:] > fix_name[-4:]) and (on_name[0:16] < fix_name[0:16]): # with larger ???? and earlier time than current file
                            fix_name = on_name[0:16] + fix_name[16:] # update the first part of name, which is time



    full_name = dir_name + "/" + new_name + "." + ext_name
    full_fix_name = dir_name + "/" + fix_name + "." + ext_name

    # make sure no duplication of name
    if full_fix_name != orig_name: # this if is to avoid no-changing-name
        repeat_time = 1
        while os.path.exists(full_fix_name):
            full_fix_name = dir_name + "/" + new_name + "_" + str(repeat_time) + '.' + ext_name
            repeat_time += 1
    

    if drill:
        print ("orig: " + orig_name)
        print ("then: " + full_name)
        if fix:
            print ("fix : " + full_fix_name)
        print ("")
    else:
        os.rename(orig_name, full_fix_name)
        #shutil.move(orig_name, full_name)

    
def sanity_check():
    result = True
    recursive = False
    drill = False
    fix = False
    target = None
    
    if len(sys.argv) > 5 or len(sys.argv) < 2:
        return False, False, False, False, None
    
    for arg in sys.argv[1:]:
        if arg == "-r":
            recursive = True
        elif arg == "-n":
            drill = True
        elif arg == "-f":
            fix = True
        elif os.path.exists(arg):
            target = arg
        else:
            result = False
            
    return result, recursive, drill, fix, target
    
def print_usage():
    print ("Usage:")
    print ("    name2time [OPTION] FILE    : change name of FILE")
    print ("    name2time [OPTION] DIR     : change name of all files in DIR")
    print ("OPTIONS:")
    print ("    -r  recursive")
    print ("    -n  no actual rename, just show the result")
    print ("    -f  fix filename according to other file name and time, takes long time")
    
if __name__ == "__main__":
 
    result, recursive, drill, fix, target = sanity_check()
    
    if not result:
        print_usage()
        exit()
 
    if os.path.isfile(target):
        change_name_to_time(target, drill, fix)
    
    if os.path.isdir(target):
        if not recursive:
            for ff in os.listdir(target):
                if os.path.isfile(target + "/" + ff):
                    change_name_to_time(target + "/" + ff, drill, fix)
        else: # if recursive
            for home, dirs, files in os.walk(target):
                for ff in files:
                    change_name_to_time(home + "/" + ff, drill, fix)
                    
