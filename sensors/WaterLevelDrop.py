import RPi.GPIO as GPIO
import os
import sys

import config

from RootSensor import RootSensor
import app_logger

# this may be used only during watering
class WaterLevelDrop(RootSensor):

    def probe(self):
        with self.lock:
            if not hasattr(config, "GPIO_WATER_DROP_SENSOR"):
                return False

            GPIO.setup(config.GPIO_WATER_DROP_SENSOR, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        return True

    def read_val(self):
        with self.lock:
            self.data_bus.waterLevel=GPIO.input(config.GPIO_WATER_DROP_SENSOR)
        return self.data_bus.waterLevel


    def get_status_str(self):
        ret = "Last water level: "
        if self.data_bus.waterLevel == None:
            ret += "not measured yet"
        elif self.data_bus.waterLevel:
            ret += "critical low"
        else:
            ret += "ok"
        return ret
