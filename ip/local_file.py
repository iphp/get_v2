#!/usr/bin/env python3

import requests
import os
import time

class local_file(): # 将订阅链接中YAML，Base64等内容转换为 Url 链接内容

    # 从本地文本文件中读取字符串
    def read_local_file(fname):
        retxt = ""
        try:
            with open(fname, "r") as f:  # 打开文件
                retxt = f.read()  # 读取文件
        except Exception as ex:
            print("Line-15-local_file: open local file error. \n" + + str(ex))
        return retxt.strip('\n')

    # 写入字符串到本地文件
    def write_local_file(fname, fcont):
        try:
            res = fcont.encode("utf-8")
            _file = open(fname, 'w', encoding='utf-8')
            _file.write(res.decode("utf-8"))
            _file.close()
        except Exception as ex:
            print("Line-26-local_file: write local file error. \n" + str(ex))
