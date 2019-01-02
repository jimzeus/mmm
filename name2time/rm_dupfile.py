#! /usr/bin/env python
# -*- coding: utf-8 -*-


import os
import sqlite3
import sys
import hashlib
reload(sys)
sys.setdefaultencoding('utf-8')

def sanity_check():
    if len(sys.argv) != 2:
        return False

    if not os.path.exists(sys.argv[1]):
        print sys.argv[1] + " not exist!"
        return False

    return True

def print_usage():
    print "Usage:"
    print "    rm_dupfile.py TEMP_DB"
    print ""
    print "    TEMP_DB: temporary database to store data, created by find_dupfile.py"



def rm_from_temp_db(tdb):
    con = sqlite3.connect(tdb)
    con.text_factory = str
    cur = con.cursor()

    cur.execute('''SELECT * FROM dups2 WHERE filename LIKE "/media/jimzeus/回忆/pictures/时间照片/照片/%" AND size > 3000  ''')
    results = cur.fetchall()
    for res in results:
        filename, size, md5 = res
        os.remove(filename)
        #print filename
    cur.execute('''DELETE FROM  files WHERE filename IN (SELECT filename FROM dups2 WHERE filename LIKE "/media/jimzeus/回忆/pictures/时间照片/照片/%" AND size > 3000) ''')


    con.close()

if __name__ == "__main__":
    if not sanity_check():
        print_usage()
        exit(1)

    tdb = sys.argv[1]

    rm_from_temp_db(tdb)



