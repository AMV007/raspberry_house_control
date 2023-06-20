import sys
import os
import speech_recognition as sr
from datetime import datetime

from SttBase import SttBase

pathname = os.path.dirname(sys.argv[0])
work_dir = os.path.abspath(pathname)


class SttGoogle(SttBase):
    __device_index = 0 #audio microphone device index
    __use_key = True
    __use_key_day = datetime.now().day
    __recognizer = None
    __google_key = None

    def __init__(self, logger, google_key: str, device_index:int=-1, keywords=None):
        super().__init__(logger,keywords)

        self.__device_index = device_index
        self.__google_key = google_key

        self.__recognizer = sr.Recognizer()


    ################### threaded function
    def wait_voice(self, noise_detect_len=None):
         # for minimize lag between input and start listening - specifying microphone device by number
         with sr.Microphone(device_index=self.__device_index) as source:
            if noise_detect_len != None:
                # recognizer.adjust_for_ambient_noise(source, duration=noise_detect_len) # to remove noise environment
                pass
            audio = self.__recognizer.listen(source, timeout=5)
            return audio

    def recognize(self, voice_required_try=None, noise_detect_len=None):

        phrase = ""

        speech_listened_and_recognized = False
        while not speech_listened_and_recognized and not self.is_force_stop():
            try:
                audio = self.wait_voice(noise_detect_len)

                speech_recognized = False
                while not speech_recognized and not self.is_force_stop():
                    # because google service can not approve my key due to limit of requests
                    try:
                        if self.__use_key:
                            # if using my key, recognition working faster
                            key = self.__google_key
                            phrase = self.__recognizer.recognize_google(
                                audio, language="ru-RU", key=key)
                            speech_recognized = True
                        else:
                            phrase = self.__recognizer.recognize_google(
                                audio, language="ru-RU")
                            if self.__use_key_day != datetime.now().day:
                                self.__use_key = True  # day changed, trying 50 call limitations on next day
                            speech_recognized = True
                    except sr.RequestError as e:
                        self.__use_key_day = datetime.now().day
                        exit.wait(60); # add delay at 1 minute

                speech_listened_and_recognized = True
            except sr.WaitTimeoutError:
                pass
            except sr.UnknownValueError:
                # error recognize, looking like empty request lets try again
                if voice_required_try != None:
                    voice_required_try -= 1
                    if voice_required_try == 0:
                        return None

        return phrase.lower()




