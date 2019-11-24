import os
import sys

import config
import logging

import devices

from RootControl import RootControl

class ConditionerControl_IR(RootControl):
    def __init__(self):
        super().__init__(self.__class__.__name__)
        self.control_devices=devices.get(devices.IrConditioner)

    def do_check(self,noisy_time=False):
        with self.lock:
            if not self.auto_mode:
                return
            self.internal_devices_enable_disable(noisy_time)