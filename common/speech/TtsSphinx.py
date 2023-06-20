from decimal_to_text_ru import replace_numbers
from TtsBase import TtsBase
import pyttsx3

class TtsSphinx(TtsBase):
    speaker = None

    def __init__(self, logger, sound_device=None, speaker='russian'):
        super(TtsSphinx, self).__init__(logger, sound_device)
        self.speaker = speaker

    def save_to_wav(self,text:str, file:str)->bool:
        super().save_to_wav(text, file)

        engine = pyttsx3.init()
        engine.setProperty('voice', self.speaker)
        engine.save_to_file(text,file)
        engine.runAndWait()
        return True


