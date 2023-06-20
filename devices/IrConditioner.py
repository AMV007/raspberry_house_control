import os, sys

import RPi.GPIO as GPIO
from time import sleep
import numpy as np
import pigpio

import config
import utils
from RootDevice import RootDevice

import app_logger

def find_nearest(array, value):
    n = [abs(i-value) for i in array]
    idx = n.index(min(n))
    return array[idx]

def decode_data(commands):
    #Compute the average low pulse width
    #Ignore the first two readings it's start bit
    commands=commands[2:]
    analyzed_len=len(commands)-len(commands)%16

    if len(commands)%16 !=1: #1 - stop bit at the end
        app_logger.error(f"warning, got unknown bits: {len(commands)%16}")

    threshold = 0
    for counter in range(0,analyzed_len,2):
        val, pulseLength = commands[counter]
        threshold += pulseLength
    threshold /= (((analyzed_len-1)/2)-1)

    bands=[110, 300, 600, 1200, 2400, 4800, 9600, 14400, 19200, 38400, 57600, 115200, 128000 ]
    possible_band=int(1e6/threshold)
    bandwidth=find_nearest(bands, possible_band)
    app_logger.error(f"threshold={threshold}, possible_band:{possible_band} bps")

    #ignoring first 3 commands - empirically


    data_len=int(analyzed_len/16)
    data = bytearray(data_len)

    #due to gaps, need to increase it's threshold value
    threshold*=1.5


    for counter in range(1,analyzed_len,2):
        val, pulseLength = commands[counter]
        index = int((counter)/16)
        data[index] >>=1
        if pulseLength>=threshold:
            #One bit for long pulse.
            data[index] |=(0x1<<7)
        #Else zero bit for short pulse.

    return bandwidth, data

def get_conditioner_data_array(enabled, hvac_mode, temperature, fan, vanne):
    data=[0x23, 0xcb, 0x26, 0x01, 0x00] # header
    if enabled:
        data.append(0x24)
    else:
        data.append(0x20)

    if hvac_mode == "heat":
        data.append(0x1)
    elif hvac_mode == "dry":
        data.append(0x2)
    elif hvac_mode == "cool":
        data.append(0x3)
    elif hvac_mode == "feel":
        data.append(0x8)
    else:
        raise "unknown mode"

    if temperature>31 or temperature<16:
        raise "not possible temperature"

    temperature=31-temperature
    data.append(temperature)

    fan_vanne=0
    if fan == 'auto':
        fan_vanne|=0x0
    elif fan == '1':
        fan_vanne|=0x2
    elif fan == '2':
        fan_vanne|=0x3
    elif fan == '3':
        fan_vanne|=0x5
    else:
        raise "unknown fan value"

    if vanne== 'auto':
        fan_vanne|=0x0
    elif vanne == '1':
        fan_vanne|=0x8
    elif vanne == '2':
        fan_vanne|=0x10
    elif vanne == '3':
        fan_vanne|=0x18
    elif vanne == '4':
        fan_vanne|=0x20
    elif vanne == '5':
        fan_vanne|=0x28
    elif vanne == 'cruise':
        fan_vanne|=0x38
    else:
        raise "unknown vanne value"

    data.append (fan_vanne)
    # clock ?
    data.append(0)
    data.append(0)
    data.append(0)
    data.append(0)

    arr_sum = sum(data)
    data.append(arr_sum&0xff)

    return data

def check_conditioner_data_crc(data):
    app_logger.info (f"check data[{len(data)}]: "+''.join('0x{:02x}, '.format(x) for x in data))
    recv_data=data[:-1]
    sum_arr=sum(data[:-1])&0xff
    if sum_arr != data[-1]:
        app_logger.error(f"CRC ERROR !!! must be 0x{sum_arr:x} but we have 0x{data[-1]:x}")
    else:
        app_logger.info("CRC OK")

###############################################

class IrConditioner(RootDevice):

    irControl=None
    bandwidth=2400

    def probe(self):
        if not hasattr(config, "GPIO_IR_WRITE"):
            return False

        self.irControl=utils.IRControl.IRControl()
        app_logger.info("ircontrol: "+str(self.irControl))
        self.disable()
        return True

    def enable(self):
        with self.lock:
            if not self.enabled :
                data=get_conditioner_data_array(enabled=True, hvac_mode='cool', temperature=26, fan='1', vanne='1')
                self.irControl.write_output(self.bandwidth, data)
            super().enable()


    def disable(self):
        with self.lock:
            if self.enabled :
                data=get_conditioner_data_array(enabled=False, hvac_mode='cool', temperature=26, fan='1', vanne='1')
                self.irControl.write_output(self.bandwidth, data)
            super().disable()