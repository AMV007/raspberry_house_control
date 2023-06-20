import RPi.GPIO as GPIO
import os
import sys

import config

from RootSensor import RootSensor

class Light(RootSensor):
    variable=1

    def probe(self):
        with self.lock:
            if not hasattr(config, "GPIO_LIGHT_DETECT"):
                return False

            GPIO.setup(config.GPIO_LIGHT_DETECT, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
            self.disable()
        return True

    def read_val(self):
        with self.lock:
            value = not GPIO.input(config.GPIO_LIGHT_DETECT)
        self.data_bus.light=value
        return value

    def get_status_str(self):
        ret = "Light status: "
        if self.read_val():
            ret += "light"
        else:
            ret += "dark"
        return ret
