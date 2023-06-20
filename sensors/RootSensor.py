from threading import Lock
from abc import ABC, abstractmethod

import bus

class RootSensor(ABC):

    name="unknown"
    enabled=False
    lock = None
    data_bus=None

    def __init__(self):
        self.name="sensor "+self.__class__.__name__
        self.lock = Lock()
        self.data_bus=bus.DataBus.DataBus()

    @abstractmethod
    def probe(self):
        self.disable()
        return False

    @abstractmethod
    def read_val(self):
        return 0

    def enable(self):
        self.enabled = True

    def disable(self):
        self.enabled = False

    def get_enable_status(self):
        return self.enabled

    def get_status_str(self):
        return self.name+": "+str(self.read_val())

