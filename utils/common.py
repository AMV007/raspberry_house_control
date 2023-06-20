#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys,os
import time as tm
from datetime import datetime, time as datetime_time, timedelta
from subprocess import PIPE, Popen

# for html
import requests
from bs4 import BeautifulSoup

import config

def get_mac_address():
    if sys.platform == 'win32':
        for line in os.popen("ipconfig /all"):
            if line.lstrip().startswith('Physical Address'):
                mac = line.split(':')[1].strip().replace('-', ':')
                break
    else:
        for line in os.popen("/sbin/ifconfig"):
            if line.find('Ether') > -1:
                mac = line.split()[4]
                break
    return mac

def get_time(time=None):
    if time is None:
        return datetime.now().strftime('%d-%m-%Y %H:%M:%S')
    else:
        return time.strftime('%d-%m-%Y %H:%M:%S')

def get_cpu_temperature():
    """get cpu temperature using vcgencmd"""
    process = Popen(['vcgencmd', 'measure_temp'], stdout=PIPE)
    output, _error = process.communicate()
    # converting from string to bytes, this will not work for python less 3
    output = output.decode('utf-8')
    return float(output[output.index('=') + 1:output.rindex("'")])
