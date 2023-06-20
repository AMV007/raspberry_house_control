import RPi.GPIO as GPIO
import os
import sys

import config

from RootDevice import RootDevice

class Outlet(RootDevice):

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

