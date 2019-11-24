import RPi.GPIO as GPIO
import os
import sys

import config
import logging

from RootSensor import RootSensor

class WaterLevelDrop(RootSensor):
    # this may be used only during watering
    last_val = None

    def __init__(self):
        super().__init__(self.__class__.__name__)

    def probe(self):
        with self.lock:
            if not hasattr(config, "GPIO_WATER_DROP_SENSOR"):
                return False

            GPIO.setup(config.GPIO_WATER_DROP_SENSOR, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        return True

    def read_val(self):
        with self.lock:
            self.last_val = GPIO.input(config.GPIO_WATER_DROP_SENSOR)
        return self.last_val


    def get_status_str(self):
        ret = "Last water level: "
        if self.last_val == None:
            ret += "not measured yet"
        elif self.last_val:
            ret += "critical low"
        else:
            ret += "ok"
        return ret
