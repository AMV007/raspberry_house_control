import RPi.GPIO as GPIO
import os
import sys

import config
import logging

from RootDevice import RootDevice

class Outlet(RootDevice):
    def __init__(self):
        super().__init__(self.__class__.__name__)

    def probe(self):
        if not hasattr(config, "GPIO_OUTLET_ENABLE"):
            return False

        GPIO.setup(config.GPIO_OUTLET_ENABLE, GPIO.OUT)
        self.disable()
        return True

    def enable(self):
        with self.lock:
            super().enable()
            GPIO.output(config.GPIO_OUTLET_ENABLE, GPIO.LOW)


    def disable(self):
        with self.lock:
            super().disable()
            GPIO.output(config.GPIO_OUTLET_ENABLE, GPIO.HIGH)


