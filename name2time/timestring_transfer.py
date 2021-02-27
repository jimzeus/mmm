#!/usr/bin/env python
import os
import time

target_dir = "/media/jimzeus/回忆/My Documents/__ok/拍摄设备/MB525/"

for f in os.listdir(target_dir):
    basename = os.path.basename(f)
    ext_name = basename.split('.')[-1]

    print target_dir + basename
    afterbase = time.strftime("%Y_%m_%d_%H%M%S", time.strptime(basename[0:19], "%Y-%m-%d_%H-%M-%S"))
    aftername = target_dir + afterbase + '.' + ext_name
    os.rename(target_dir+basename, aftername) 
    print ""
