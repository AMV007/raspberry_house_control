import os
import sys

import config
import devices

from RootControl import RootControl

class Outlet(RootControl):

    def __init__(self):
        super().__init__()
        self.control_devices=devices.get(devices.Outlet)

    def do_check(self,noisy_time=False):
        with self.lock:
            if not self.auto_mode:
                return
            self.internal_devices_enable_disable(noisy_time)

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
