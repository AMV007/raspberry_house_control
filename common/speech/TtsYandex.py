import requests
from TtsBase import TtsBase
from yandex_speech import TTS as yTTS
from utils_sound import play_audio_file

class TtsYandex(TtsBase):
    __key=""
    speaker = None # jane | oksana | alyss | omazh | zahar | ermil
    sample_rate = None

    def __init__(self, logger, sound_device=None, speaker='oksana', key="", sample_rate = 48000):
        super().__init__(logger, sound_device)
        self.speaker = speaker
        self.sample_rate = sample_rate
        self.__key = key

    def save_to_wav(self,text:str, file:str)->bool:
        super().save_to_wav(text, file)

        tts = yTTS(speaker=self.speaker, audio_format="wav",
                key=self.__key, emotion="good", speed=1)
        tts.generate(text)
        tts.save(file)
        return True

    def say_raw(self,text:str):
        URL = 'https://tts.voicetech.yandex.net/generate?text='+text + \
            '&format=wav&quality=hi&lang=ru-RU&speaker=' + \
            self.speaker+'&key='+self.__key+'&speed=0.9&emotion=good'
        response = requests.get(URL)
        if response.status_code == 200:
            with open(TtsBase.TEMP_WAV_FILE, 'wb') as file:
                file.write(response.content)
            play_audio_file(TtsBase.TEMP_WAV_FILE,self._sound_device, self._force_stop)
        else:
            raise ValueError('error play Yandex Cloud, error=' +
                            str(response.status_code)+"\n text="+text)
