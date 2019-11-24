import RPi.GPIO as GPIO
import os
import sys

import config
import logging

from RootSensor import RootSensor

class Moisture(RootSensor):
    test_field="asdasd"
    def __init__(self):
        super().__init__(self.__class__.__name__)

    def probe(self):
        with self.lock:
            if not hasattr(config, "GPIO_MOISTURE"):
                return False

            GPIO.setup(config.GPIO_MOISTURE, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        return True

    def read_val(self):
        with self.lock:
            ret = GPIO.input(config.GPIO_MOISTURE)
        return ret

    def get_status_str(self):
        ret = "Moisture status: "
        if self.read_val():
            ret += "dry"
        else:
            ret += "wet"
        return ret
