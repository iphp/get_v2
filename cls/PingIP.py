#!/usr/bin/env python3

import requests
import os
import time
import socket
import json
import re
import subprocess
from io import StringIO
import multiprocessing
import time
import sys
from ip import QQwry
from cls.IsValid import IsValid

import struct
import select
import platform
import zlib
import threading
import logging
import functools
import errno

class PingIP():
    def get_ping_time(ip):
        num = 0
        try:
            result = subprocess.call('ping -w 1000 -n 1 ' + ip,stdout=subprocess.PIPE,shell=True)
            if result == 0:
                h = subprocess.getoutput('ping ' + ip)
                num = h.split('平均 = ')[1].replace('ms', '')
        except:
            num = 0
        return num

    def check_alive(ip):
        result = subprocess.call('ping -w 1000 -n 1 %s' %ip,stdout=subprocess.PIPE,shell=True)
        if result == 0:
            h = subprocess.getoutput('ping ' + ip)
            returnnum = h.split('平均 = ')[1]
            info = ('\033[32m%s\033[0m 能ping通，延迟平均值为：%s' %(ip,returnnum))
            print('\033[32m%s\033[0m 能ping通，延迟平均值为：%s' %(ip,returnnum))
            #return info
        else:
            with open('notong.txt','a') as f:
                f.write(ip)
            info = ('\033[31m%s\033[0m ping 不通！' % ip)
            #return info
            print('\033[31m%s\033[0m ping 不通！' % ip)
            
    def ping8(dest_addr: str, timeout: int = 4, unit: str = "s", src_addr: str = None, ttl: int = None, seq: int = 0, size: int = 56, interface: str = None) -> float:
        """
        Send one ping to destination address with the given timeout.

        Args:
            dest_addr: The destination address, can be an IP address or a domain name. Ex. "192.168.1.1"/"example.com"
            timeout: Time to wait for a response, in seconds. Default is 4s, same as Windows CMD. (default 4)
            unit: The unit of returned value. "s" for seconds, "ms" for milliseconds. (default "s")
            src_addr: The IP address to ping from. This is for multiple network interfaces. Ex. "192.168.1.20". (default None)
            interface: LINUX ONLY. The gateway network interface to ping from. Ex. "wlan0". (default None)
            ttl: The Time-To-Live of the outgoing packet. Default is None, which means using OS default ttl -- 64 onLinux and macOS, and 128 on Windows. (default None)
            seq: ICMP packet sequence, usually increases from 0 in the same process. (default 0)
            size: The ICMP packet payload size in bytes. If the input of this is less than the bytes of a double format (usually 8), the size of ICMP packet payload is 8 bytes to hold a time. The max should be the router_MTU(Usually 1480) - IP_Header(20) - ICMP_Header(8). Default is 56, same as in macOS. (default 56)

        Returns:
            The delay in seconds/milliseconds, False on error and None on timeout.

        Raises:
            PingError: Any PingError will raise again if `ping3.EXCEPTIONS` is True.
        """
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
        except PermissionError as err:
            if err.errno == errno.EPERM:  # [Errno 1] Operation not permitted
                _debug("`{}` when create socket.SOCK_RAW, using socket.SOCK_DGRAM instead.".format(err))
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_ICMP)
            else:
                raise err
        with sock:
            if ttl:
                try:  # IPPROTO_IP is for Windows and BSD Linux.
                    if sock.getsockopt(socket.IPPROTO_IP, socket.IP_TTL):
                        sock.setsockopt(socket.IPPROTO_IP, socket.IP_TTL, ttl)
                except OSError as err:
                    _debug("Set Socket Option `IP_TTL` in `IPPROTO_IP` Failed: {}".format(err))
                try:
                    if sock.getsockopt(socket.SOL_IP, socket.IP_TTL):
                        sock.setsockopt(socket.SOL_IP, socket.IP_TTL, ttl)
                except OSError as err:
                    _debug("Set Socket Option `IP_TTL` in `SOL_IP` Failed: {}".format(err))
            if interface:
                sock.setsockopt(socket.SOL_SOCKET, SOCKET_SO_BINDTODEVICE, interface.encode())  # packets will be sent from specified interface.
                _debug("Socket Interface Binded:", interface)
            if src_addr:
                sock.bind((src_addr, 0))  # only packets send to src_addr are received.
                _debug("Socket Source Address Binded:", src_addr)
            thread_id = threading.get_native_id() if hasattr(threading, 'get_native_id') else threading.currentThread().ident  # threading.get_native_id() is supported >= python3.8.
            process_id = os.getpid()  # If ping() run under different process, thread_id may be identical.
            icmp_id = zlib.crc32("{}{}".format(process_id, thread_id).encode()) & 0xffff  # to avoid icmp_id collision.
            try:
                send_one_ping(sock=sock, dest_addr=dest_addr, icmp_id=icmp_id, seq=seq, size=size)
                delay = receive_one_ping(sock=sock, icmp_id=icmp_id, seq=seq, timeout=timeout)  # in seconds
            except errors.Timeout as err:
                _debug(err)
                _raise(err)
                return None
            except errors.PingError as err:
                _debug(err)
                _raise(err)
                return False
            if delay is None:
                return None
            if unit == "ms":
                delay *= 1000  # in milliseconds
            return delay