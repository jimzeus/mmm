#! /usr/bin/env python
# -*- coding: utf-8 -*-


import os
import sqlite3
import sys
import hashlib
#reload(sys)
#sys.setdefaultencoding('utf-8')

def sanity_check():
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        return None, False

    if len(sys.argv) == 2: 
        if not os.path.exists(sys.argv[1]):
            print("Error: ", sys.argv[1], " not exist!")
            return None, False
        else:
            return sys.argv[1], False

    if len(sys.argv) == 3: 
        if not os.path.exists(sys.argv[2]):
            print("Error: ", sys.argv[1], " not exist!")
            return None, False

        if sys.argv[1] != "-n":
            return None, False
        else:
            return sys.argv[2], True



    return True

def print_usage():
    print("Usage:")
    print("    rm_dupfile.py [-n] TEMP_DB")
    print("Description:")
    print("    Delete duplicated files according to temp database")
    print("Options:")
    print("    -n: show files will be deleted instead of really deleting them")
    print("    TEMP_DB: temporary database to store data, created by find_dupfile.py")

# choose which file will be deleted, according to filename 
# several rules will be applied
def _rm_which(f1, f2):
    l1 = len(f1)
    l2 = len(f2)

    # First, here is some cases that none will be deleted
    # 1.Island_Job pics
    # 2.2008_09_13大马行 pics
    if "Island Job" in f1 or "Island Job" in f2:
        return None
    if "2008_09_13大马行" in f1 or "2008_09_13大马行" in f2:
        return None


    # if they have same length:
    # 1. the filename contain "IMG" or "DJI" will be returned, which means it's more "original"
    # 2. otherwise the "bigger" filename will be returned, which means it might has the later timestamp
    if l1 == l2:
        if "IMG" in f1 or "DJI" in f1:
            return f2
        elif "IMG" in f2 or "DJI" in f2:
            return f1
        elif f1 > f2:
            return f1
        else:
            return f2

    # if they don't have the same length
    if l1 > l2:
        lf = f1
        sf = f2
    else:
        lf = f2
        sf = f1

    # 1.if the longer one is ended with "_1", will be returned
    #    that's usually the case like "abcd.jpg" and "abcd_1.jpg"
    # 2.otherwise, return the shorter one
    if lf.split(".")[-2][-2:] == "_1":
        return lf
    else:
        return sf

def rm_from_temp_db(tdb, drill):
    con = sqlite3.connect(tdb)
    con.text_factory = str
    cur = con.cursor()

    cur.execute('''SELECT * FROM dups2 WHERE size > 3000  ORDER BY md5''')
    results = cur.fetchall()
    saved_md5 = None
    saved_filename = None
    to_del = None
    for res in results:
        filename, size, md5 = res
        if saved_md5 != md5:
            saved_md5 = md5
            saved_filename = filename
            continue
        else:
            to_del = _rm_which(saved_filename, filename)

            if to_del == None:
                print("-: ", saved_filename)
                print("-: ", filename)
                print("")
            elif to_del == filename:
                print("X: ", filename)
                print("-: ", saved_filename)
                print("")

            if not drill and to_del != None and os.path.exists(to_del):
                os.remove(to_del)
#            cur.execute('''DELETE FROM  files WHERE filename IN (SELECT filename FROM dups2 WHERE filename LIKE "/media/jimzeus/回忆/pictures/时间照片/照片/%" AND size > 3000) ''')

    con.close()

if __name__ == "__main__":
    tdb, drill = sanity_check()

    if not tdb:
        print_usage()
        exit(1)

    rm_from_temp_db(tdb, drill)



