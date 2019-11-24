# Text To Speech
import os
import threading
from gtts import gTTS
from yandex_speech import TTS as yTTS

import requests

import TTS

import my_logging
import sound

lock = None


def init():
    global lock
    lock = threading.Lock()


def say(text):
    lock.acquire()
    try:
        sayGoogle(text)
        # sayYandex(text)
        # sayYandexRaw(text)
        # sayOffline(text)
        return True
    except Exception as e:
        my_logging.logger.exception("voice recognition exception:")
        return False
    finally:
        lock.release()


def sayYandex(text):
    filename = "/dev/shm/say.mp3"
    speaker = "oksana"  # jane | oksana | alyss | omazh | zahar | ermil
    tts = yTTS(speaker=speaker, audio_format="mp3",
               key="b4360d0c-eab6-4be7-9fa7-fb034cf41d17", emotion="good", speed=1)
    tts.generate(text)
    tts.save(filename)

    sound.play_file(filename, False)


def sayYandexRaw(text):
    key = "b4360d0c-eab6-4be7-9fa7-fb034cf41d17"
    filename = "/dev/shm/say.mp3"
    speaker = "oksana"  # jane | oksana | alyss | omazh | zahar | ermil
    URL = 'https://tts.voicetech.yandex.net/generate?text='+text + \
        '&format=mp3&quality=hi&lang=ru-RU&speaker=' + \
        speaker+'&key='+key+'&speed=0.9&emotion=good'
    response = requests.get(URL)
    if response.status_code == 200:
        with open(filename, 'wb') as file:
            file.write(response.content)
            file.close()
        sound.play_file(filename, False)
    else:
        raise ValueError('error play Yandex Cloud, error=' +
                         str(response.status_code)+"\n text="+text)


def sayGoogle(text):
    filename = "/dev/shm/say.mp3"
    language = 'ru'
    # Passing the text and language to the engine,
    # here we have marked slow=False. Which tells
    # the module that the converted audio should
    # have a high speed
    myobj = gTTS(text=text, lang=language, slow=False)

    # Saving the converted audio in a mp3 file named
    # welcome
    myobj.save(filename)

    sound.play_file(filename, True)

# this one real shitty


def sayOffline(text):

    #asound = cdll.LoadLibrary('libasound.so')
    # asound.snd_lib_error_set_handler(c_error_handler) # Set error handler

    engine = pyttsx3.init()
    engine.setProperty('voice', 'russian')
    engine.say(text)
    engine.runAndWait()

    # asound.snd_lib_error_set_handler(None)
