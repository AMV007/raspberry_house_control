import os, sys
from threading import Thread
from time import sleep

#my imports
import devices
import sensors
import controls
import sound
from threading import Event

import app_logger
import config

Running = None
thread = None

exit = Event()

def init():
    global thread
    global Running

    Running = True
    thread = Thread(target=listen_thread, args=(10, ))
    thread.start()

def deinit():
    global thread
    global Running
    Running = False
    exit.set()

    app_logger.info("start stoping "+os.path.basename(__file__))
    if thread != None:
        thread.join()
    app_logger.info(__file__+" stopped")

def listen_thread(arg):
    while Running:
        try:
            noisy_time=controls.get(controls.control_NoisyActions).do_check()
            for control in controls.active:
                control.do_check(noisy_time)
                if not Running:
                    return

            exit.wait(config.CHECK_PERIOD_S)
        except Exception:
            app_logger.exception("watch thread exception:")
            exit.wait(config.CHECK_PERIOD_S) # for not spam
            pass
