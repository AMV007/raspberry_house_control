# Text To Speech
import os
import time
from threading import Thread
import queue
from enum import Enum

import app_logger
import sound
import config
from utils_sound import play_audio_file

from common.speech.TtsBase import TtsBase
from common.speech.TtsSilero import TtsSilero
from common.speech.TtsGoogle import TtsGoogle
from common.speech.TtsYandex import TtsYandex
from common.speech.TtsSphinx import TtsSphinx

thread_tts = None
tts_engine_online = None
tts_engine_offline = None # if online not working
tts_queue = queue.Queue()
Running = True
last_say_time = time.time()

WAV_FOLDER="wav"

class Commands(Enum):
    HELLO = 1
    EXECUTE = 2
    THINK = 3
    SMART_HOUSE_STARTED = 4

#for faster say response
commands = {
    Commands.HELLO: "Привет, как дела",
    Commands.EXECUTE: "Выполняю",
    Commands.THINK: "Надо подумать",
    Commands.SMART_HOUSE_STARTED: f"Ассистент {config.TTS_KEYWORD} запущен",
}

def generate_commands():
    if not os.path.exists(WAV_FOLDER):
        os.makedirs(WAV_FOLDER)
    for command in Commands:
        text=commands.get(command)
        filename = f"{WAV_FOLDER}/{command.name}.wav"
        if not os.path.exists(filename):
            try:
                tts_engine_online.save_to_wav(text, filename)
            except:
                tts_engine_offline.save_to_wav(text, filename)

def say_command(command:Commands):
    filename = f"{WAV_FOLDER}/{command.name}.wav"
    play_audio_file(filename, sound.jabra_device_name_pygame)

def say_text(text)->TtsBase:
    try:
        app_logger.info(f"start to say: {text}")
        tts_engine_online.say(text)
        return tts_engine_online
    except Exception:
        app_logger.exception("tts recognition exception online, trying offline:")
        tts_engine_offline.say(text)
        return tts_engine_offline

def tts_thread():
    global last_say_time

    while Running:
        try:
            text = tts_queue.get(timeout=1)

            if isinstance(text, Enum):
                say_command(text)
            else:
                tts_engine=say_text(text)
                if not tts_engine.is_force_stop():
                    last_say_time = time.time() #keep talinkg if not stopped
        except queue.Empty:
            pass
        except Exception:
            app_logger.exception("tts thread exception:")

    app_logger.warn("tts thread exited")

def say(text):
    tts_queue.put(text)

def stop_say():
    global last_say_time

    tts_queue.queue.clear()

    if tts_engine_online:
        tts_engine_online.force_stop()
        tts_engine_online.wait_end_say()
    if tts_engine_offline:
        tts_engine_offline.force_stop()
        tts_engine_offline.wait_end_say()

    last_say_time -= 100 # for stop recognition without keyword

def init():
    global tts_engine_online
    global tts_engine_offline
    global thread_tts

    try:
        tts_engine_online = TtsGoogle(app_logger.logger, sound.jabra_device_name_pygame)
    except:
        app_logger.exception("error online TTS")
        tts_engine_online = None
    try:
        tts_engine_offline = TtsSilero(app_logger.logger, sound.jabra_device_name_pygame)
    except:
        app_logger.exception("error init offline TTS")
        tts_engine_offline = None

    #tts_engine_online = TtsYandex(app_logger.logger, sound.jabra_device_name_pygame, key=config.yandex_key)
    #tts_engine = TtsSphinx(app_logger.logger, sound.jabra_device_name_pygame)

    generate_commands()

    thread_tts = Thread(target=tts_thread)
    thread_tts.kill_received = False
    thread_tts.start()

def deinit():
    global Running
    global thread_tts
    if Running:
        Running = False

        app_logger.info("start stoping "+os.path.basename(__file__))
        stop_say()
        if thread_tts != None:
            thread_tts.kill_received = True
            thread_tts.join()
            thread_tts = None

        app_logger.info("end stoping "+os.path.basename(__file__))
