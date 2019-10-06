#! /usr/bin/env python
# -*- coding: utf-8 -*-


import os
import sqlite3
import sys
import hashlib
#reload(sys)
#sys.setdefaultencoding('utf-8')

def sanity_check():
    if len(sys.argv) != 3:
        return False

    if not os.path.isdir(sys.argv[1]):
        print(sys.argv[1] + " is not a directory!")
        return False

    if os.path.exists(sys.argv[2]):
        print(sys.argv[2] + " should NOT exist!")
        return False

    return True

def print_usage():
    print("Usage:")
    print("    find_dupfile.py DIR TEMP_DB")
    print("Description:")
    print("    DIR: target directory to find out duplicated files in it")
    print("    TEMP_DB: temporary database to store data, must not exist")

def create_temp_db(tdb):
    con = sqlite3.connect(tdb)
    con.text_factory = str
    cur = con.cursor()

    cur.execute("CREATE TABLE files (filename TEXT, size INT, md5 TEXT)")
    cur.execute("CREATE VIEW dups as select *  from files where md5  in (select md5 from files group by md5 having count(md5) > 1)")
    cur.execute("CREATE VIEW dups2 as select *  from files where md5  in (select md5 from files group by md5 having count(md5) = 2)")
    cur.execute("CREATE VIEW dups3 as select *  from files where md5  in (select md5 from files group by md5 having count(md5) = 3)")
    cur.execute("CREATE VIEW dups4 as select *  from files where md5  in (select md5 from files group by md5 having count(md5) > 3)")
    con.commit()
    con.close()


def _FileMd5(filename):
    print(filename)
    file_read_size = 8096

    if not os.path.isfile(filename):
        return False
    myhash = hashlib.md5()
    f = file(filename, 'rb')
    while True:
        b = f.read(file_read_size)
        if not b:
            break
        myhash.update(b)
    f.close()
    return myhash.hexdigest()

def fill_temp_db(tdir, tdb):
    con = sqlite3.connect(tdb)
    con.text_factory = str
    cur = con.cursor()

    num = 0
    for home, dirs, files in os.walk(tdir):
        for ff in files:
            fullname = home + "/" + ff
            md5 = _FileMd5(fullname)
            size = os.path.getsize(fullname)
            cur.execute("INSERT INTO files VALUES (?, ?, ?)", (fullname, size, md5))
            num += 1
            if num == 10000:
                num = 0
                con.commit()

    con.commit()
    con.close()

if __name__ == "__main__":
    if not sanity_check():
        print_usage()
        exit(1)

    tdir = sys.argv[1]
    tdb = sys.argv[2]

    create_temp_db(tdb)
    fill_temp_db(tdir, tdb)



