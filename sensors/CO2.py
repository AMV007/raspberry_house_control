from time import sleep
from datetime import datetime, time as datetime_time, timedelta

#my import
import config
import bus
from utils.common import get_time
import app_logger

from RootSensor import RootSensor

cmd_on_off_auto_calib = 0x79 # if param 0xa0 - it will enable, otherwise will disable
cmd_get_co2 =           0x86
cmd_calibrate_zero =    0x87
cmd_calibrate_span =    0x88
cmd_sensor_detection_range =    0x99 # param not implemented - read datasheet

# Function to calculate MH-Z19 crc according to datasheet
def crc8(a):
    crc = 0x00
    count = 1
    b = bytearray(a)
    if len(b) < 8:
        app_logger.error("crc array must be at least 8 bytes, but we have only: "+str(len(b))+", values: "+str(b))
        return -1
    while count < 8:
        crc += b[count]
        count = count+1
    # Truncate to 8 bit
    crc %= 256
    # Invert number with xor
    crc = ~crc & 0xFF
    crc += 1
    return crc

class CO2(RootSensor):
    uart_bus=None
    data_bus=None
    max_read_try=5

    measure_count=0

    def __init__(self):
        super().__init__()
        self.uart_bus=bus.UartBus.UartBus()

    def probe(self):
        if not self.uart_bus or not self.uart_bus.probe(): #UART bus not exist
            return False

        if self.read_val()!=-1:
            return True

        app_logger.warn("CO2 sensor not responded")
        return False

    def send_cmd(self, cmd, param=None):
        cmd_template = bytearray()
        cmd_template.append(0xff)
        cmd_template.append(0x01)
        cmd_template.append(cmd)
        if param:
            cmd_template.append(param>>8)
            cmd_template.append(param)
        else:
            cmd_template.append(0x00)
            cmd_template.append(0x00)

        cmd_template.append(0x00)
        cmd_template.append(0x00)
        cmd_template.append(0x00)

        cmd_template.append(crc8(cmd_template))
        self.uart_bus.write(cmd_template)

    def zero_calibrate(self):
        with self.lock:
            try:
                self.uart_bus.acqure_lock_switch_to_measure_co2()

                self.send_cmd(cmd_calibrate_zero)

            except Exception:
                app_logger.exception("CO2 calibrate exception:")
                #esceptions here appearing constantly so just forget about it ?
                pass
            finally:
                self.uart_bus.release_lock_switch()

    def read_co2(self):
        with self.lock:
            co2value = -1
            temperature = 25
            try:
                self.uart_bus.acqure_lock_switch_to_measure_co2()
                for i in range(0, 5): # trying couple times, because got crc error ?
                    #self.uart_bus.release_lock_switch()
                    #self.uart_bus.acqure_lock_switch_to_measure_co2()
                    sleep(0.1) #for stabilize processes
                    # Send "read value" command to MH-Z19 sensor
                    self.send_cmd(cmd_get_co2)
                    s = self.uart_bus.read(9)
                    if(len(s) != 9):
                        app_logger.error(str(datetime.now())+", error, uart data len in response: "+str(len(s)))
                        continue

                    crc = crc8(s)
                    # Calculate crc
                    if crc != s[8]:
                        if i == (self.max_read_try-1): #for not spam
                            app_logger.error('CO2 CRC error calculated, try %d, crc calc=0x%x bytes= %x:%x:%x:%x:%x:%x:%x:%x crc= 0x%x, date=%s\n' % (
                                i, crc, s[0], s[1], s[2], s[3], s[4], s[5], s[6], s[7], s[8], str(datetime.now()) ))
                        continue

                    if s[0] != 0xFF or s[1] != cmd_get_co2:
                        if i == (self.max_read_try-1): #for not spam
                            app_logger.error('CO2 wrong answer to command %d bytes= %d:%d:%d:%d:%d:%d:%d:%d crc= %d\n' % (
                                cmd_get_co2, s[0], s[1], s[2], s[3], s[4], s[5], s[6], s[7], s[8]))
                        continue

                    co2value = s[2] * 256 + s[3]
                    temperature = s[4]-40
                    break
            except Exception:
                app_logger.exception("CO2 read exception:")
                #esceptions here appearing constantly so just forget about it ?
            finally:
                self.uart_bus.release_lock_switch()

            #app_logger.info("CO2 : "+str(co2value))
            return co2value, temperature

    def read_val(self):
        co2value, temperature=self.read_co2()
        self.data_bus.CO2=co2value
        if not hasattr(config, "GPIO_GET_TEMP_HUMID"):
            #in case not exist good temperature sensor - try to measure what we have with rough
            self.data_bus.temperature=temperature
        return self.data_bus.CO2


    def get_status_str(self):
        if not self.data_bus.CO2:
            self.read_val()
        return "CO2: "+str(self.data_bus.CO2)
