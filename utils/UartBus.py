import RPi.GPIO as GPIO
import os
import sys
import serial
import threading

import config

from utils.Singleton import Singleton

# this is switch between CO2 and Particles sensors on the same UART
# this is not sensor!!!

class UartBus(metaclass=Singleton):

    SerialDevice = '/dev/serial0'
    ser = None
    lock = None
    uart_lock_for_device=None
    value=1

    def __init__(self):
        self.lock = threading.Lock()
        self.uart_lock_for_device=threading.Lock()

        GPIO.setup(config.GPIO_SWITCH_CO2_PARTICLES, GPIO.OUT)
        GPIO.output(config.GPIO_SWITCH_CO2_PARTICLES, GPIO.LOW)

    def acqure_lock_switch_to_measure_co2(self):
        self.uart_lock_for_device.acquire()
        with self.lock:
            self.ser = serial.Serial(   port=self.SerialDevice, baudrate=9600,
                                        timeout=2.0, dsrdtr=False, rtscts=False)
            GPIO.output(config.GPIO_SWITCH_CO2_PARTICLES, GPIO.LOW)

    def acqure_lock_switch_to_measure_particles(self):
        self.uart_lock_for_device.acquire()
        with self.lock:
            self.ser = serial.Serial(   port=self.SerialDevice, baudrate=9600, 
                                        bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE,
                                        stopbits=serial.STOPBITS_ONE)
            GPIO.output(config.GPIO_SWITCH_CO2_PARTICLES, GPIO.HIGH)

    def release_lock_switch(self):
        with self.lock:
            if self.ser:
                self.ser.close()
            self.uart_lock_for_device.release()

    def write(self, data):
        with self.lock:
            self.ser.write(data)

    def read(self, size=1):
        with self.lock:
            return self.ser.read(size)

    def read_val(self):
        with self.lock:
            return self.read()