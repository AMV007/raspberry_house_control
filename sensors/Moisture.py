import RPi.GPIO as GPIO

import config

from RootSensor import RootSensor

class Moisture(RootSensor):

    def probe(self):
        with self.lock:
            if not hasattr(config, "GPIO_MOISTURE"):
                return False

            GPIO.setup(config.GPIO_MOISTURE, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        return True

    def read_val(self):
        with self.lock:
            value = GPIO.input(config.GPIO_MOISTURE)
        self.data_bus.moisture=value
        return value

    def get_status_str(self):
        ret = "Moisture status: "
        if self.read_val():
            ret += "dry"
        else:
            ret += "wet"
        return ret
