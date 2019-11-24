import RPi.GPIO as GPIO
import os
import sys

import config
import logging

from RootSensor import RootSensor

class Light(RootSensor):
    variable=1
    def __init__(self):
        super().__init__(self.__class__.__name__)

    def probe(self):
        with self.lock:
            if not hasattr(config, "GPIO_LIGHT_DETECT"):
                return False

            GPIO.setup(config.GPIO_LIGHT_DETECT, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
            self.disable()
        return True

    def read_val(self):
        with self.lock:
            ret = not GPIO.input(config.GPIO_LIGHT_DETECT)
        return ret

    def get_status_str(self):
        ret = "Light status: "
        if self.read_val():
            ret += "light"
        else:
            ret += "dark"
        return ret
