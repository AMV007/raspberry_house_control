import os
import sys
from datetime import datetime, time as datetime_time, timedelta

import devices
import bus

from RootControl import RootControl

class NextionDisplay(RootControl):

    data_bus=None

    def __init__(self):
        super().__init__()
        self.data_bus=bus.DataBus.DataBus()
        self.control_devices=devices.get(devices.NextionDisplay)

    def do_check(self,noisy_time=False):
        with self.lock:
            if noisy_time:
                backlight=95
            else:
                backlight=1
            for device in self.control_devices:
                device.display(self.data_bus.temperature, self.data_bus.humidity,
                self.data_bus.CO2, self.data_bus.particles, backlight)

    def get_status_str(self):
        ret = "Outlet control: "
        if self.auto_mode:
            ret += "auto"
        else:
            ret += "manual"
        ret += "\n"
        for device in self.control_devices:
            ret+=device.get_status_str()
        return ret