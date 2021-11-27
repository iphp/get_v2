#!/usr/bin/env python3

import requests
import sys
import json
import base64
import os
import re
import time
import datetime
import hashlib
import pdb
import socket
import multiprocessing
import subprocess
import operator
from cls import IsValid
from cls import LocalFile
from cls import NetFile
from cls import StrText
from cls import PingIP
from ping3 import ping, verbose_ping

# 配置信息
# resurl = 'https://ipfs.io/ipns/k2k4r8n10q07nqe02zysssxw1b9qboab0dd3ooljd32i9ro3edry6hv6/'
resurl = 'https://cf-ipfs.com/ipns/k2k4r8n10q07nqe02zysssxw1b9qboab0dd3ooljd32i9ro3edry6hv6/'
# resurl = os.environ["RESURL"] + '/ipns/k2k4r8n10q07nqe02zysssxw1b9qboab0dd3ooljd32i9ro3edry6hv6/'
# resurl = "http://127.0.0.1/"

def get_list_sort(s):
    global list
    # 先将列表转化为set，再转化为list就可以实现去重操作
    list = list(set(s))
    # 将list进行排序 .sort(reverse=True)表示倒序
    list.sort()
    return list

# 同步本地需要更新的资源文件
# 下载IPFS网关节点信息
try:
    ipfs = NetFile.down_res_file(resurl, 'ipfs', 240, 120)
    if(len(ipfs)<2000):
        ipfs = LocalFile.read_LocalFile("./res/ipfs")
except Exception as ex:
    print('Get-ipfs.txt:\n' + str(ex))
    ipfs = LocalFile.read_LocalFile("./res/ipfs")
print('Get-ipfs.txt:\n' + ipfs)

# 下载代理节点过滤信息
try:
    expire = NetFile.down_res_file(resurl, 'expire.txt', 240, 120)
    if(len(expire)<2000):
        expire = LocalFile.read_LocalFile("./res/expire.txt")
except Exception as ex:
    print('Get-expire.txt:\n' + str(ex))
    expire = LocalFile.read_LocalFile("./res/expire.txt")
print('Get-expire.txt:Len(' + str(len(expire)) + ')')

# 下载订阅链接将其合并
nodes = LocalFile.read_LocalFile("./res/node.json")
print('Get-node.json: \n' + nodes)

sub_link = []
#for i in range(len(sub_url)):
#    s_url = sub_url[i]
nodeurl = ""
allonenode = ""
if(len(expire) > 0):
    list1 = nodes.split('\n')
    list1 = get_list_sort(list1)
    linecount = 0
    ii = 0
    for i in list1:
        try:
            ii += 1
            print('\nNodes-List-OneNodeList:\n' + i)
            onode = json.loads(i)
            onode_uptime = onode['uptime']
            onode_upmd5 = onode['upmd5']
            onode_upurl = onode['upurl']
            try:
                rq = requests.get(onode_upurl, timeout=(240, 120)) #连接超时 和 读取超时
                if (rq.status_code != 200):
                    print('[GET Code {}] Download sub error on link: '.format(rq.status_code) + onode_upurl)
                    continue
                if (onode_upmd5 != hashlib.md5(rq.content).hexdigest() and linecount < 50):
                    if (onode_upurl.find('vpei') == -1):
                        linecount += 1
                    #60行后，只执行一行
                    if (ii > 70):  
                        linecount = 50
                    clashnodes = ''
                    print('Get node link on sub ' + onode_upurl)
                    onode['upmd5'] = hashlib.md5(rq.content).hexdigest()
                    #onode['uptime'] = time.asctime( time.localtime(time.time()) )
                    #onode['uptime'] = (datetime.datetime.now() + datetime.timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S")
                    #onode['uptime'] = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(datetime.datetime.now() - datetime.timedelta(days=7)))
                    if (onode_upurl.find('k2k4r8n10q07nqe02zysssxw1b9qboab0dd3ooljd32i9ro3edry6hv6/index') > -1):
                        onode['uptime'] = (datetime.datetime.now() - datetime.timedelta(days=730)).strftime("%Y-%m-%d %H:%M:%S")
                    elif (onode_upurl.find('vpei') > -1):
                        onode['uptime'] = (datetime.datetime.now() - datetime.timedelta(days=365)).strftime("%Y-%m-%d %H:%M:%S")
                    elif (ii > 70):
                        onode['uptime'] = (datetime.datetime.now() + datetime.timedelta(days=365)).strftime("%Y-%m-%d %H:%M:%S")
                    else:
                        onode['uptime'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    print('UpdateTime:' + onode['uptime'])
                    #clashnodes = str(rq.content, encoding='utf-8')
                    clashnodes = (rq.content).decode('utf-8' ,"ignore")
                    if (clashnodes != ''):
                        if (onode['type'] == 'mixed'):
                            try:
                                if(IsValid.isBase64(clashnodes)):
                                    print('Url-All-Nodes-is-Base64:\n' + clashnodes)
                                    sub_link.append(base64.b64decode(clashnodes).decode("utf-8"))
                                else:
                                    print('Url-All-Nodes-no-Base64:\n' + clashnodes)
                                    sub_link.append(clashnodes)
                            except Exception as ex:
                                print('Line-212:' + str(ex))
                        elif (onode['type'] == 'clash'):
                            try:
                                #- {name: "@SSRSUB-V05-付费推荐:suo.yt/ssrsub", server: uuus1.liuwei01.tk, port: 443, type: vmess, uuid: 0fab5928-9d70-4666-b351-5debff8a15de, alterId: 0, cipher: auto, tls: true, skip-cert-verify: false, network: ws, ws-path: /liuwei, ws-headers: {Host: uuus1.liuwei01.tk}, udp: true}
                                #- {name: 付费推荐:dlj.tf/ssrsub__10, server: 172.99.190.153, port: 8090, type: ss, cipher: aes-256-gcm, password: PCnnH6SQSnfoS27, udp: true}
                                try:
                                    if(clashnodes.find('proxies:') > -1 and clashnodes.find('proxy-groups:') > -1):
                                        clashnodes = StrText.get_str_btw(clashnodes, 'proxies:', 'proxy-groups:')
                                    elif(clashnodes.find('proxies:') > -1 and clashnodes.find('proxy-groups:') == -1):
                                        clashnodes = clashnodes.partition('proxies:')[2]
                                except Exception as ex:
                                    print('\nLine-204:\n' + str(ex) +'\n' + clashnodes)
                                clashnodes = clashnodes.strip('\n')
                                #print('Url-All-Nodes-Clash-Old0:\n' + clashnodes)
                                clashnodes = clashnodes.replace('\'', '').replace('"', '').replace('  ', ' ').strip('-').strip(' ')
                                #print('Url-All-Nodes-Clash-Old1:\n' + clashnodes)
                                if(clashnodes.find(',') > -1 and clashnodes.find('{') > -1 and clashnodes.find('}') > -1):
                                    clashnodes = clashnodes.replace(', ', ',')
                                    clashnodes = clashnodes.replace('- {', '{')
                                    clashnodes = clashnodes.replace('{ ', '{')
                                    clashnodes = clashnodes.replace('}', '"}')
                                    if(clashnodes.find(': ') > -1):
                                        clashnodes = clashnodes.replace(': ', '": "')
                                    else:
                                        clashnodes = clashnodes.replace(':', '": "')
                                    clashnodes = clashnodes.replace(',', '", "')
                                    #clashnodes = clashnodes.replace('{"Host": "', '{Host: ')
                                    #clashnodes = clashnodes.replace('"}",', '}",')
                                    clashnodes = clashnodes.replace('{', '{"')
                                    clashnodes = clashnodes.strip('\n').strip('- ')
                                else:
                                    clashnodes = clashnodes.strip('\n').strip('- ')
                                    clashnodes = clashnodes.replace('\n', ',').replace('\r', ',').replace(',', ',')
                                    clashnodes = clashnodes.replace(',- ', '"}\n{"')
                                    if(clashnodes.find(': ') > -1):
                                        clashnodes = clashnodes.replace(': ', '": "')
                                    else:
                                        clashnodes = clashnodes.replace(':', '": "')
                                    clashnodes = clashnodes.replace(', ', '", "')
                                    clashnodes = clashnodes.replace('- {', '{"')
                                    clashnodes = '{"' + clashnodes + '"}'
                                if (clashnodes.find(':"}') > -1):
                                    clashnodes = clashnodes.replace(': "}', '": ""}')
                                elif (clashnodes.find(': "}') > -1):
                                    clashnodes = clashnodes.replace(':"}', '": ""}')
                                clashnodes = clashnodes.replace('{"Host": "', '{Host: ')
                                clashnodes = clashnodes.replace('"}"}', '}"}')
                                clashnodes = clashnodes.replace('"""', '""').strip('\n')
                                clashnodes = clashnodes.replace('{""}', '{}')
                                clashnodes = clashnodes.replace('{"HOST": "', '{HOST: ')
                                clashnodes = clashnodes.replace('"}", ', '}", ')
                                #print('Url-All-Nodes-Clash-New1:\n' + clashnodes)
                                onenode = ""
                                iii = 0
                                print('Line-194-clashnodes:\n' + clashnodes)
                                for clashnode in clashnodes.split('\n'):
                                    try:
                                        iii += 1
                                        clashnode = StrText.all_to_vmess(clashnode)
                                        wnode = json.loads(clashnode)
                                        if (wnode['type'] == 'ss'):
                                            onenode = 'ss://' +  base64.b64encode((wnode['cipher'] + ':' + wnode['password'] + '@' + wnode['server'] + ':' + wnode['port']).encode("utf-8")).decode("utf-8") + '#' + wnode['name']
                                        elif (wnode['type'] == 'trojan'):
                                            onenode = 'trojan://' + wnode['password'] + '@' + wnode['server'] + ':' + wnode['port'] + '#' + wnode['name']
                                        elif (wnode['type'] == 'vmess'):
                                            onenode = 'vmess://' + base64.b64encode((clashnode.replace('type": "vmess"','type": "none"')).encode("utf-8")).decode("utf-8")
                                        else:
                                            continue
                                        if (onenode != '' and expire.find(onenode) == -1 and allonenode.find(onenode) == -1):
                                            print('Line-188-已添加(clash-node-url-id:' + str(ii)+ ')-onenode-id-' + str(iii) + '\n' + onenode)
                                            allonenode = allonenode + onenode + '\n'
                                        else:
                                            print('Line-188-已过滤(clash-node-url-id:' + str(ii)+ ')-onenode-id-' + str(iii) + '-Find-Index-Allonenode:' + str(allonenode.find(onenode)) + '\n' + onenode)
                                    except Exception as ex:
                                        print('Line-193:' + str(ex) + '\nclashnode:\n' + clashnode + '\nclashnode:\n' + onenode)
                                #sub_link.append(base64.b64decode(allonenode).decode("utf-8"))
                            except Exception as ex:
                                print('Line-268:\n' + str(ex) +'\n' + clashnodes)
                    i = json.dumps(onode)
            except Exception as ex:
                print('Line-262:' + str(ex))
            if(nodeurl.find(onode_upurl) == -1):
                nodeurl = nodeurl + "\n" + i
        except Exception as ex:
            print('Line-132:' + str(ex))
    #转换Clash节点为正常混合节点并保存至本地vpei.txt
    print('Url-All-Clash-To-Mixed-Nodes:\n' + allonenode)
    res = base64.b64encode(allonenode.strip('\n').encode("utf-8")).decode("utf-8")
    LocalFile.write_LocalFile('./res/vpei.txt', res)

    # 将节点更新时间等写入配置文件
    if (len(nodeurl) > 1000):
        LocalFile.write_LocalFile('./res/node.json', nodeurl.strip('\n'))
else:
    print('Line-198:过滤名单读取失败，暂停运行。expire-' + expire)

# 逐条读取链接，并进行测试
onenode = ''
allnode = ''
cnnode = ''
tmpnode = ''
oldname = ''
newname = ''
ipdomain = ''
merged_link = []
merged_link_ping = []
class Department:#自定义的元素
    def __init__(self, id, name, id2):
        self.id = id
        self.name = name
        self.id2 = id2
datecont = time.strftime('%m-%d',time.localtime(time.time()))
#datecont = now.strftime("%Y-%m-%d %H:%M:%S")
ii = 0
iii = 0
if(len(sub_link)>0):
    for i in sub_link:
        #for j in i.split():
        for j in i.split('\n'):
            #print('deal site url id:' + str(ii))
            oldname = ''
            newname = ''
            ipdomain = ''
            try:
                if (j.find("#") > -1):
                    testj = j.split("#", 1)[0]
                else:
                    testj = j
                if (expire.find(testj) == -1 and tmpnode.find(testj) == -1):
                    #if (j.find("vmess://") == -1):
                    #    continue
                    print('\nLine-234-j-' + str(ii) + ':\n' + j)
                    ii += 1
                    if (j.find("vmess://") == 0):
                        #{alterId: 2,  cipher: auto,  name: '[11-07]|oslook|_2',  network: ws,  port: 80,  server: 7.yyds123.com,  tls: false,  type: vmess,  uuid: bac18e70-9964-3f99-805a-d809c4bdc6cb,  ws-path: /ny}
                        #  - {name: 🇨🇦 @SSRSUB-加拿大ss01-付费推荐:dlj.tf/ssrsub, server: ss1.ssrsub.com, port: 10443, type: ss, cipher: aes-128-gcm, password: suo.yt/ssrsub, plugin: obfs, plugin-opts: {mode: tls, host: n46hm52773.wns.windows.com}, udp: true}
                        #{
                        #  "v": "2",
                        #  "ps": "name-1.1.1.1",
                        #  "add": "1.1.1.1",
                        #  "port": "443",
                        #  "id": "892ebb75-7055-3007-8d16-356e65c6a49a",
                        #  "aid": "32",
                        #  "scy": "auto",
                        #  "net": "tcp",
                        #  "type": "http",
                        #  "host": "domain.com",
                        #  "path": "/v112EtCE3uAcU",
                        #  "tls": "tls",
                        #  "sni": "sni123"
                        #}
                        #- {name: US-107.173.157.168, server: 107.173.157.168, port: 443, type: vmess, uuid: 4f6aa0c3-7be1-4eaa-a64c-a23418070422, alterId: 6, cipher: auto, skip-cert-vertify: false, network: ws, ws-path: /b06fde1/, tls: True, ws-headers: {Host: www.shunxin.ml}}
                        onenode = base64.b64decode(j[8:]).decode('utf-8')

                        onenode = StrText.all_to_vmess(onenode)

                        #print('newnode-1:\n' + onenode)
                        node = json.loads(onenode.encode("utf-8").decode("utf-8"))
                        ipdomain = node['add']
                        newname = StrText.get_country(ipdomain) + '-' + ipdomain
                        try:
                            oldname = node['ps']
                            node['ps'] = newname #.decode("utf-8")
                            onenode = json.dumps(node, ensure_ascii = False)
                        except Exception as ex:
                            newname = oldname
                            print('Line-436:' + str(ex) + '\n' + onenode)
                        #vmess标题需要固定
                        #newname = '[' + datecont + ']-' + StrText.get_country(node['add']) + '-'+ str(ii).zfill(3) + '-' + node['add']
                        #onenode = node.replace('"ps": "'+StrText.get_str_btw(node, '"ps": "', '"'), '"ps": "'+ newname, 1)
                        print('newnode-0:\n' + onenode)
                        if (newname.find('.') > -1):
                            onenode = "vmess://" + base64.b64encode(onenode.encode("utf-8")).decode("utf-8")
                        else:
                            onenode = ''
                            newname = ''
                    elif (j.find("ss://") == 0):
                        if (j.find("#")==-1):
                            j = j + "#0"
                        #j = "ss://YWVzLTI1Ni1nY206bjh3NFN0bmJWRDlkbVhZbjRBanQ4N0VBQDIxMi4xMDIuNTQuMTYzOjMxNTcy#title"
                        #j = "ss://YWVzLTI1Ni1nY206bjh3NFN0bmJWRDlkbVhZbjRBanQ4N0VB@212.102.54.163:31572#title"
                        #j = "ss://YWVzLTEyOC1nY206c3VvLnl0L3NzcnN1Yg==@212.102.54.163:10443/?plugin=obfs-123
                        onenode = j.replace("/?", "#")
                        if (onenode.find("@") == -1):
                            jjs = onenode.split("#", 1) # 第二个参数为 1，返回两个参数列表
                            onenode = "ss://"+(base64.b64decode(jjs[0][5:].encode("utf-8")).decode("utf-8"))+"#"+jjs[1]
                        else:
                            jjs = onenode.split("@", 1) # 第二个参数为 1，返回两个参数列表
                            onenode = "ss://"+(base64.b64decode(jjs[0][5:].encode("utf-8")).decode("utf-8"))+"@"+jjs[1]
                        #ss://aes-256-gcm:n8w4StnbVD9dmXYn4Ajt87EA@212.102.54.163:31572#title
                        ipdomain = StrText.get_str_btw(onenode,"@",":")
                        ip_country = StrText.get_country(ipdomain)
                        newname = '[' + datecont + ']-' + ip_country + '-'+ str(ii).zfill(3) + '-' + ipdomain
                        oldname = onenode.split("#", 1)[1]
                        onenode = "ss://" + base64.b64encode(onenode.split("#", 1)[0][5:].encode("utf-8")).decode("utf-8") + "#" + newname
                    elif (j.find("trojan://") == 0):
                        if (j.find("#")==-1):
                            j = j + "#0"
                        onenode = j
                        #trojan://28d98f761aca9d636f44db62544628eb@45.66.134.219:443#%f0%9f%87%af%f0%9f%87%b5+%e6%97%a5%e6%9c%ac-45.66.134.219
                        #trojan://28d98f761aca9d636f44db62544628eb@45.66.134.219:443?sni=123#%f0%9f%87%af%f0%9f%87%b5+%e6%97%a5%e6%9c%ac-45.66.134.219
                        ipdomain = StrText.get_str_btw(j,"@",":")
                        ip_country = StrText.get_country(ipdomain)
                        oldname = j.split("#", 1)[1]
                        newname = '[' + datecont + ']-' + ip_country + '-'+ str(ii).zfill(3) + '-' + ipdomain
                        onenode = j.split("#", 1)[0] + "#" + newname
                    elif (j.find("vless://") == 0):
                        if (j.find("#")==-1):
                            j = j + "#0"
                        onenode = j
                        #vless://892ebb75-7055-3007-8d16-356e65c6a49a@45.66.134.219:443?encryption=none&security=tls&sni=45.66.134.219&type=ws&host=45.66.134.219&path=%2fv1t-vless#filename
                        ipdomain = StrText.get_str_btw(onenode,"@",":")
                        ip_country = StrText.get_country(ipdomain)
                        oldname = onenode.split("#", 1)[1]
                        newname = '[' + datecont + ']-' + ip_country + '-'+ str(ii).zfill(3) + '-' + ipdomain
                        onenode = onenode.split("#", 1)[0] + "#" + newname
                    elif (j.find("ssr://") == 0):
                        #14.152.92.79:12127:auth_aes128_sha1:aes-256-cfb:http_simple:Njh4ZGd1OWV5aWY=/?obfsparam=MGYwOTk2MDA3NzcudjIzZjduTTA&protoparam=NjAwNzc3OjE1NFQ4Yg&remarks=5pel5pysIFNhcmFwaGluZSAxNw&group=
                        onenode = base64.b64decode(j[6:]).decode('utf-8')
                        oldname = StrText.get_str_btw(onenode + '&','remarks=', '&')
                        ipdomain = onenode.split(':')[0]
                        ip_country = StrText.get_country(ipdomain)
                        newname = base64.b64encode((ip_country + '-'+ ipdomain).encode("utf-8")).decode("utf-8")
                        onenode = onenode.replace(oldname, newname)
                        onenode = "ssr://" + base64.b64encode(onenode.encode("utf-8")).decode("utf-8")
                        onenode = ''
                        ii = ii - 1
                    else:
                        ii = ii - 1
                        continue
                    try:
                        if (onenode != '' and expire.find(onenode) == -1 and IsValid.isIPorDomain(ipdomain) and tmpnode.find(onenode) == -1 and (onenode.find("vmess://") == 0 or onenode.find("ss://") == 0 or onenode.find("trojan://") == 0 or onenode.find("vless://") == 0)):
                            print('Rename node ' + oldname.strip('\n') + ' to ' + newname)
                            allnode = allnode + '\n' + onenode   #新旧节点信息都加入作对比。
                            if(len(allnode) > 102400000):
                                #res = base64.b64encode(allnode.strip('\n').encode("utf-8")).decode("utf-8")
                                LocalFile.write_LocalFile('./res/node' + ii + '.txt', allnode.strip('\n'))
                                allnode = ''
                            if(newname.find(u'中国') > -1 or newname.find(u'省') > -1 or newname.find(u'上海') > -1 or newname.find(u'北京') > -1 or newname.find(u'重庆') > -1 or newname.find(u'内蒙') > -1):
                                cnnode = cnnode + '\n' + onenode
                            else:
                                merged_link.append(onenode)
                                tmpnode = tmpnode + ',' + j + ',' + onenode   #新旧节点信息都加入作对比。
                                if(iii < 200):
                                    try:
                                        iii += 1
                                        #ipdomain = '114.114.114.114'
                                        stime = 0
                                        print('ipdomain:' + ipdomain + '-ipdomain-ping:' + str(ping(ipdomain, unit='ms')))
                                        stime = int(str(ping(ipdomain, unit='ms')).replace('False', '9999').replace('None', '9999')) #PingIP.get_ping_time(ipdomain)
                                        if(stime <= 0):
                                            stime = 9999
                                        merged_link_ping.append(Department(stime, onenode, '1'))
                                        print('Line-366-已添加(' + str(ii)+ '-Expire-Len:' + str(len(expire)) + '):\n' + onenode)
                                    except Exception as ex:
                                        print('Line-363:' + str(ex) + '\nipdomain:' + ipdomain + '\nonenode:' + onenode)
                                else:
                                    print('Line-366-已过滤(' + str(ii)+ '-Expire-Len:' + str(len(expire)) + ')-FindIndex:' + str(tmpnode.find(onenode)) + '):\n' + onenode)
                            # print(newname + '---------' + newname.find('省')+ '*' + newname.find(u'省'))
                            #print('Line-401:onenode-' + onenode)                            
                        else:
                            print('Line-425-已过滤(' + str(ii)+ '-Expire-Len:' + str(len(expire))+ ')-FindIndex:' + str(tmpnode.find(onenode)) ) #+ ' onenode:' + onenode + ' expire.find(onenode):' +  str(expire.find(onenode)) + '\nIsValid.isIP(ipdomain):' +  str(IsValid.isIP(ipdomain)) + ' IsValid.isIPorDomain(ipdomain):' +  str(IsValid.isIPorDomain(ipdomain)) + ' allnode.find(onenode):' +  str(allnode.find(onenode)) + ' allnode:\n' + allnode)
                    except Exception as ex:
                        print('Line-524:' + str(ex) + '\nConT:' + j)
            except Exception as ex:
                print('Line-444:' + str(ex) + '\noldnode:' + j + '\nonenode:' + onenode)
        print('[' + str(ii) + '][Sub merged success]')
    print(merged_link)
    # 合并整理完成的节点，生成Clash配置文件
    res = base64.b64encode(cnnode.strip('\n').encode("utf-8")).decode("utf-8")
    LocalFile.write_LocalFile('./out/nodecn.txt', res)
    #res = base64.b64encode(allnode.strip('\n').encode("utf-8")).decode("utf-8")
    LocalFile.write_LocalFile('./res/node.txt', allnode.strip('\n'))
else:
    print('Line-421:sub_link:' + str(sub_link))

#print(merged_link_ping)
#划重点#划重点#划重点----排序操作
#cmpfun = operator.attrgetter('id','name')#参数为排序依据的属性，可以有多个，这里优先id，使用时按需求改换参数即可
merged_link_ping.sort(key = operator.attrgetter('id','name'))#使用时改变列表名即可 
#划重点#划重点#划重点----排序操作
#此时Departs已经变成排好序的状态了，排序按照id优先，其次是name，遍历输出查看结果
for depart in merged_link_ping:
    print('\nmerged_link_ping:' + str(depart.id) + '-' + depart.name)
#print(sorted(merged_link_ping, key=lambda x:x[1]))

allnodetxt = ''
if(len(merged_link_ping) > 0):
    try:
        #for i in merged_link:
        for depart in merged_link_ping:
	        #print(i)
	        #if (i.find("vmess://") == 0):
	        #    bs = "vmess://" + base64.b64encode(json.dumps(i).encode("utf-8")).decode("utf-8")
	        #else:
	        #    bs = i
            onenodeurl = depart.name
            print('onenodeurl:\n' + onenodeurl)
            if (allnodetxt.find(onenodeurl) == -1):
                allnodetxt = allnodetxt + onenodeurl + '\n'
        res = base64.b64encode(allnodetxt.encode("utf-8")).decode("utf-8")
        LocalFile.write_LocalFile('./ipfs/tmp/new-node.txt', res)
        print('allnodetxt:\n' + allnodetxt)
        #print(res)
        print('混合节点已生成，下一步将生成Clash节点。')
    except Exception as ex:
        print('Line-483:' + str(ex) + '\nlen(merged_link_ping):' + len(merged_link_ping))
else:
    print('Line-416-merged_link:\n' + str(merged_link_ping))

# 逐条读取链接，并生成CLASH订阅链接，进行测试 
clashurl = ''
openclashurl = ''
clash_node_url = ''
clashname = ''
telename = ''
nodecount = 96
if(len(allnodetxt) > 0):
    for j in allnodetxt.split():
        try:
            #如果已经添加则跳过
            if (nodecount > 0):
                onenode = ''
                print('Line-457-j:\n' + j)
                if (j.find("vmess://") == 0):
                    j = base64.b64decode(j[8:].encode("utf-8")).decode("utf-8")
                    j = j.replace('\'', '')
                    #newname = StrText.get_str_btw(j, "ps: \"","\"");- server:139.155.22.227
                    #v:2
                    #name: | 2.14Mb
                    #port:49110
                    #uuid:f7675b7e-59bf-435c-ac03-dc2482f27e5d
                    #alterId:64
                    #network:tcp
                    #type:
                    #host:
                    #path:/
                    #tls:
                    #  name: 🇨🇳-中国-139.155.22.227
                    #  cipher: auto
                    node = json.loads(j)
                    node['ps'] = '\'' + node['ps'] + '\''
                    j = json.dumps(node, ensure_ascii = False)
                    
                    #print('newname:' + newname)
                    #print('onenode:' + j)
                    #{"tls": "false", "type": "none", "scy": "auto", "ps": "\ud83c\uddef\ud83c\uddf5-\u65e5\u672c-54.238.161.11", "aid": "4", "path": "/v2ray", "net": "ws", "port": "80", "id": "261aeb5f-b6f7-359c-a321-9794bf344e12", "add": "54.238.161.11"}
                    if(j.find('ps":')>-1 or j.find('"v":') > -1 or j.find('"aid":') > -1):
                        j = j.replace(' ', '').replace('"', '') #.replace('\'', '')
                        j = j.replace(',', '\n').replace('\n\n', '\n')
                        j = j.replace('{\n', '').replace('\n}', '\n')
                        if (j.find('name:') == -1):
                            j = j.replace('ps:', 'name:')
                        if (j.find('cipher:') == -1):
                            j = j.replace('scy:', 'cipher:')
                        if (j.find('network:') == -1):
                            j = j.replace('net:', 'network:')
                        if (j.find('server:') == -1):
                            j = j.replace('add:', 'server:')
                        if (j.find('alterId:') == -1):
                            j = j.replace('aid:', 'alterId:')
                        if (j.find('uuid:') == -1):
                            j = j.replace('id:', 'uuid:')
                        #j = j.replace('path:', 'ws-path:')
                        j = j.replace('\n', '\n  ').replace(':', ': ')

                        #newname = StrText.get_str_btw(j, 'name: ', '\n')
                        #pdb.set_trace()
                        #if(j.find(newname) > -1):
                        #    j = j.replace('name: ' + newname + '\n', 'name: \'' + newname + '\'\n')
                        j = j.replace('type: none\n', 'type: vmess\n') #类型tcp?
                        j = j.replace('type: \n', 'type: vmess\n') #类型type为空时，则填入vmess
                        j = j.replace('tls:tls\n', 'tls: true\n') #类型type为空时，则填入vmess
                        j = j.replace('tls:none\n', 'tls: false\n') #类型type为空时，则填入vmess
                        j = j.replace('tls:\n', 'tls: false\n') #类型type为空时，则填入vmess
                        j = j.replace('tls: tls\n', 'tls: true\n') #类型type为空时，则填入vmess
                        j = j.replace('tls: none\n', 'tls: false\n') #类型type为空时，则填入vmess
                        j = j.replace('tls: \n', 'tls: false\n') #类型type为空时，则填入vmess
                        j = j.strip(' ').strip('{').strip('}')

                        if(j.find('cipher') == -1):
                            j = j + '\n  cipher: auto'
                    #elif(j.find('"v":')>-1):
                        #{"v": 2, "tls": "none", "path": "/", "host": "", "port": 58443, "net": "ws", "add": "159.223.67.223", "type": "", "id": "07c40cf6-db51-4179-cce7-5607cc0d301b", "aid": 64}
                    #else:
                    #    j = j.strip('\n') #其他格式转化备用
                    
                    #j = j.lstrip('\n')
                    #j = j.rstrip('\n')
                    onenode = '- ' + j
                elif (j.find("trojan://") == 0):
                    #trojan://28d98f761aca9d636f44db62544628eb@45.66.134.219:443#%f0%9f%87%af%f0%9f%87%b5+%e6%97%a5%e6%9c%ac-45.66.134.219
                    #trojan://d8aacec8-e256-427b-a927-0c6013f6595b@t4.ssrsub.com:833?sni=123123#%f0%9f%87%af%f0%9f%87%b5+%e6%97%a5%e6%9c%ac-45.66.134.219
                    newname = j.split("#", 1)[1]
                    password = StrText.get_str_btw(j, "trojan://", "@")
                    server = StrText.get_str_btw(j,"@",":")
                    if (j.find("?sni=")>-1):
                        port = StrText.get_str_btw(StrText.get_str_btw(j,"@","#"),":","?")
                        onenode = '- name: \'' + newname + '\'\n  server: ' + server + '\n  port: ' + port + '\n  type: trojan\n  password: ' + password + '\n  sni: ' + StrText.get_str_btw(j, "?sni=", "#") + '\n  skip-cert-verify: true'
                    else:
                        port = StrText.get_str_btw(j,"@","#").split(":", 1)[1]
                        onenode = '- name: \'' + newname + '\'\n  server: ' + server + '\n  port: ' + port + '\n  type: trojan\n  password: ' + password + '\n  skip-cert-verify: true'
                elif (j.find("ss://") == 0):
                    #j = "ss://aes-256-gcm:n8w4StnbVD9dmXYn4Ajt87EA@212.102.54.163:31572#title"
                    jj = j.split("#", 1)
                    onenode = 'ss://' + base64.b64decode(jj[0][5:].encode("utf-8")).decode("utf-8") + "#" + newname
                    cipher = StrText.get_str_btw(onenode, "ss://", ":")
                    newname = jj[1]
                    password = StrText.get_str_btw(StrText.get_str_btw(onenode, "ss://", "#"), ":", "@")
                    server = StrText.get_str_btw(onenode, "@", ":")
                    port = StrText.get_str_btw(onenode, "@", "#").split(":", 1)[1]
                    onenode = '- cipher: ' + cipher + '\n  name: \'' + newname + '\'\n  password: ' + password + '\n  server: ' + server + '\n  port: ' + port + '\n  type: ss'
                else:
                    continue
                if (onenode != '' and newname != '' and clashurl.find(onenode) == -1 and clashname.find(newname) == -1):
                    nodecount = nodecount - 1
                    clashurl = clashurl + onenode + '\n'
                    openclashurl = openclashurl + onenode + '\n  udp: true\n'
                    clash_node_url = clash_node_url + '\n' + onenode.replace('- ', '- {"').replace('\'', '').replace(': ', '": "').replace('\n  ', '", "') + '"}'

                    clashname = clashname + '  - "' + newname + '"\n'
                    if(newname.find('伊朗') == -1):
                        telename = telename + '  - "' + newname + '"\n'
                print('Line-558-onenode:\n' + onenode)
            else:
                print('\n[保留96条节点，忽略多余节点]:\n' + j)
        except Exception as ex:
            print('Line-578:' + str(ex))
    clashname = clashname.rstrip('\n')
    clashname = clashname.replace('\n\n', '\n')
    print('clashname:\n' + clashname)

    telename = telename.rstrip('\n')

    clashurl = clashurl.rstrip('\n')
    clashurl = clashurl.replace('\n\n', '\n')

    openclashurl = openclashurl.rstrip('\n')
    openclashurl = openclashurl.replace('\n\n', '\n')
    print('clashurl:\n' + clashurl)

    # 合并替换Clash节点信息，下载后回车行丢失
    #clash_1 = NetFile.down_res_file(resurl, 'clash-1.txt', 240, 120)
    #clash_2 = NetFile.down_res_file(resurl, 'clash-2.txt', 240, 120)
    #clash_1 = ""
    if(clashname != ''):
        with open("./res/clash-1.txt", "r", encoding='utf-8') as f:  # 打开文件
            clash_1 = f.read()  # 读取文件

        with open("./res/clash-2.txt", "r", encoding='utf-8') as f:  # 打开文件
            clash_2 = f.read()  # 读取文件
        tmp = clash_1.replace("clash-url.txt", clashurl)
        tmp = tmp.replace("clash-name.txt", clashname)
        tmp = tmp.replace("tele-name.txt", telename)
        tmp = tmp.replace("clash-2.txt", clash_2)
        tmp = tmp.replace('\nexternal-ui: "/usr/share/openclash/dashboard"', '')
        # 写入节点文件到本地Clash文件
        LocalFile.write_LocalFile('./out/clash.yaml', tmp)
        #print(tmp)
        print('Clash文件成功写入。')

        tmp = clash_1.replace("clash-url.txt", openclashurl)
        tmp = tmp.replace("clash-name.txt", clashname)
        tmp = tmp.replace("tele-name.txt", telename)
        tmp = tmp.replace("clash-2.txt", clash_2)
        # 写入节点文件到本地Clash文件
        #LocalFile.write_LocalFile('./out/openclash.yaml', tmp + '\nexternal-ui: "/usr/share/openclash/dashboard"')
        LocalFile.write_LocalFile('./out/openclash.yaml', tmp)
        #print(tmp)
        print('OpenClash文件成功写入。(添加UDP为True的参数)')

        #with open("./res/clash-pc.yaml", "r", encoding='utf-8') as f:  # 打开文件
        #    clash_pc = f.read()  # 读取文件
        tmp = 'proxies:' + clash_node_url
        LocalFile.write_LocalFile('./out/clashnode.txt', tmp)
        #print(tmp)
        print('ClashNode文件成功写入。(纯节点)')
else:
    print('Line-625:数据获取失败，暂停生成CLASH等链接。\nallnodetxt:' + allnodetxt)