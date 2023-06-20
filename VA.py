# Text To Speech
import os
from threading import Thread
from concurrent.futures import ThreadPoolExecutor
import queue
from babel.dates import format_date, format_datetime, format_time
from datetime import date, datetime, time, timedelta
import subprocess

import app_logger
import config
import TTS
import utils.common
import va_skills

thread_va = None
va_queue = queue.Queue()
Running = True

exec_pool = None

def process_comand(text:str):
    va_queue.put(text)

def init(telegram_warning_handle):
    global exec_pool
    global thread_va

    va_skills.init(app_logger.logger, telegram_warning_handle)

    exec_pool = ThreadPoolExecutor(max_workers=20)
    thread_va = Thread(target=va_thread)
    thread_va.kill_received = False
    thread_va.start()

def deinit():
    global Running
    global thread_va
    if Running:
        Running = False

        app_logger.info("start stoping "+os.path.basename(__file__))

        if exec_pool:
            exec_pool.shutdown(wait=True)

        if thread_va != None:
            thread_va.kill_received = True
            thread_va.join()
            thread_va = None

        va_skills.deinit()
        app_logger.info("end stoping "+os.path.basename(__file__))

def va_thread():
    while Running:
        try:
            text = va_queue.get(timeout=1)
            va_queue.task_done()
            exec_pool.submit(exec_command_internal, text)
        except queue.Empty:
            pass
        except Exception:
            app_logger.exception("VA thread exception:")
    app_logger.warn("VA thread exited")

def exec_command_internal(command):

    if len(command) <= 2:
        app_logger.info("command ignore:"+str(command))
        return # ignore error recognition 1-2 chars

    app_logger.info("command:"+str(command))

    TTS.stop_say()

    num_words=len(command.split())
    if num_words >= 30:
        TTS.say("очень длинная фраза, покороче пожалуйста")
    elif command in ["стоп", "остановись","хватит","стол","да стол"]:
        va_skills.stop()
        TTS.stop_say()
        TTS.say("хорошо")
    else:
        va_skills.process(command)

def say_ok(command):
    TTS.say("Выполняю : "+command)
