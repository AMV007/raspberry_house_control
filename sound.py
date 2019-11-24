import my_logging
import os
import threading

#to hide pygame import message
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame

import pyaudio
from ctypes import *
import wave

import pyttsx3

import config
import controls

lock = None
asound=None
os.environ['SDL_VIDEODRIVER'] = 'dummy'  # for headless pygame

# ---------------------------- to remove pyaudio errors in text
# From alsa-lib Git 3fd4ab9be0db7c7430ebd258f2717a976381715d
# $ grep -rn snd_lib_error_handler_t
# include/error.h:59:typedef void (*snd_lib_error_handler_t)(const char *file, int line, const char *function, int err, const char *fmt, ...) /* __attribute__ ((format (printf, 5, 6))) */;
# Define our error handler type
ERROR_HANDLER_FUNC = CFUNCTYPE(None, c_char_p, c_int, c_char_p, c_int, c_char_p)

def py_error_handler(filename, line, function, err, fmt):
    pass

c_error_handler = ERROR_HANDLER_FUNC(py_error_handler)

def init():
    global lock
    global asound
    lock = threading.Lock()
    # to suppress errors from asound library, because this thread using audio constantly - removed audio error
    # supporess from other modules
    asound = cdll.LoadLibrary('libasound.so')
    asound.snd_lib_error_set_handler(c_error_handler)  # Set error handler

def deinit():
    asound.snd_lib_error_set_handler(None)

def beep(duration_s=3, force=False):  # duration in floating point !

    freq = 600  # Hz
    #os.system('speaker-test -c1 -t sine -f %f -P %s -p 0.4 -l 1' % (freq,duration))
    os.system('play --no-show-progress --null --channels 1 synth %s sine %f' %
              (duration_s, freq))


def play_wav(name, force=False):

    # define stream chunk
    chunk = 32768

    # open a wav format music
    f = wave.open(name, "rb")

    p = pyaudio.PyAudio()
    # open stream
    stream = p.open(format=p.get_format_from_width(f.getsampwidth()),
                    channels=f.getnchannels(),
                    rate=f.getframerate(),
                    output=True)
    # read data
    data = f.readframes(chunk)

    # play stream
    while data:
        stream.write(data)
        data = f.readframes(chunk)

    # stop stream
    stream.stop_stream()
    stream.close()

    # close PyAudio
    p.terminate()


def play_command(name):
    filename = "sound/"+name+".wav"
    play_file(filename)


def play_file(filename, delete_after=False):
    with lock:
        try:
            pygame.mixer.init()

            pygame.mixer.music.load(filename)
            pygame.mixer.music.play()

            while pygame.mixer.music.get_busy():
                pygame.time.wait(100)  # 100 ms

            pygame.mixer.quit()

            if delete_after:
                os.remove(filename)
        except Exception as e:
            my_logging.logger.exception("pygame play sound exception:")
