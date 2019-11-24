#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, sys

pathname = os.path.dirname(sys.argv[0])
work_dir=os.path.abspath(pathname)
sys.path.insert(0, work_dir+'/common') # for common python modules


import serial.tools.list_ports

from time import sleep
import time as tm
import subprocess
import signal
import argparse
import socket

import RPi.GPIO as GPIO

#my imports
import devices
import sensors
import controls #namely in this sequence - controls after devices and sensors
import database
import sound

from check_instance import check_only_one_instance
import utils.common
import my_logging
from utils.common import get_time

from bot import send_warning_telegram
from bot import stop_bot
from bot import start_bot
import web_server
import sopare_plugin
import TTS
import STT
import watch_thread

import config

# GLOBAL
# this must be first in case script run not from home path
os.chdir(work_dir)

#   LOGGING
my_logging.my_init_logging()

#   CHECK ONLY 1 INSTANCE of APPLICATION RUNNING
check_only_one_instance()

def stop_all_devices():
    devices.disable()
    watch_thread.deinit()
    STT.deinit()  # this must be at the end
    sound.deinit()
    sensors.disable()


#   HANDLE CTRL+C
def signal_handler(signal, frame):
    my_logging.logger.error('You pressed Ctrl+C, start stopping all ...')
    stop_all_devices()
    stop_bot()
    my_logging.logger.error('You pressed Ctrl+C, all stopped !')
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

def syscmd(cmd, encoding=''):
    """
    Runs a command on the system, waits for the command to finish, and then
    returns the text output of the command. If the command produces no text
    output, the command's return code will be returned instead.
    """
    p = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        close_fds=True)
    p.wait()
    output = p.stdout.read()
    if len(output) > 1:
        if encoding: return output.decode(encoding)
        else: return output
    return p.returncode

def init():

    syscmd("jack_control start")

    # GPIO setup
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)

    sensors.init()
    devices.init()
    #controls init must be after devices and sensors, because it using them
    controls.init()
    controls.set_telegram_warning_handle(send_warning_telegram)

    sound.init()  # must be after controls

    # arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--time")
    parser.add_argument("--check_water_level", action='store_true')
    args = parser.parse_args()
    if args.time:
        config.DEF_TIME_WATER_S = int(args.time)

    #just check water level
    if args.check_water_level:
        my_logging.logger.info(
            "water level: " + ("ok" if check_water_level() else "low"))
        exit()

    my_logging.logger.info("this is "+socket.gethostname()+" and we will run server and telegram bot")
    web_server.run(__name__)
    start_bot()

    status=devices.get_status_str()+sensors.get_status_str()+controls.get_status_str()
    my_logging.logger.info(status)

    TTS.init()  # this must be before STT
    # sopare_plugin.init()
    STT.init()  # this must be at the end

    watch_thread.init()

    my_logging.logger.info("end init")

#   MAIN
if __name__ == "__main__":

    init()

    my_logging.logger.info("Script started")
    my_logging.logger.info("time for watering = " + str(config.DEF_TIME_WATER_S)+" s")

    if controls.get(controls.control_NoisyActions).check_speech_allowed():
        TTS.say("Умный дом перезапущен.")

    # TTS.say(utils.common.get_weather_desc())
    # MAIN LOOP
    while True:
       STT.listen_cycle()

    stop_all_devices()
    my_logging.logger.info("Script ended " + get_time())
    GPIO.cleanup()
