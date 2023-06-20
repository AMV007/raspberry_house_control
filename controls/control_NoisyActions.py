import os
import sys
from datetime import datetime, time as datetime_time, timedelta

import config

import sensors

from RootControl import RootControl

class NoisyActions(RootControl):

    force_silent = False

    # this control wiil allways exist
    def probe(self):
        self.disable()
        return True

    def __init__(self):
        super().__init__()
        self.control_sensors=sensors.get(sensors.Light)
        if len(self.control_sensors)>1:
            raise ValueError("now we are supporting only 1 Light sensor")

    def do_check(self,noisy_time=False):
        with self.lock:
            now = datetime.now()

            #check time first
            if (now.hour < config.START_CHECK_TIME or now.hour > config.STOP_CHECK_TIME):
                return False

            if len(self.control_sensors)>0 :
                #if sensor exist
                data=self.control_sensors[0].read_val()
                if not data:
                    return False

            return True

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
