from threading import Lock
from abc import ABC, abstractmethod

class RootDevice(ABC):

    name="unknown"
    enabled=False
    lock = None

    def __init__(self, name):
        self.name="device "+name
        self.lock = Lock()

    @abstractmethod
    def probe(self):
        self.disable()
        return False

    def enable(self):
        self.enabled = True

    def disable(self):
        self.enabled = False

    def get_enable_status(self):
        return self.enabled

    def get_status_str(self):
        res=f"{self.name}: "
        if self.enabled:
            res+="enabled"
        else:
            res+="disabled"
        return res

