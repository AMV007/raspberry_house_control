import threading
import traceback # for debug
import time

import app_logger
import bus

from RootSensor import RootSensor

HEAD_FIRST = b'B' #0x42
HEAD_SECOND = b'M' #0x4b
DATA_LENGTH = 32
BODY_LENGTH = DATA_LENGTH - 1 - 1
P_CF_PM10 = 2
P_CF_PM25 = 4
P_CF_PM100 = 6
P_C_PM10 = 8
P_C_PM25 = 10
P_C_PM100 = 12
P_C_03 = 14
P_C_05 = 16
P_C_10 = 18
P_C_25 = 20
P_C_50 = 22
P_C_100 = 24

DATA_DESC = [
    (P_CF_PM10, 'CF=1, PM1.0', 'μg/m3'),
    (P_CF_PM25, 'CF=1, PM2.5', 'μg/m3'),
    (P_CF_PM100, 'CF=1, PM10', 'μg/m3'),
    (P_C_PM10, 'PM1.0', 'μg/m3'),
    (P_C_PM25, 'PM2.5', 'μg/m3'),
    (P_C_PM100, 'PM10', 'μg/m3'),
    (P_C_03, '0.1L, d>0.3μm', ''),
    (P_C_05, '0.1L, d>0.5μm', ''),
    (P_C_10, '0.1L, d>1μm', ''),
    (P_C_25, '0.1L, d>2.5μm', ''),
    (P_C_50, '0.1L, d>5.0μm', ''),
    (P_C_100, '0.1L, d>10μm', ''),
]

def get_frame_length(_frame):
    h8 = _frame[0]
    l8 = _frame[1]
    return int(h8 << 8 | l8)


def get_version_and_error_code(_frame):
    return _frame[-4], _frame[-3]


def valid_frame_checksum(_frame):
    checksum = _frame[-2] << 8 | _frame[-1]
    calculated_checksum = ord(HEAD_FIRST) + ord(HEAD_SECOND)
    for field in _frame[:-2]:
        calculated_checksum += field
    return checksum == calculated_checksum


def decode_frame(_frame):
    data = {}
    for item in DATA_DESC:
        start, desc, unit = item
        value = int(_frame[start] << 8 | _frame[start + 1])
        data[str(start)] = (desc, value, unit)
    return data

def get_frame(_serial):
    timeout = time.time() + 5   # 5 seconds

    while time.time() < timeout:
        b = _serial.read()
        if b != HEAD_FIRST:
            continue
        b = _serial.read()
        if b != HEAD_SECOND:
            continue
        body = _serial.read(BODY_LENGTH)
        if len(body) != BODY_LENGTH:
            continue

        # print(bytearray(body))
        return bytearray(body)
    raise ValueError("Particles_pms7003 sensor data not received")

def set_sleep_mode(_serial, mode):
    send_data = bytearray([0x42,0x4d,0xe4,0x00,0x00,0x00,0x00])
    if not mode:
        send_data[4]=1
    sum=send_data[0]+send_data[1]+send_data[2]+send_data[3]+send_data[4]
    send_data[5]=(sum>>8)&0xFF
    send_data[6]=(sum>>0)&0xFF

    _serial.write(send_data)



#######################################################################3
from bus.UartBus import UartBus
class Particles_pms7003(RootSensor):
    sleep_timer = None
    sleep_count = 0
    uart_bus=None

    def __init__(self):
        super().__init__()
        self.uart_bus=bus.UartBus.UartBus()

    def probe(self):
        # init device
        try:
            if not self.uart_bus or not self.uart_bus.probe(): #UART bus not exist
                return False

            # try to read a line of data from the serial port and parse
            if not self.read_val() :
                raise ValueError('no particles sensor data')
        except Exception:
            app_logger.exception("parcticles probe exception:")
            return False

        return True

    def disable(self):
        with self.lock:
            if self.sleep_timer and self.sleep_timer.is_alive():
                self.sleep_timer.cancel()
            self.set_sleep(True)

        super().disable()

    #for internal usage inside read_val
    def read_data(self):
        try:
            self.uart_bus.acqure_lock_switch_to_measure_particles()
            time.sleep(0.1) #for stabilize processes

            frame = get_frame(self.uart_bus)
        except Exception:
            app_logger.exception("particles get frame got exception:")
        else:
            if not valid_frame_checksum(frame):
                app_logger.error('frame checksum mismatch')
                return None
            data = {'data': decode_frame(frame)}
            version, error_code = get_version_and_error_code(frame)
            data['version'] = version
            data['errcode'] = error_code
            return data
        finally:
            self.uart_bus.release_lock_switch()
        return None

    def set_sleep(self, mode):
        try:
            self.uart_bus.acqure_lock_switch_to_measure_particles()
            set_sleep_mode(self.uart_bus, mode)
        except Exception:
            app_logger.exception("set sleep exception:")
        finally:
            self.uart_bus.release_lock_switch()

    def sleep_sensor_callback(self, count):
        with self.lock:
            try:
                #print("sleep sensor "+str(count)+", "+str(datetime.now()))
                self.set_sleep(True)
            except Exception:
                app_logger.exception("sleep sensor exception:")

    def read_val(self):
        value = None
        sensor_warm = False
        timeout = time.time() + 20   # 5 seconds only for warm up

        while time.time() < timeout:
            with self.lock:
                try:

                    if self.sleep_timer and self.sleep_timer.is_alive():
                        self.sleep_timer.cancel()
                        sensor_warm = True

                    #waking up sensor - allways
                    self.set_sleep(False)

                    if not sensor_warm:
                        #print ("wating particles sensor warm up")
                        time.sleep(5)  # waiting sensor warm up
                    else:
                        #print ("partilces not warming")
                        pass

                    data = self.read_data()

                    if not data:
                        raise ValueError('no data from particles sensor')
                    if data['errcode'] == 8:
                        # data not ready as I understand
                        continue
                    if data['errcode'] != 0:
                        raise ValueError('got error: {}'.format(data['errcode']))
                    # for k in sorted(data['data'], key=lambda x: int(x)):
                        #v = data['data'][k]
                        # if v[]]
                        #print('{}: {} {}'.format(v[0], v[1], v[2]))
                    value=data
                except Exception:
                    app_logger.exception("particles read exception:")
                else:
                    break
                finally:
                    # so sensor will not sleep during constant update over server
                    #print("start sleep timer "+str(self.sleep_count)+", "+str(datetime.now()))
                    self.sleep_timer = threading.Timer(10, self.sleep_sensor_callback, [self.sleep_count])
                    self.sleep_timer.start()
                    self.sleep_count = self.sleep_count+1

        self.data_bus.particles=value
        return value

    def get_status_str(self):
        ret = ""
        if not self.data_bus.particles:
            self.read_val()

        if self.data_bus.particles:
            pm1 = self.data_bus.particles['data']['8']
            pm25 = self.data_bus.particles['data']['10']
            pm10 = self.data_bus.particles['data']['12']

            ret += 'Particles {}: {} {}\n'.format(pm1[0], pm1[1], pm1[2])
            ret += 'Particles {}: {} {}\n'.format(pm25[0], pm25[1], pm25[2])
            ret += 'Particles {}: {} {}'.format(pm10[0], pm10[1], pm10[2])
        else:
            ret += "not readed"
        return ret

