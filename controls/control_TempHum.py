import RPi.GPIO as GPIO
import os
import sys

import time
from datetime import datetime, time as datetime_time, timedelta

#local imports
import config
from utils.common import get_time
import sensors
import devices
import database
import TTS
import sound

from RootControl import RootControl

class TempHum(RootControl):

    auto_mode = True

    #temperature - will try to control it
    check_temp = config.DEF_CHECK_TEMP

    #for dump sensors
    next_time_dump = time.time()

    #for not frequently switch fan
    next_time_switch = time.time()

    #to calculate average data
    temperature_values=[]

    def __init__(self):
        super().__init__(self.__class__.__name__)
        self.control_devices=devices.get(devices.ThermalFan)
        self.control_sensors=sensors.get(sensors.TempHum)

        self.auto_mode = True
        self.check_temp = config.DEF_CHECK_TEMP

        if len(self.control_sensors)>1:
            raise ValueError("now we are supporting only 1 temperature sensor")

        # if no devices - no reason to work
        if len(self.control_devices)==0 or len(self.control_sensors)==0:
            self.control_sensors=[]
            self.control_devices=[]

    def internal_switch_with_state_letency(self, new_state):
        if self.enabled != new_state:
            if time.time()>self.next_time_switch: #so fans will not be so frequent power on and off
                self.internal_devices_enable_disable(new_state)
                self.next_time_switch=time.time()+config.FAN_ON_OFF_DELAY_PERIOD_S

    def Average_temperature(self, new_temperature):

        self.temperature_values.append(new_temperature)

        #to control length of temperature values array
        if len(self.temperature_values) > 10:
            self.temperature_values.pop(0)

        return sum(self.temperature_values) / len(self.temperature_values)

    def do_check(self,noisy_time=False):
        with self.lock:

            temperature, humidity, num_cycles_wrong = self.control_sensors[0].read_val()
            self.dump_sensors(temperature, humidity, num_cycles_wrong)

            if not self.auto_mode:
                return

            if not noisy_time:
                self.internal_devices_enable_disable(False)
                return

            #to reduce temperature jumings
            temperature_average=self.Average_temperature(temperature)

            if temperature_average < config.TEMP_LOW_WARNING or temperature_average > config.TEMP_HIGH_WARNING :
                warning_message=config.warning_message_temperature+'\n Temp: {0:0.1f} C  Humidity: {1:0.1f} %'.format(temperature_average, humidity)
                self.send_telegram_warning(warning_message)
                TTS.say(warning_message)

            if temperature_average < self.check_temp:
                self.internal_switch_with_state_letency(True)
            else:
                self.internal_switch_with_state_letency(False)

    def dump_sensors(self, temperature, humidity, num_cycles_wrong):
        now = time.time()
        if now >= self.next_time_dump:
            self.next_time_dump = now + config.SENSOR_POLL_PERIOD_S
            database.add_temp_humid(temperature, humidity, num_cycles_wrong)

    def get_status_str(self):
        ret = "Fans control: "
        if self.auto_mode:
            ret += "auto"
        else:
            ret += "manual"
        ret += "\n"
        for device in self.control_devices:
            ret+=device.get_status_str()
        return ret