#! /usr/bin/env python
# -*- coding: utf-8 -*-
import os
import time
import sys
import exifread
reload(sys)
sys.setdefaultencoding('utf-8')

from hachoir_core.error import HachoirError
from hachoir_core.cmd_line import unicodeFilename
from hachoir_parser import createParser
from hachoir_core.tools import makePrintable
from hachoir_metadata import extractMetadata
from hachoir_core.i18n import getTerminalCharset

# Get metadata for video file
def hachoir_metadata(filename):
    filename,realname = unicodeFilename(filename), filename
    parser = createParser(filename, realname)
    if not parser:
        print "Unable to parse file"
        return None
    try:
        metadata = extractMetadata(parser)
    except HachoirError, err:
        print "Metadata extraction error: %s" % unicode(err)
        metadata = None
    if not metadata:
        print "Unable to extract metadata"
        return None

    text = metadata.exportPlaintext()
    charset = getTerminalCharset()
    for line in text:
        print makePrintable(line, charset)

    return metadata

def exif_metadata(file_name):

    FIELDS = ('EXIF DateTimeOriginal',)

    print "EXIF Metadata:"
    
    fd = open(file_name, 'rb')
    tags = exifread.process_file(fd)
    fd.close()

    for field in FIELDS:
        if field in tags:
            print "- " + field + ": " + str(tags[field])

def fs_meta(filename):

    print "FS Metadata:"
    stat = os.stat(pathname)
    print "- Create Time: " + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(stat.st_ctime))
    print "- Modify Time: " + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(stat.st_mtime))
    print "- Access Time: " + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(stat.st_atime))
    
def sanity_check():
    if len(sys.argv) != 2:
        return False
        
    if not os.path.exists(sys.argv[1]):
        return False

    return True
    
def print_usage():
    print "Usage:"
    print "    metadata.py FILE    : show metadata of FILE"
    
if __name__ == "__main__":
    
    if not sanity_check():
        print_usage()
        exit(1)
        
    pathname = sys.argv[1]
    hachoir_metadata(pathname)
    exif_metadata(pathname)
    fs_meta(pathname)