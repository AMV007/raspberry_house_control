import os
import sys
import time

from datetime import datetime, timedelta

#local imports
import config
import sensors
import sound
import TTS
import database

from RootControl import RootControl

class CO2(RootControl):

    #for not spam alerts
    alert_time = datetime.now() - timedelta(days=1)

    #for dump sensors
    next_time = time.time()

    def __init__(self):
        super().__init__(self.__class__.__name__)
        self.control_sensors=sensors.get(sensors.CO2)
        if len(self.control_sensors)>1:
            raise ValueError("now we are supporting only 1 CO2 sensor")

    def do_check(self,noisy_time=False):
        with self.lock:
            co2 = self.control_sensors[0].read_val()
            self.dump_sensors(co2)
            if not noisy_time:
                return

            if co2 > 1000:
                min_diff = (datetime.now() - self.alert_time).total_seconds() / 60.0
                if min_diff > 5:  # so it will not alert too frequently
                    self.alert_time = datetime.now()
                    self.send_telegram_warning(
                        config.warning_message_co2+'\n CO2 '+str(co2)+" ppm")
                    if not TTS.say("Внимание, высокий уровень углекислого газа : "+str(co2)+" ppm, нужно открыть окно !"):
                        sound.play_command("co2_level")

    def dump_sensors(self, data):
        now = time.time()
        if now >= self.next_time:
            self.next_time = now + config.SENSOR_POLL_PERIOD_S
            database.add_co2(data)

    def get_status_str(self):
        return ""