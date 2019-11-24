import RPi.GPIO as GPIO
import os
import sys

import config
import logging

import time
from time import sleep
from datetime import datetime, time as datetime_time, timedelta

from utils.common import get_time
import my_logging
from my_logging import setup_logger
import traceback

import Adafruit_DHT
import database

from RootSensor import RootSensor

def usleep(x): return sleep(x/1000000.0)

def read_raw_val(pin):
    max_wait_count = 10000
    error = 0
    raw_val = []
    res = [int(0)]*5

    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.HIGH)
    usleep(500000)
    GPIO.output(pin, GPIO.LOW)
    usleep(20000)
    GPIO.output(pin, GPIO.HIGH)
    usleep(40)
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    # wait first law
    for count in range(0, max_wait_count):
        if GPIO.input(pin):
            break

    if count == (max_wait_count-1):
        error = -1
        return (res, error)

    # waiting data
    for pulse in range(0, 41):
        for count in range(0, max_wait_count):
            if not GPIO.input(pin):
                break
        raw_val.append(count)
        if count == (max_wait_count-1):
            error = -2
            return (res, error)

        for count in range(0, max_wait_count):
            if GPIO.input(pin):
                break
        raw_val.append(count)
        if count == (max_wait_count-1):
            error = -3
            return (res, error)

    count = 0
    for pulse in range(1, 81, 2):
        indx = int(count/8)
        count = count+1
        res[indx] <<= 1
        if raw_val[pulse+1] >= raw_val[pulse]:
            res[indx] |= 0x1

    # check parity
    if not res[4] == ((res[0]+res[1]+res[2]+res[3]) & 0xff):
        error = -4
        return (res, error)

    return (res, error)

class TempHum(RootSensor):
    def __init__(self):
        super().__init__(self.__class__.__name__)

    def probe(self):
        with self.lock:
            if not hasattr(config, "GPIO_GET_TEMP_HUMID"):
                return False

            GPIO.setup(config.GPIO_ENABLE_POWER_TEMP_HUM, GPIO.OUT)
            GPIO.output(config.GPIO_ENABLE_POWER_TEMP_HUM, GPIO.LOW)
            GPIO.setup(config.GPIO_GET_TEMP_HUMID, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        return True

    def read_dht22_data(pin):
        humidity = 0
        temperature = 0
        data, error = read_raw_val(pin)
        if not error == 0:
            return (humidity, temperature, error)

        temperature = float(((data[2] & 0x7F) << 8 | data[3])) / 10
        humidity = float((data[0] << 8 | data[1])) / 10
        if (data[2] & 0x80) != 0:
            temperature = -temperature
        return (humidity, temperature, error)


    def read_val(self):
        with self.lock:
            tot_humidity = 0
            tot_temperature = 0
            try:
                num_cycles_wrong = 0
                num_cycles_total = 1
                GPIO.output(config.GPIO_ENABLE_POWER_TEMP_HUM, GPIO.HIGH)
                # sleep(1) # wait sensor warm up - not waiting now, because at's constantly enabled
                for x in range(0, num_cycles_total):
                    humidity = 0
                    temperature = None
                    error = 0

                    num_cycles=0
                    timeout = time.time() + 5   # 5 seconds
                    while time.time() < timeout:
                        humidity, temperature = Adafruit_DHT.read_retry(
                            config.TEMP_DHT_VER, config.GPIO_GET_TEMP_HUMID)
                        #humidity, temperature,error=read_dht22_data(config.GPIO_GET_TEMP_HUMID)
                        if error == 0:
                            if temperature != None and humidity < 100 and humidity > 5:
                                # all good
                                break
                            else:
                                #print("temperature="+str(temperature)+", humidity="+str(humidity)+", error="+str(error)+", num_cycles_wrong: "+str(num_cycles))
                                pass
                        else:
                            #print("temperature="+str(temperature)+", humidity="+str(humidity)+", error="+str(error)+", num_cycles_wrong: "+str(num_cycles))
                            pass
                        num_cycles+=1

                    num_cycles_wrong += num_cycles
                    if temperature != None and error == 0:
                        tot_humidity += humidity
                        tot_temperature += temperature
                    else:
                        tot_humidity = num_cycles_total*50
                        tot_temperature += num_cycles_total*25
                        my_logging.logger.debug("can't measure temperature")

                GPIO.output(config.GPIO_ENABLE_POWER_TEMP_HUM, GPIO.LOW)
                tot_humidity /= num_cycles_total
                tot_temperature /= num_cycles_total
                #my_logging.logger.info( 'Temp: {0:0.1f} C  Humidity: {1:0.1f} %'.format(tot_temperature, tot_humidity)+", num cycles: "+str(num_cycles_wrong))
            except Exception as e:
                my_logging.logger.exception(
                    "get temp error, temp="+str(tot_temperature)+", hum="+str(tot_humidity))
            finally:
                return (tot_temperature, tot_humidity, num_cycles_wrong)


    def get_status_str(self):
        temperature, humidity, num_cycles_wrong = self.read_val()
        ret = 'Temp: {0:0.1f} °C \nHumidity: {1:0.1f} %\n'.format(
            temperature, humidity,)+"measure try: "+str(num_cycles_wrong)
        return ret
