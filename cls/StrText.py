#!/usr/bin/env python3

import requests
import os
import time
import socket
import json
from ip import QQwry
from cls.IsValid import IsValid
from cls.LocalFile import LocalFile

class StrText():

    # 从字符中取两不同字符串中间的字符，print(sub_link)
    def get_str_btw(s, f, b):
        par = s.partition(f)
        return (par[2].partition(b))[0][:]

    # 通过域名获取IP
    def getIP(domain):
      try:
        print('get-domain-Ip:' + domain)
        domain = socket.getaddrinfo("www.baidu.com", 'http')
        return domain[0][4][0]
      except:
        return '127.0.0.1'

    def get_ip_list(domain): # 获取域名解析出的IP列表
        ip_list = []
        try:
            addrs = socket.getaddrinfo(domain, None)
            for item in addrs:
                if item[4][0] not in ip_list:
                    ip_list.append(item[4][0])
        except Exception as e:
            # print(str(e))
            pass
        return ip_list
            
    # 通过IP获取国家名称并添加国旗符号，print(get_country) 
    def get_country(ipdomain):
        global ip_info
        ip_country = ''
        ipdomainurl = ''
        try:
            q = QQwry()
            q.load_file('./res/qqwry.dat')
            #q.lookup('8.8.8.8')
            if(IsValid.isIP(ipdomain) == False):
                domain = ipdomain
                ipdomain = StrText.getIP(ipdomain)
                print(domain + '---' + ipdomain)
            #print('QQwryIp is loaded. ' + str(q.is_loaded()) + '-' + str(IsValid.isIP(ipdomain)) + '-' + ipdomain + '-' + q.lookup(ipdomain)[0]) #+ '-' + q.lookup(ipdomain)[1]) #('国家', '省份')
            if(q.is_loaded() == True):
                ip_country = q.lookup(ipdomain)[0]
                if(ip_country == 'None'):
                    ip_country = ''
            if(ip_country == ''):
                #rq = requests.get("http://ip-api.com/json/{}?lang=zh-CN".format(node['add']), timeout=30) #连接超时 和 读取超时 均为30
                ipdomainurl = 'http://ip-api.com/json/' + ipdomain + '?lang=zh-CN'
                rq = requests.get(ipdomainurl, timeout=10) #连接超时 和 读取超时 均为30
                if (rq.status_code == 200):
                    ip_info = json.loads(rq.content)
                    if (ip_info['status'] == 'success'):
                        ip_country = ip_info['country']
                else:
                    print('Line-128: download sub error on link: [' + str(rq.status_code) + ']' + ipdomainurl)
                    ipdomainurl = 'http://ip.360.cn/IPQuery/ipquery?ip=' + ipdomain
                    rq = requests.get(ipdomainurl, timeout=10)
                    if (rq.status_code == 200):
                        ip_info = json.loads(rq.content)
                        if (ip_info['errno'] == '0'):
                            #ip_country = ip_info['data'].encode('utf-8').decode('unicode_escape')
                            ip_country = ip_info['data'].encode('utf-8').decode('utf-8')
                    else:
                        print('Line-137: download sub error on link: [' + str(rq.status_code) + ']' + ipdomainurl)
                        ipdomainurl = 'http://ipinfo.io/' + ipdomain + '?token=7f459101a94acc'
                        rq = requests.get(ipdomainurl, timeout=10)
                        if (rq.status_code == 200):
                            ip_info = json.loads(rq.content)
                            ip_country = ip_info['country'].encode('utf-8').decode('utf-8')
                        else:
                            ip_country = "未知"
                            print('Line-145: download sub error on link: [' + str(rq.status_code) + ']' + ipdomainurl)
            #print(ip_country)
            ip_country = ip_country.encode('utf-8').decode('utf-8')
            ip_country = ip_country.replace('台湾省', '台湾', 1)
            #if(len(ip_country)>3):
            #    old_ip_country = ip_country[0:3]
            #else:
            #    old_ip_country = ip_country
            emoji = {
                'US': '🇺🇸', 'HK': '🇭🇰', 'SG': '🇸🇬', 'JP': '🇯🇵', 'TW': '🇹🇼', 'CA': '🇨🇦', 'GB': '🇬🇧', 'CN': '🇨🇳', 'NL': '🇳🇱',
                'TH': '🇹🇭', 'BE': '🇧🇪', 'IN': '🇮🇳', 'IT': '🇮🇹', 'PE': '🇵🇪', 'RO': '🇷🇴', 'AU': '🇦🇺', 'DE': '🇩🇪', 'RU': '🇷🇺',
                'KR': '🇰🇷', 'DK': '🇩🇰', 'PT': '🇵🇹', 'CY': '🇨🇾', 'ES': '🇪🇸', 'RELAY': '🏁', 'NOWHERE_LAND': '🇦🇶',
                '澳大利亚': '🇦🇺', '阿尔巴尼亚': '🇦🇱', '阿根廷': '🇦🇷', '比利时': '🇧🇪', '秘鲁': '🇵🇪', '波兰': '🇵🇱', '德国': '🇩🇪', '俄罗斯': '🇷🇺',
                '法国': '🇫🇷', '加拿大': '🇨🇦', '罗马尼亚': '🇷🇴', '日本': '🇯🇵', '韩国': '🇰🇷', '荷兰': '🇳🇱', 
                '美国': '🇺🇸', '南非': '🇿🇦', '挪威': '🇳🇴', '葡萄牙': '🇵🇹', '瑞典': '🇸🇪', '泰国': '🇹🇭', '台湾': '🇹🇼', '斯洛伐克': '🇸🇰',
                '瑞士': '🇨🇭', '乌克兰': '🇺🇦', '西班牙': '🇪🇸', '香港': '🇭🇰', '新加坡': '🇸🇬', '新西兰': '🇳🇿', 
                '意大利': '🇮🇹', '伊朗': '🇮🇷', '英国': '🇬🇧', '印度': '🇮🇳', '智利': '🇨🇱', '中国': '🇨🇳', '欧洲': '🇪🇸',
            }
            if ip_country in emoji:
                ip_country = emoji[ip_country] + '-' + ip_country
            else:
                # 方法三: 最快，推荐方法
                for k,v in emoji.items(): 
                    if(ip_country.find(k) > -1):
                        ip_country = v + '-' + ip_country
                        #print('n:' + v)
                        break
            if(ip_country.find('-') == -1 and (ip_country.find('省') == -1 or ip_country.find('市') == -1)):
                ip_country = emoji['NOWHERE_LAND'] + '-' + ip_country
        except Exception as ex:
            print('Line-113-StrText: ' + str(ex) + '\n' + ipdomainurl + '\n' + ipdomain)
        return ip_country.encode('utf8').decode('utf-8')

    # 非标准格式的vmess明文地址转化为标准格式的vmess明文
    def all_to_vmess(onenode):
        try:
            # onenode = '{"add":"104.255.66.87","v":"2","ps":"CA_940:001","port":38922,"id":"f3e846c1-d8e4-42df-86d4-f4e5028630d8","aid":"8","net":"tcp","type":"","host":"","path":"/:011","tls":""}'
            # onenode = '{"add": "v7.ssrsub.com", "v": "2", "ps": "\'v7.ssrsub.com\'", "port": "168", "id": "e54a480c-77e3-41ca-8f8b-17ffb50dbd08", "aid": "0", "net": "ws", "type": "", "host": "", "path": "/ssrsub", "tls": "tls"}'
            # onenode = '{name: 🇯🇵JP-35.77.5.55, server: 034.ap.pop.bigairport.net, port: 12356, type: vmess, uuid: a6f82e7d-6e99-4a4e-8981-8e91453c13f7, alterId: 1, cipher: auto, skip-cert-vertify: false, network: ws, ws-path: /, tls: True, ws-headers: {Host: t.me/vpnhat}}'
            # onenode = '{add:v1-asw-sg-14.niaoyun.online,port:666,id:b9cc1e88-5db0-37ff-840a-b882345e22d1,aid:1,scy:auto,net:ws,host:v1-asw-sg-14.niaoyun.online,path:/niaocloud,tls:,sni:,v:2,ps:Relay_新加坡-_7234,type:none,serverPort:0,nation:}'
            print('oldnode-0:\n' + onenode)
            #onenode = onenode.strip('- ')
            newnode = '{\n'
            onenode = onenode.replace('\r', ',').replace('\n', ',')
            onenode = onenode.replace('"', '').replace('\'', '')
            onenode = onenode.replace('{', '').replace('}', '')
            for i in onenode.split(','):
                if(i.find(':') > -1):
                    a = i.split(':', 1)[0].strip(' ')
                    b = i.split(':', 1)[1].strip(' ')
                    newnode = newnode + '  "' + a + '": "' + b + '",\n'
            onenode = newnode.strip(',\n') + '\n}'
            #print('newnode-1:\n' + onenode)
            if(onenode.find('alterId":')>-1):
                onenode = onenode.replace('name":', 'ps":')
                onenode = onenode.replace('server":', 'add":')
                onenode = onenode.replace('uuid":', 'id":')
                onenode = onenode.replace('alterId":', 'aid":')
                onenode = onenode.replace('cipher":', 'scy":')
                onenode = onenode.replace('network":', 'net":')
                onenode = onenode.replace('ws-path":', 'path":')
                #onenode = onenode.replace('"host":', '"host":')

            if(onenode.find('ws-headers":') > -1):
                onenode = onenode.replace('ws-headers": "Host:','host": "').replace('" ','"')
                onenode = onenode.replace('ws-headers": "host:','host": "').replace('" ','"')
                 
            #互相转换: 文本转换成字典
            if(onenode.find('"ps":') == -1):
                onenode = onenode.replace('\n}', ',\n  "ps": "tmp"\n}')
                print('[ps] is added.')
            #print('newnode-2:\n' + onenode)
            return onenode
        except Exception as ex:
            print('Line-167-StrText: ' + str(ex) + '\n' + onenode)
            LocalFile.write_LocalFile('./ipfs/tmp/err.log', 'Line-167-StrText: ' + str(ex) + '\n' + onenode)
            return ''
            
    # 非标准格式的vmess明文地址转化为标准格式的vmess明文
    def all_to_vmess2(ipdomain):
        print('NewNode1:\n' + onenode)
        if(onenode.find('ps:') > -1):
            if(oldname.find('ps:\'') > -1):
                oldname = StrText.get_str_btw(oldname, 'ps:\'', '\',')
            elif(oldname.find('ps:"') > -1):
                oldname = StrText.get_str_btw(oldname, 'ps:"', '\",')
            else:
                oldname = StrText.get_str_btw(oldname, 'ps:', ',')
            if(len(oldname) > 0):
                onenode = onenode.replace(oldname, 'tmpname')
        else:
            if(oldname.find('name:\'') > -1):
                oldname = StrText.get_str_btw(oldname, 'name:\'', '\',')  #空格全替换掉，名称IP:PORT的就会出错。
            elif(oldname.find('name:"') > -1):
                oldname = StrText.get_str_btw(oldname, 'name:"', '\",')
            else:
                oldname = StrText.get_str_btw(oldname, 'name:', ',')

        if(len(oldname)  > 0):
            onenode = onenode.replace(oldname, 'tmpname')
        onenode = onenode.replace('\'', '').replace('"', '')
        onenode = onenode.replace(' ', '') #空格全替换掉，名称IP:PORT的就会出错。现已经对名称进行替换，故可以去掉全部空格。
        #onenode = onenode.replace(',}', '}')
        onenode = onenode.replace('\n', ',')
        onenode = onenode.replace('\r', ',')
        onenode = onenode.replace(',,', ',')
        onenode = onenode.replace(',,', ',')
        onenode = onenode.replace(',,', ',')
        onenode = onenode.replace('{,','{')
        onenode = onenode.replace(',}','}')

        #忽略{name: 🇯🇵JP-35.77.5.55, server: 034.ap.pop.bigairport.net, port: 12356, type: vmess, uuid: a6f82e7d-6e99-4a4e-8981-8e91453c13f7, alterId: 1, cipher: auto, skip-cert-vertify: false, network: ws, ws-path: /, tls: True, ws-headers: {Host: t.me/vpnhat}}
        if(onenode.find('ws-headers:') > -1):
            onenode = onenode.replace('ws-headers:{Host:','Host:')
            onenode = onenode.replace('}}',',}')

        if(onenode.find('alterId:')>-1):
            #onenode = onenode.replace('name:', 'ps:')
            onenode = onenode.replace('server:', 'add:')
            onenode = onenode.replace('uuid:', 'id:')
            onenode = onenode.replace('alterId:', 'aid:')
            onenode = onenode.replace('cipher:', 'scy:')
            onenode = onenode.replace('network:', 'net:')
            onenode = onenode.replace('ws-path:', 'path:')
            #onenode = onenode.replace('"host":', '"host":')
        print('NewNode2:\n' + onenode)
        onenode = onenode.strip('- ')
        onenode = onenode.replace(',,', ',')
        onenode = onenode.replace(' ', '')
        onenode = onenode.replace(':', '": "')
        onenode = onenode.replace(',', '",\n  "')
        onenode = onenode.replace('{', '{\n  "')
        onenode = onenode.replace('\n\n', '\n')
        onenode = onenode.replace('"\n', '"')
        onenode = onenode.replace('"}', '"\n}')
        onenode = onenode.replace(': ",', ': "",')
        onenode = onenode.replace(': "\n', ': ""\n')
        onenode = onenode.replace(',\n  "}', '"\n}')
        onenode = onenode.replace('}",\n  "', '}')

        if(onenode.find('\n}') == -1 and onenode.find('"}') == -1):
            onenode = onenode.replace('}', '"\n}')
            
        print('NewNode3:\n' + onenode)
        if(onenode.find('\n}') == -1 and onenode.find('"}') == -1 and onenode.find(',}') == -1):
            onenode = onenode.replace('}', '"\n}')
        #{"add":"104.255.66.87","v":"2","ps":"CA_940","port":38922,"id":"f3e846c1-d8e4-42df-86d4-f4e5028630d8","aid":"8","net":"tcp","type":"","host":"","path":"/","tls":""}
        #{"add": "v7.ssrsub.com", "v": "2", "ps": "'v7.ssrsub.com'", "port": "168", "id": "e54a480c-77e3-41ca-8f8b-17ffb50dbd08", "aid": "0", "net": "ws", "type": "", "host": "", "path": "/ssrsub", "tls": "tls"}
        
        if(onenode.find('{name: \'') > -1):
            print('Line-446:\n'+ base64.b64decode(j[8:]).decode('utf-8') + '\n' + onenode)
        #    print(onenode)
        #elif(onenode.find('"v":')>-1):
        #    if(onenode.find('"ps":')==-1):
        #        temp = onenodeson.loads(onenode)
        #        temp.update({"ps": "tmp"})
        #        onenode = onenodeson.dumps(temp)                    
        #互相转换: 文本转换成字典
        if(onenode.find('"ps":') == -1):
            onenode = onenode.replace('\n}', ',\n  "ps": "tmp"\n}')
            print('[ps] is added.')