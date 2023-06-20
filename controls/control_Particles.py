import os
import sys
import time

from datetime import datetime, timedelta

import config
import sound

import TTS

import sensors
import database

from RootControl import RootControl

class Particles(RootControl):

    #for not spam alerts
    alert_time = datetime.now() - timedelta(days=1)

    #for not ask sensor too frequently
    next_check_time = time.time()

    #for dump sensors
    next_time = time.time()

    def __init__(self):
        super().__init__()
        self.control_sensors=sensors.get(sensors.Particles_pms7003)
        if len(self.control_sensors)>1:
            raise ValueError("now we are supporting only 1 particles sensor")
        self.control_devices=[]

    def do_check(self,noisy_time=False):
        with self.lock:
            # because it's noisy sensor - we are polling it time to time
            now = time.time()
            if now < self.next_check_time:
                return

            data = self.control_sensors[0].read_val()
            if data == None:
                return #TODO: handle data none ?

            #remember time and dump seonsors only on success
            self.dump_sensors(data)
            self.next_check_time = now + config.SENSOR_PARTICLES_POLL_PERIOD_S

            if not noisy_time:
                return

            pm1 = data['data']['8']
            pm25 = data['data']['10']
            pm10 = data['data']['12']

            #check for alert
            if pm1[1] > 100 or pm25[1] > 100 or pm10[1] > 100:
                min_diff = (datetime.now() - self.alert_time).total_seconds() / 60.0
                if min_diff > 5:  # so it will not alert too frequently
                    self.alert_time = datetime.now()
                    data = '{}: {} {}'.format(pm1[0], pm1[1], pm1[2])
                    data += ', {}: {} {}'.format(pm25[0], pm25[1], pm25[2])
                    data += ', {}: {} {}'.format(pm10[0], pm10[1], pm10[2])
                    self.send_telegram_warning(
                        config.warning_message_particles+'\n Particles: '+data)
                    TTS.say("Внимание, высокий уровень частиц в воздухе : "+str(pm25[1])+" микрограмм на кубометр, надо одеть маску !")

    def dump_sensors(self, data):
        now = time.time()
        if now >= self.next_time:
            self.next_time = now + config.SENSOR_PARTICLES_POLL_PERIOD_S
            database.add_particles(data)

    def get_status_str(self):
        return ""