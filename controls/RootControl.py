from threading import Lock
from abc import ABC, abstractmethod

class RootControl(ABC):

    name="unknown"
    enabled=False
    lock = None
    auto_mode = True

    control_devices=[]
    control_sensors=[]
    send_telegram_warning=None

    __send_telegram_warning_handle=None

    def __init__(self):
        self.name="control "+self.__class__.__name__
        self.lock = Lock()

    def probe(self):
        self.disable()
        if len(self.control_devices)==0 and len(self.control_sensors)==0:
            return False
        return True

    @abstractmethod
    def do_check(self, noisy_time=False):
        pass

    # to not lock switch and enable-disable at lock
    def internal_devices_enable_disable(self, enable):
        self.enabled = enable

        for device in self.control_devices:
            if(enable):
                device.enable()
            else:
                device.disable()

    def enable(self, external_command=False):
        with self.lock:
            #was pushed by external, not internal
            if external_command:
                self.auto_mode = False

            self.internal_devices_enable_disable(True)

    def disable(self, external_command=False):
        with self.lock:
            #was pushed by external, not internal
            if external_command:
                self.auto_mode = False

            self.internal_devices_enable_disable(False)


    def switch(self, external_command=False):
        with self.lock:
            #was pushed by external, not internal
            if external_command:
                self.auto_mode = False

            self.internal_devices_enable_disable(not self.enabled)

    def set_auto(self):
        self.auto_mode = True
        self.do_check()

    def get_enable_status(self):
        return self.enabled

    def get_status_str(self):
        res=self.name
        if self.enabled:
            res+=": enabled"
        else:
            res+=": disabled"
        return res

    def send_telegram_warning(self, text):
        if self.__send_telegram_warning_handle:
            self.__send_telegram_warning_handle(text)

    def set_telegram_warning_handle(self, send_telegram_warning_handle):
        self.__send_telegram_warning_handle=send_telegram_warning_handle

