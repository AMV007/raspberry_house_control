import os
import sys
from datetime import datetime, time as datetime_time, timedelta

import config
import logging

import sensors

from RootControl import RootControl

class NoisyActions(RootControl):

    force_silent = False

    def __init__(self):
        super().__init__(self.__class__.__name__)
        self.control_sensors=sensors.get(sensors.Light)
        if len(self.control_sensors)>1:
            raise ValueError("now we are supporting only 1 Light sensor")

    def do_check(self,noisy_time=False):
        with self.lock:
            now = datetime.now()
            if self.control_sensors[0].read_val() and (now.hour >= config.START_CHECK_TIME and now.hour <= config.STOP_CHECK_TIME):
                return True
            else:
                return False

    def check_speech_allowed(self):
        return self.do_check() and not self.force_silent


    def get_status_str(self):
        ret = "Noisy actions : "
        if self.do_check():
            ret += "enabled"
        else:
            ret += "disabled"
        ret += "\n"

        ret += "Speech allowed : "
        if self.check_speech_allowed():
            ret += "enabled"
        else:
            ret += "disabled"
        return ret
