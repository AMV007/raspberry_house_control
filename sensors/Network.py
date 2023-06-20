import RPi.GPIO as GPIO
import os
import sys
import netifaces as ni

import config

from RootSensor import RootSensor

#this sensor using for detect IP address

class Network(RootSensor):
    variable=1

    def probe(self):
        with self.lock:
            self.disable()
        return True

    def read_val(self):
        with self.lock:
            ni.ifaddresses('eth0')
            value = ni.ifaddresses('eth0')[ni.AF_INET][0]['addr']
        self.data_bus.network=value
        return value

    def get_status_str(self):
        ret = "IP: "+self.read_val()
        return ret