#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, sys

import subprocess
import socket
from time import sleep
from common import *

import RPi.GPIO as GPIO

#this must be here for include common folder as source !!!
pathname = os.path.dirname(sys.argv[0])
work_dir = os.path.abspath(pathname)
os.chdir(work_dir)  # if call from not script dir

#my imports
import devices
import sensors
import controls #namely in this sequence - controls after devices and sensors

import sound

from GracefulKiller import GracefulKiller
from check_instance import check_only_one_instance
import app_logger
from utils.common import get_time

from BotImpl import BotImpl
import web_server
import TTS
import STT
import VA
import watch_thread

import config

bot = None

#   CHECK ONLY 1 INSTANCE of APPLICATION RUNNING
check_only_one_instance()

def stop_all_devices():
    app_logger.warn('Start stopping all devices ...')
    devices.disable()
    watch_thread.deinit()
    VA.deinit()  # this must be at the end
    STT.deinit()  # this must be at the end
    TTS.deinit()  # this must be at the end
    sound.deinit() # this must be after TTS and STT
    sensors.disable()
    app_logger.warn('All devices stopped')

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


def send_warning_telegram(message):
    bot.send_msg_bot_long_check(str(config.my_telegram_id), message)

def init():
    global bot
    app_logger.info("start init ...")

    # GPIO setup
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(True)

    sensors.init(app_logger.logger)
    devices.init(app_logger.logger)
    #controls init must be after devices and sensors, because it using them
    controls.init(app_logger.logger, send_warning_telegram)

    sound.init(app_logger.logger)  # must be after controls

    bot = BotImpl() #must be after all controls otherwise watering control will be empty

    app_logger.info("this is "+socket.gethostname()+" and we will run server and telegram bot")
    web_server.run(__name__)

    status=devices.get_status_str()+sensors.get_status_str()+controls.get_status_str()
    app_logger.info(status)

    watch_thread.init()

    bot.start()

    TTS.init()  # this must be before STT
    STT.init(True)  # this must be at the end
    VA.init(send_warning_telegram)  # this must be at the end

    app_logger.info("end init")

#   MAIN
if __name__ == "__main__":
    try:
        killer = GracefulKiller(stop_all_devices)

        init()

        app_logger.info("Script started")
        app_logger.info("time for watering = " + str(config.DEF_TIME_WATER_S)+" s")
        app_logger.info("!!! ALL STARTED !!!")
        if config.NOTIFY_DEVICE_START:
            TTS.say(TTS.Commands.SMART_HOUSE_STARTED)

        killer.wait_app_exit()
    except KeyboardInterrupt:
        print("Ctrl-c pressed ...")
    except Exception as e:
        app_logger.exception("main exception:")
    finally:
        stop_all_devices() # in case they are not stopped from Ctrl+C

        if bot:
            bot.stop()
        sleep(1) #wait all finish
        GPIO.cleanup()
        app_logger.info("All finished...exiting")

