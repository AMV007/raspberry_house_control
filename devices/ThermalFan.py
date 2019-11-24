import RPi.GPIO as GPIO
import os
import sys

import config
import logging

import time as tm
from time import sleep
from datetime import datetime, time as datetime_time, timedelta

from utils.common import get_time
import my_logging
from my_logging import setup_logger

from RootDevice import RootDevice



class ThermalFan(RootDevice):
    def __init__(self):
        super().__init__(self.__class__.__name__)

    def probe(self):
        if not hasattr(config, "GPIO_RUN_FAN"):
            return False

        check_temp = config.DEF_CHECK_TEMP
        GPIO.setup(config.GPIO_RUN_FAN, GPIO.OUT)
        self.disable()
        return True

    def enable(self):
        with self.lock:
            super().enable()
            GPIO.output(config.GPIO_RUN_FAN, GPIO.HIGH)  # stop fan

    def disable(self):
        with self.lock:
            super().disable()
            GPIO.output(config.GPIO_RUN_FAN, GPIO.LOW)  # stop fan

    def get_status_str(self):
        ret = "Fans: "
        if self.enabled:
            ret += "running"
        else:
            ret += "stopped"
        return ret



