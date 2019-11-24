import os, sys
from threading import Thread
from time import sleep

#my imports 
import devices
import sensors
import controls
import sound

import my_logging
import config

Running = None
thread = None

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
    print("start stoping "+os.path.basename(__file__))
    if thread != None:
        thread.join()
    print(__file__+" stopped")


def listen_thread(arg):
    while Running:
        try:
            noisy_time=controls.get(controls.control_NoisyActions).do_check()
            for control in controls.active:
                control.do_check(noisy_time)
                if not Running:
                    break
            sleep(config.CHECK_PERIOD_S)
        except Exception as e:
            my_logging.logger.exception("main exception:")
            pass
