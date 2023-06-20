#!/usr/bin/env python3
# Requires PyAudio and PySpeech.
# Speech To Text

import sys,os
import time
from threading import Thread
from threading import Event

import app_logger
import sound
import TTS
import VA

import config
from common.speech.SttVosk import SttVosk

KEEP_SPEECH_TIMEOUT=6 # time during what will be ready for continue talk without keyword, in RPI4 8 gb 3.5 good, with 4 gb 6 good ?
pathname = os.path.dirname(sys.argv[0])
work_dir=os.path.abspath(pathname)

thread_listen = None
recognition = None
Running = True

keywords = [config.TTS_KEYWORD]

def init(use_thread=False):
    global thread_listen
    global thread_notify
    global recognition

    recognition = SttVosk(app_logger.logger, config.vosk_model_path_small, sound.jabra_device_id, keywords)

    if use_thread:
        thread_listen = Thread(target=listen_thread, args=(10, ))
        thread_listen.kill_received = False
        thread_listen.start()

def deinit():
    global thread_listen
    global Running
    if Running:
        Running = False
        app_logger.info("start stoping "+os.path.basename(__file__))
        if recognition:
            recognition.force_stop()

        if thread_listen != None:
            thread_listen.kill_received = True
            thread_listen.join()
            thread_listen = None
        app_logger.info("end stoping "+os.path.basename(__file__))

def listen_thread(arg):
    try:
        if sound.jabra_device_id == -1 :
            app_logger.info(f"no jabra found, no listen: {sound.jabra_device_id}")
            return

        # just thread started and ready for commands
        sound.beep(0.05)
        while Running:
            listen_cycle()
    except Exception:
        app_logger.exception("STT thread exception:")

def remove_prefix(s, prefix):
    return s[len(prefix):] if s.startswith(prefix) else s

def wait_for_keyword():
    while not recognition.is_force_stop():
        text = recognition.recognize()
        if text :
            text=text.strip().lower() # remove spaces and convert to lower case

            app_logger.info(f"STT: {text}")

            #remove keyword from command
            for keyword in recognition.keywords:
                if text.startswith(keyword):
                    return remove_prefix(text, keyword).strip()

            #this must be after keyword in case if keyword was talked again
            time_diff=time.time()-TTS.last_say_time
            if (time_diff) < KEEP_SPEECH_TIMEOUT:
                # we are keep talking no need for keyword check
                return text
    return ""

def listen_cycle():
    try:
        command=wait_for_keyword()

        if not command and Running:
            command = listen_phrase()
        if not command or not Running:
            return

        VA.process_comand(command)

    except Exception:
        app_logger.exception("voice recognition exception:")

def listen_phrase():
    TTS.say("Слушаю")
    command = recognition.recognize(3, 0.5)
    if not command :
        TTS.say("Ни шанса понять, давай все заново")
    return command
