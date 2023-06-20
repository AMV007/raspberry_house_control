import RPi.GPIO as GPIO

import config

import time
from time import sleep
from datetime import datetime, time as datetime_time, timedelta

from utils.common import get_time
import app_logger

import Adafruit_DHT

from RootSensor import RootSensor

def usleep(x): return sleep(x/1000000.0)

def read_raw_val(pin):
    max_wait_count = 10000
    error = 0
    raw_val = []
    res = [int(0)]*5

    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.HIGH)
    usleep(500000)
    GPIO.output(pin, GPIO.LOW)
    usleep(20000)
    GPIO.output(pin, GPIO.HIGH)
    usleep(40)
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    # wait first law
    for count in range(0, max_wait_count):
        if GPIO.input(pin):
            break

    if count == (max_wait_count-1):
        error = -1
        return (res, error)

    # waiting data
    for pulse in range(0, 41):
        for count in range(0, max_wait_count):
            if not GPIO.input(pin):
                break
        raw_val.append(count)
        if count == (max_wait_count-1):
            error = -2
            return (res, error)

        for count in range(0, max_wait_count):
            if GPIO.input(pin):
                break
        raw_val.append(count)
        if count == (max_wait_count-1):
            error = -3
            return (res, error)

    count = 0
    for pulse in range(1, 81, 2):
        indx = int(count/8)
        count = count+1
        res[indx] <<= 1
        if raw_val[pulse+1] >= raw_val[pulse]:
            res[indx] |= 0x1

    # check parity
    if not res[4] == ((res[0]+res[1]+res[2]+res[3]) & 0xff):
        error = -4
        return (res, error)

    return (res, error)

class TempHum(RootSensor):

    def probe(self):
        with self.lock:
            if not hasattr(config, "GPIO_GET_TEMP_HUMID"):
                return False

            GPIO.setup(config.GPIO_ENABLE_POWER_TEMP_HUM, GPIO.OUT)
            GPIO.output(config.GPIO_ENABLE_POWER_TEMP_HUM, GPIO.LOW)
            GPIO.setup(config.GPIO_GET_TEMP_HUMID, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        return True

    def read_dht22_data(pin):
        humidity = 0
        temperature = 0
        data, error = read_raw_val(pin)
        if not error == 0:
            return (humidity, temperature, error)

        temperature = float(((data[2] & 0x7F) << 8 | data[3])) / 10
        humidity = float((data[0] << 8 | data[1])) / 10
        if (data[2] & 0x80) != 0:
            temperature = -temperature
        return (humidity, temperature, error)


    def read_val(self):
        with self.lock:
            tot_humidity = 0
            tot_temperature = 0
            try:
                num_good_cycles = 0
                num_cycles_wrong = 0

                GPIO.output(config.GPIO_ENABLE_POWER_TEMP_HUM, GPIO.HIGH)
                # sleep(1) # wait sensor warm up - not waiting now, because at's constantly enabled
                timeout = time.time() + 5   # 5 seconds
                while time.time() < timeout:
                    error = 0
                    humidity, temperature = Adafruit_DHT.read_retry(config.TEMP_DHT_VER, config.GPIO_GET_TEMP_HUMID)
                    #humidity, temperature,error=read_dht22_data(config.GPIO_GET_TEMP_HUMID) # my implemented read

                    if error == 0 and temperature != None and humidity < 100 and humidity > 5:
                        tot_humidity += humidity
                        tot_temperature += temperature
                        num_good_cycles+=1
                        if num_good_cycles>3:
                            break # enough good data
                    else:
                        num_cycles_wrong+=1

                GPIO.output(config.GPIO_ENABLE_POWER_TEMP_HUM, GPIO.LOW)

                if num_good_cycles > 0 :
                    tot_humidity /= num_good_cycles
                    tot_temperature /= num_good_cycles
                else:
                    #to not enable fan by default
                    tot_humidity=50
                    tot_temperature=25
                    app_logger.debug("can't measure temperature and humidity, wrong cycles: "+str(num_cycles_wrong))

                #app_logger.info( 'Temp: {0:0.1f} C  Humidity: {1:0.1f} %'.format(tot_temperature, tot_humidity)+", num cycles: "+str(num_cycles_wrong))
            except Exception as e:
                app_logger.exception("get temp error, temp="+str(tot_temperature)+", hum="+str(tot_humidity))
            finally:
                self.data_bus.temperature=tot_temperature
                self.data_bus.humidity=tot_humidity
                return (tot_temperature, tot_humidity, num_cycles_wrong)

    def get_status_str(self):
        if not self.data_bus.temperature:
            self.read_val()

        ret = 'Temp: {0:0.1f} °C \nHumidity: {1:0.1f} %\n'.format(
            self.data_bus.temperature, self.data_bus.humidity,)
        return ret
