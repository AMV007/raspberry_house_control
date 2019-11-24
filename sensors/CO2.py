import RPi.GPIO as GPIO
import os
import sys

import binascii

import logging

from time import sleep
from datetime import datetime, time as datetime_time, timedelta

#my import
import config
import sensors
import database
import utils
from utils.common import get_time
import my_logging
from my_logging import setup_logger

from RootSensor import RootSensor

def crc8(a):
        crc = 0x00
        count = 1
        b = bytearray(a)
        while count < 8:
            crc += b[count]
            count = count+1
        # Truncate to 8 bit
        crc %= 256
        # Invert number with xor
        crc = ~crc & 0xFF
        crc += 1
        return crc

class CO2(RootSensor):
    uart_bus=None
    def __init__(self):
        super().__init__(self.__class__.__name__)
        self.uart_bus=utils.UartBus.UartBus()
        

    def probe(self):
        with self.lock:
            # init device
            try:
                # try to read a line of data from the serial port and parse
                self.uart_bus.acqure_lock_switch_to_measure_co2()
                # 'warm up' with reading one input
                send_data = b"\xff\x01\x86\x00\x00\x00\x00\x00\x79"
                result = self.uart_bus.write(send_data)
                sleep(0.1)
                s = self.uart_bus.read(9)
                if not s:
                    return False

                crc = crc8(s)
                if crc != s[8]:
                    raise ValueError('CRC error calculated0 %d bytes= %d:%d:%d:%d:%d:%d:%d:%d crc= %d\n' % (
                        crc, s[0], s[1], s[2], s[3], s[4], s[5], s[6], s[7], s[8]))
            except Exception as e:
                my_logging.logger.exception("main exception:")
                return False
            finally:
                self.uart_bus.release_lock_switch()
            return True

# Function to calculate MH-Z19 crc according to datasheet
    def read_val(self):
        with self.lock:
            co2value = 0
            try:
                self.uart_bus.acqure_lock_switch_to_measure_co2()

                # Send "read value" command to MH-Z19 sensor
                send_data = b"\xff\x01\x86\x00\x00\x00\x00\x00\x79"
                result = self.uart_bus.write(send_data)
                sleep(0.1)
                s = self.uart_bus.read(9)
                if(len(s) != 9):
                    raise ValueError("error,. uart data len in recponse: "+str(len(s)))
                crc = crc8(s)
                # Calculate crc
                if crc != s[8]:
                    raise ValueError('CRC error calculated1 %d bytes= %d:%d:%d:%d:%d:%d:%d:%d crc= %d\n' % (
                        crc, s[0], s[1], s[2], s[3], s[4], s[5], s[6], s[7], s[8]))
                else:
                    if s[0] == "xff" and s[1] == "x86": #TODO : what is it ? may be add check for right value ?
                        print("co2=", s[2]*256 + s[3])
                co2value = s[2] * 256 + s[3]
            except Exception as e:
                #my_logging.logger.exception("CO2 read exception:")
                #esceptions here appearing constantly so just forget about it ?
                pass
            finally:
                self.uart_bus.release_lock_switch()
            #my_logging.logger.info("CO2 : "+str(co2value))
            return co2value


    def get_status_str(self):
        return "CO2: "+str(self.read_val())
