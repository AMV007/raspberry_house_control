import RPi.GPIO as GPIO
import os
import sys

import config
import logging

from RootDevice import RootDevice


class WaterPump(RootDevice):
    def __init__(self):
        super().__init__(self.__class__.__name__)

    def probe(self):
        if not hasattr(config, "GPIO_RUN_PUMP"):
            return False

        GPIO.setup(config.GPIO_RUN_PUMP, GPIO.OUT)
        self.disable()
        return True

    def enable(self):
        with self.lock:
            super().enable()
            GPIO.output(config.GPIO_RUN_PUMP, GPIO.HIGH)  # stop water pump


    def disable(self):
        with self.lock:
            super().disable()
            GPIO.output(config.GPIO_RUN_PUMP, GPIO.LOW)  # stop water pump

    def get_status_str(self):
        ret = "Water pump: "
        if self.enabled:
            ret += "working now"
        else:
            ret += "stopped"
        return ret



