import RPi.GPIO as GPIO
import os
import sys
import serial
import threading
from time import sleep

import config

from Singleton import Singleton

# this class is for switch between multiple uart devices
'''
    0,0 - CO2
    0,1 - particles
    1,0 - nextion display
'''
class UartBus(metaclass=Singleton):

    __SerialDevice = '/dev/ttyAMA1'
    __ser = None
    __lock = None
    __uart_lock_for_device=None

    def probe(self)->bool:
        return hasattr(config, "GPIO_SWITCH_UART0") and hasattr(config, "GPIO_SWITCH_UART1")

    def __init__(self):
        if not self.probe(): return

        self.__lock = threading.Lock()
        self.__uart_lock_for_device=threading.Lock()

        GPIO.setup(config.GPIO_SWITCH_UART0, GPIO.OUT)
        GPIO.setup(config.GPIO_SWITCH_UART1, GPIO.OUT)

        GPIO.output(config.GPIO_SWITCH_UART0, GPIO.LOW)
        GPIO.output(config.GPIO_SWITCH_UART1, GPIO.LOW)

    def acqure_lock_switch_to_measure_co2(self):
        if not self.probe(): return

        self.__uart_lock_for_device.acquire()
        with self.__lock:
            GPIO.output(config.GPIO_SWITCH_UART0, GPIO.LOW)
            GPIO.output(config.GPIO_SWITCH_UART1, GPIO.LOW)

            self.__ser = serial.Serial(   port=self.__SerialDevice,
                                        baudrate=9600,
                                        timeout=1.0,
                                        dsrdtr=False,
                                        rtscts=False,
                                        bytesize=serial.EIGHTBITS,
                                        parity=serial.PARITY_NONE,
                                        stopbits=serial.STOPBITS_ONE
                                        )
            self.__ser.flushInput() # flush port for unwaited data

    def acqure_lock_switch_to_measure_particles(self):
        if not self.probe(): return

        self.__uart_lock_for_device.acquire()
        with self.__lock:
            GPIO.output(config.GPIO_SWITCH_UART0, GPIO.HIGH)
            GPIO.output(config.GPIO_SWITCH_UART1, GPIO.LOW)

            self.__ser = serial.Serial(   port=self.__SerialDevice,
                                        baudrate=9600,
                                        timeout=1.0,
                                        dsrdtr=False,
                                        rtscts=False,
                                        bytesize=serial.EIGHTBITS,
                                        parity=serial.PARITY_NONE,
                                        stopbits=serial.STOPBITS_ONE
                                        )
            self.__ser.flushInput() # flush port for unwaited data

    def acqure_lock_switch_to_nextion(self):
        if not self.probe(): return

        self.__uart_lock_for_device.acquire()
        with self.__lock:
            GPIO.output(config.GPIO_SWITCH_UART0, GPIO.LOW)
            GPIO.output(config.GPIO_SWITCH_UART1, GPIO.HIGH)

            self.__ser = serial.Serial(   port=self.__SerialDevice,
                                        baudrate=9600,
                                        timeout=1.0,
                                        dsrdtr=False,
                                        rtscts=False,
                                        bytesize=serial.EIGHTBITS,
                                        parity=serial.PARITY_NONE,
                                        stopbits=serial.STOPBITS_ONE
                                        )
            self.__ser.flushInput() # flush port for unwaited data

    def release_lock_switch(self):
        if not self.probe(): return

        with self.__lock:
            if self.__ser:
                self.__ser.close()
            if self.__uart_lock_for_device.locked():
                self.__uart_lock_for_device.release()

################ DATA TRANSFER

    def write(self, data):
        if not self.probe(): return

        if isinstance(data, str):
            data=str.encode(data,encoding='iso-8859-1')
        with self.__lock:
            self.__ser.write(data)

    def read(self, size=1):
        if not self.probe(): return None

        with self.__lock:
            return self.__ser.read(size)

    def readline(self):
        if not self.probe(): return None

        with self.__lock:
            return self.__ser.readline()

    def readany(self):
        if not self.probe(): return None

        with self.__lock:
            return self.__read()