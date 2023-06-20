from threading import Lock
from abc import ABC, abstractmethod
import TTS

class RootSkill(ABC):
    name="unknown"
    lock = None
    __send_telegram_warning_handle=None

    def __init__(self, name):
        self.name="skill "+name
        self.lock = Lock()

    def say(self, text:str):
        TTS.say(text)

    def say_ok(self, text:str):
        TTS.say("Выполняю : "+text)

    def stop(self):
        '''if you need it override'''
        pass

    def deinit(self):
        '''if you need it override'''
        pass

    @abstractmethod
    def process(self, command:str)->bool:
        return False

    @abstractmethod
    def get_desc(self)->str:
        return ""

    def send_telegram_warning(self, text):
        if self.__send_telegram_warning_handle:
            self.__send_telegram_warning_handle(text)

    def set_telegram_warning_handle(self, send_telegram_warning_handle):
        self.__send_telegram_warning_handle=send_telegram_warning_handle
