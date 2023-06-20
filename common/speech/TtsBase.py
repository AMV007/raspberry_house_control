import os
import threading
from utils_sound import play_audio_file

class TtsBase:
    _logger = None
    _sound_device = None
    _force_stop = [False]
    _say_end_event = threading.Event() #raised at the say end

    TEMP_WAV_FILE="/dev/shm/say.wav"

    def __init__(self, logger, sound_device=None,):
        self._logger=logger
        self._sound_device=sound_device
        self._say_end_event.set() # we finished talking from the begining
        if logger:
            logger.info(f"{self.__class__.__name__} initing ...")

    def save_to_wav(self,text:str, file:str)->bool:
        """say text override this method"""

        if not text:
            raise ValueError(f"empty text string: {text}")

        if os.path.exists(file):
            os.remove(file)

        return False

    def say(self, text:str):
        if not text:
            raise ValueError(f"empty string: {text}")

        try:
            self.force_continue()
            self._say_end_event.clear()

            if self.save_to_wav(text, TtsBase.TEMP_WAV_FILE):
                play_audio_file(TtsBase.TEMP_WAV_FILE, self._sound_device, self._force_stop)
            else:
                raise ValueError(f"can't save to file: {text}")
        finally:
            self._say_end_event.set()

    def wait_end_say(self, timeout:float=None):
        return self._say_end_event.wait(timeout)

    def is_force_stop(self):
        return self._force_stop[0]

    def force_stop(self):
        self._force_stop = [True]

    def force_continue(self):
        self._force_stop = [False]