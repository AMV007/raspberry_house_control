from TtsBase import TtsBase
from gtts import gTTS
from utils_sound import convert_to_wav

class TtsGoogle(TtsBase):
    speaker = None
    samplerate = None
    language = 'ru'
    TEMP_MP3_FILE="/dev/shm/say.mp3"

    def __init__(self, logger, sound_device=None, speaker='baya', samplerate=44100):
        super().__init__(logger, sound_device)
        self.speaker = speaker
        self.samplerate = samplerate

    def save_to_wav(self,text:str, file:str)->bool:
        super().save_to_wav(text, file)


        # Passing the text and language to the engine,
        # here we have marked slow=False. Which tells
        # the module that the converted audio should
        # have a high speed
        myobj = gTTS(text=text, lang=self.language, slow=False)

        # Saving the converted audio in a mp3 file named
        myobj.save(self.TEMP_MP3_FILE)
        convert_to_wav(self.TEMP_MP3_FILE, self.samplerate, file)
        return True
