import os, sys, threading
import RPi.GPIO as GPIO
import math
from datetime import datetime
from time import sleep
import numpy as np
import pigpio


import config
from Singleton import Singleton
import app_logger

########## IR funcs
def write_one_IR(PIN_GPIO_OUT, pi, timeout_mks):
    ir_freq=38400 # frequency for modulation 1
    pi.hardware_PWM(PIN_GPIO_OUT, ir_freq, 500000)
    sleep(timeout_mks)
    pi.hardware_PWM(PIN_GPIO_OUT, 0, 0)

def write_zero_IR(PIN_GPIO_OUT, timeout_mks):
    sleep(timeout_mks)

def write_output_internal(PIN_GPIO_OUT, bandwidth, data):
    #print(f"bandwidth: {bandwidth}")
    #print (f"data [{len(data)}]: "+''.join('0x{:02x}, '.format(x) for x in data))

    status = os.system('systemctl is-active --quiet pigpiod')
    if status !=0:
        app_logger.info(f"service status={status}")
        os.system("sudo service pigpiod start")
        sleep(1)

    pi = pigpio.pi()
    data_bits=""
    wait_timeout_mks=(1/bandwidth)
    wait_timeout_mks-=(100e-6) # because python latencies
    app_logger.info(f"wait_timeout_mks={int(wait_timeout_mks*1e6)}")

    write_one_IR(PIN_GPIO_OUT, pi, wait_timeout_mks*8)
    write_zero_IR(PIN_GPIO_OUT, wait_timeout_mks*3)

    for counter in range(0,len(data)*8):
        index = int(counter/8)
        offset=(counter%8)
        bit = (data[index]>>offset) & 0x1

        write_one_IR(PIN_GPIO_OUT, pi, wait_timeout_mks)
        data_bits+=str(bit)
        if bit:
            write_zero_IR(PIN_GPIO_OUT, wait_timeout_mks*3)
        else:
            write_zero_IR(PIN_GPIO_OUT, wait_timeout_mks)

    # last stop bit
    write_one_IR(PIN_GPIO_OUT, pi, wait_timeout_mks)
    write_zero_IR(PIN_GPIO_OUT, wait_timeout_mks)
    #print(f"data_bits={data_bits}")
    pi.stop()

###############################################
class IRControl(metaclass=Singleton):

    PIN_GPIO_IN=0
    PIN_GPIO_OUT=0
    lock = None

    def __init__(self):
        if hasattr(config, "GPIO_IR_WRITE") and hasattr(config, "GPIO_IR_READ"):
            #if sensor gpio exist
            self.lock = threading.Lock()

            self.PIN_GPIO_IN=config.GPIO_IR_READ
            self.PIN_GPIO_OUT=config.GPIO_IR_WRITE

            GPIO.setup(self.PIN_GPIO_IN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            GPIO.setup(self.PIN_GPIO_OUT, GPIO.OUT, initial=GPIO.LOW)

    def read_input(self):
        with self.lock:
            while True:
                value = 1
                # Loop until we read a 0, actually values inverted - 1 mean 0 and 0 - mean 1
                while value:
                    value = GPIO.input(self.PIN_GPIO_IN)

                # Grab the start time of the commands
                startTime = datetime.now()

                # Used to buffer the commands pulses
                commands = []

                # The end of the "commands" happens when we read more than
                # a certain number of 1s (1 is off for my IR receiver)
                numOnes = 0

                # Used to keep track of transitions from 1 to 0
                previousVal = 0

                while True:

                    if value != previousVal:
                        # The value has changed, so calculate the length of this run
                        now = datetime.now()
                        pulseLength = now - startTime
                        startTime = now

                        #commands.append((previousVal, pulseLength.microseconds))
                        #becasue inverted
                        commands.append((value, pulseLength.microseconds))

                    if value:
                        numOnes = numOnes + 1
                    else:
                        numOnes = 0

                    # 10000 is arbitrary, adjust as necessary
                    if numOnes > 100000:
                        break

                    previousVal = value
                    value = GPIO.input(self.PIN_GPIO_IN)

                #print_array(commands)

                if len(commands)>=(3+16):
                    return commands
                    #return decode_data(commands)

    #PIN_GPIO_OUT must be supporting PWM 18 for example
    def write_output(self, bandwidth, data):
        with self.lock:
           write_output_internal(self.PIN_GPIO_OUT, bandwidth, data)