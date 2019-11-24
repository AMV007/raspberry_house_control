from threading import Lock
from abc import ABC, abstractmethod

class RootSensor(ABC):

    name="unknown"
    enabled=False
    lock = None

    def __init__(self, name):
        self.name="sensor "+name
        self.lock = Lock()

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

