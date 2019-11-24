#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys,os
import time as tm
from datetime import datetime, time as datetime_time, timedelta
from subprocess import PIPE, Popen

#for weather
import pyowm

# for html
import requests
from bs4 import BeautifulSoup

import config

def getMacAddress():
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


def get_weather_desc():
    owm = pyowm.OWM(API_key=config.pyowm_key, language='ru')
    observation = owm.weather_at_place('Moscow, ru')
    w = observation.get_weather()
    min_temp = w.get_temperature('celsius')['temp_min']
    wind = w.get_wind()['speed']
    hum = w.get_humidity()
    rain = w.get_rain()
    snow = w.get_snow()
    text = "временами {} с минимальной температурой {} °C ".format(
        w._detailed_status, int(min_temp))
    if int(hum) > 50 and min_temp < 15:
        text += ", высокая влажность,"+str(hum)+"%, одевайся потеплее"
    if int(wind) > 5:
        text += ", сильный ветер, " + \
            str(wind)+" м/с, смотри чтобы тебя не продуло"
    if rain:
        text += ", не забудь взять зонтик дорог'ой, возможен дождь в течении :"+rain
    if snow:
        text += ", возможно будет снег в течении :"+snow+", поиграем в снежки ? "
    text += " дорог'ой"
    return text

def get_news():
    res=[]
    headers = {'User-Agent':'Mozilla/5.0'}
    url='https://www.rbc.ru/'
    page = requests.get(url,headers=headers)
    soup = BeautifulSoup(page.content,"lxml")
    topicsTags=soup.find_all("span", {"class": "main__feed__title"})
    for topic in topicsTags:
        res.append(topic.text)
    return res