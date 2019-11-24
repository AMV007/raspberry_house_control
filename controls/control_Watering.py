import os
import sys

from ppretty import ppretty

import time as tm
from time import sleep
from datetime import datetime, time as datetime_time, timedelta

# this invokes the secure SMTP protocol (port 465, uses SSL)
from smtplib import SMTP_SSL as SMTP
# Import the email modules we'll need
from email.mime.text import MIMEText

#my imports
import config
from utils.common import get_time

import sensors
import devices

import my_logging
import database

from RootControl import RootControl

class Watering(RootControl):

    time_wait_days=1
    watering_count=0

    MoistureSensor=None
    WaterLevelDropSensor=None

    def __init__(self):
        super().__init__(self.__class__.__name__)
        self.control_devices.extend(devices.get(devices.WaterPump))
        self.control_sensors.extend(sensors.get(sensors.Moisture))
        if len(self.control_sensors)>1:
            raise ValueError("now we are supporting only 1 Moisture sensor")
        self.control_sensors.extend(sensors.get(sensors.WaterLevelDrop))
        if len(self.control_sensors)>2:
            raise ValueError("now we are supporting only 1 WaterLevelDrop sensor")

    def probe(self):
        # just checking right config
        if not hasattr(config, "DEF_TIME_WAIT_DAYS"):
            return False

        if len(self.control_sensors)<2:
            my_logging.logger.error("not enough watering control sensors sount, need 2 sensors for now")
            return False # need 2 sensors for work properly for now 

        self.time_wait_days = config.DEF_TIME_WAIT_DAYS
        self.watering_count = database.get_num_watering_time()

        self.MoistureSensor=self.control_sensors[0]
        self.WaterLevelDropSensor=self.control_sensors[1]

        return super().probe()

    def do_check(self,noisy_time=False):
        with self.lock:

            if not noisy_time:
                return

            now = datetime.now()
            last_updated = self.get_last_watering_time()
            if (now - last_updated) > timedelta(self.time_wait_days):
                if now.hour >= 12 and now.hour < 16:
                    # to not disturb due to regular time watering at the morning and at the evening
                    self.do_watering("regular time")
            elif self.MoistureSensor.read_val():
                self.do_watering("moisture low level")

    def get_last_watering_time(self):
        last_updated = datetime.strptime(
            '10-06-1990 12:00:00', '%d-%m-%Y %H:%M:%S')
        try:
            last_updated = database.get_latest_watering_date()
        except (IOError, ValueError) as e:
            print("Error database.get_latest_watering_date, resetting, error="+str(e))
        return last_updated


    def get_total_watering_count(self):
        count = 0
        try:
            count = database.get_num_watering_time()
        except (IOError, ValueError) as e:
            print("Error database.get_num_watering_time, resetting, error="+str(e))
        return count

    # only possible during watering
    def __check_water_level(self, Notify=True):
        water_low_level = self.WaterLevelDropSensor.read_val()
        database.add_water_level_status(water_low_level)
        if water_low_level and Notify:
            my_logging.logger.info("low level of water")
            self.send_water_warning_mail()
            self.send_telegram_warning(config.warning_message_water)
        return not water_low_level


    def do_watering(self, reason, watering_seconds=config.DEF_TIME_WATER_S, Notify=True):
        #    print "watering start " + get_time()

        for device in self.control_devices:
            device.enable()

        self.time_wait_days = config.DEF_TIME_WAIT_DAYS
        for i in range(0, watering_seconds):
            sleep(1)
            if i > 10 and not self.__check_water_level(False):
                sleep(1)
                if not self.__check_water_level(Notify):
                    self.time_wait_days = 1
                    break

        for device in self.control_devices:
            device.disable()
        database.add_watering_date(watering_seconds, reason)
        my_logging.logger.info("watering done at: " + get_time())
        return self.time_wait_days

    # for bot
    def get_status_str(self):
        ret = database.get_latest_watering_info()+"\n"
        water_low_level = database.get_latest_water_level_status()
        ret += "water level: "
        if water_low_level == None:
            ret += "not measured yet"
        elif water_low_level:
            ret += "low, need water !"
        else:
            ret += "ok"

        return ret

#   -----------------WATERING---------------
    def send_water_warning_mail(self):
        try:
            msg = MIMEText(config.warning_message_water, 'plain')
            msg['Subject'] = "Water level warning !"
            msg['From'] = config.email_sender
            #msg['To'] = config.email_destination not need here, using as function parameter
            conn = SMTP(config.smtp_server)
            conn.set_debuglevel(False)
            conn.login(config.smtp_user, config.smtp_pass)
            try:
                conn.sendmail(config.email_sender,
                            config.email_destination, msg.as_string())
            except:
                my_logging.logger.error("error send mail1 !")
            finally:
                conn.quit()
            my_logging.logger.info("warning mail out ok")
        except Exception as e:
            my_logging.logger.exception("error send mail !"+str(e))
            pass
        return
