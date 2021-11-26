#!/usr/bin/env python3

import requests
import sys
import time
import datetime
import hashlib
import socket
import os
from ip import updateQQwry
from cls.TimeText import TimeText

# 获取传递的参数
try:
    #0表示文件名，1后面都是参数 0.py, 1, 2, 3
    filename = sys.argv[1:][0]
except:
    filename = 'newip'
print(filename)

try:
    filename_1 = './res/qqwry.dat'
    filename_2 = './res/' + filename + '.dat'
    date1 = TimeText.get_local_file_modifiedtime(filename_1).split()[2]
    date2 = time.asctime(time.localtime()).split()[2]
    print(date1)
    print(date2)
    diffdate = int(date2) - int(date1)
    #if(diffdate > 6 or diffdate < 0):
    filesize_1 = os.path.getsize(filename_1)
    ret = updateQQwry(filename_2)
    print('升级qqwry.dat信息-' + str(ret))
    filesize_2 = os.path.getsize(filename_2)
    if(filesize_2 > filesize_1):
        os.remove(filename_1)
        os.rename(filename_2, filename_1)
    else:
        print('暂时不需要升级！')
except Exception as ex:
    print("Line-29-update:" + str(ex))
