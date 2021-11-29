#!/usr/bin/env python3

import requests
import os
import time
import urllib.request as urllib2
from cls.LocalFile import LocalFile

class NetFile(): # 将订阅链接中YAML，Base64等内容转换为 Url 链接内容
    # 从网络下载文件，返回文本信息
    def url_to_str(r_url, linktime, readtime):
        retxt = ''
        try:
            rq = requests.get(r_url, timeout=(linktime, readtime))
            #rq = requests.get(url, timeout=(30, 60)) #连接超时 和 读取超时
            if (rq.status_code != 200):
                print("NetFile-Line-18: Download File error.][" + str(rq.status_code) + "]-Url: " + r_url)
            else:
                retxt = rq.content.decode("utf-8")
        except Exception as ex:
            print('NetFile-Line-34: down res file err: ' + str(ex) + '\n' +  r_url)
        return retxt

    # 从网络下载配置文件，下载失败则读取本地文件
    def down_res_file(r_url, fname, linktime, readtime):
        retxt = ''
        try:
            r_url = r_url + '' + fname
            rq = requests.get(r_url, timeout=(linktime, readtime))
            #rq = requests.get(url, timeout=(30, 60)) #连接超时 和  读取超时
            if (rq.status_code != 200):
                print("NetFile-Line-33:" + str(rq.status_code) + "] Download sub error on link, Read local file. " + r_url)
                retxt = LocalFile.read_LocalFile("./res/" + fname)
            else:
                print("NetFile-Line-36:" + str(rq.status_code) + " get file from " + r_url)
                #retxt = rq.text
                #print(type(ret))    # 返回类型 <class 'requests.models.Response'>
                #print(ret)          # 返回值:<Response [200]>
                #print(ret.text)     # 输出文本信息
                #print(ret.content)  # 以二进制输出
                retxt = rq.content.decode("utf-8")
                LocalFile.write_LocalFile('./res/' + fname, retxt)
        except Exception as ex:
            retxt = LocalFile.read_LocalFile("./res/" + fname)
            print('NetFile-Line-46: down res file err: ' + str(ex) + '\n' +  r_url)
        return retxt

def getRemoteFileSize(url, proxy = None):
    ''' 通过content-length头获取远程文件大小
        url - 目标文件URL
        proxy - 代理  '''
    opener = urllib2.build_opener()
    if proxy:
        if url.lower().startswith('https://'):
            opener.add_handler(urllib2.ProxyHandler({'https' : proxy}))
        else:
            opener.add_handler(urllib2.ProxyHandler({'http' : proxy}))
    try:
        request = urllib2.Request(url)
        request.get_method = lambda: 'HEAD'
        response = opener.open(request)
        response.read()
    except Exception:
        return 0
    else:
        print(response.headers)
        fileSize = dict(response.headers).get('Content-Length', 0)
        if(fileSize == 0):
            fileSize = dict(response.headers).get('content-length', 0)
        return int(fileSize)