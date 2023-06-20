import os
import torch
import sounddevice as sd
import soundfile as sf
from decimal_to_text_ru import replace_numbers
from TtsBase import TtsBase
from utils_sound import play_audio_file
from transliterate import translit, get_available_language_codes
from multiprocessing import cpu_count

list_of_chars_for_remove = ['{', '}', '[', ']', '(',')']
def remove_spec_symbols(text:str):
    for character in list_of_chars_for_remove:
        text = text.replace(character, '')
    return text

def prepare_text(text:str):
    text=remove_spec_symbols(text)
    text=replace_numbers(text)
    text=translit(text, 'ru')
    return text

class TtsSilero(TtsBase):
    __model = None
    __device = None
    speaker = None
    sample_rate = None
    language = None

    #speakers: aidar, baya, kseniya, xenia, eugene, random
    def __init__(self, logger, sound_device=None, device_name="cpu", sample_rate=24000,
                 speaker='kseniya', language = 'ru', model_id = 'v3_1_ru'):
        super().__init__(logger, sound_device)
        self.speaker = speaker
        self.language = language
        self.sample_rate = sample_rate #get_audio_device_sd_samplerate(device_index)

        # a bit faster than next approach
        try:
            self.__model, _ = torch.hub.load(repo_or_dir='snakers4/silero-models',
                                        model='silero_tts',
                                        language=self.language,
                                        speaker=model_id)
        except:
            try:
                #tryint to find offline
                self.__model, _ = torch.hub.load(f"{os.path.expanduser('~')}/.cache/torch/hub/snakers4_silero-models_master",
                                            model='silero_tts',
                                            source='local',
                                            language=self.language,
                                            speaker=model_id)
            except:
                logger.exception("error load silero engine")

        # local_file = 'model.pt'
        # if not os.path.isfile(local_file):
        #    torch.hub.download_url_to_file('https://models.silero.ai/models/tts/ru/v3_1_ru.pt',
        #                                local_file)
        # self.__model = torch.package.PackageImporter(local_file).load_pickle("tts_models", "model")

        torch.set_num_threads(cpu_count())
        self.__device = torch.device(device_name)
        self.__model.to(self.__device)

    def save_to_wav(self,text:str, file:str)->bool:
        text=prepare_text(text)
        super().save_to_wav(text, file)

        self.__model.save_wav(
                                    audio_path=file,
                                    text=text,
                                    speaker=self.speaker,
                                    sample_rate=self.sample_rate)
        return True

    def say_raw(self, text:str):
        text=prepare_text(text)
        if not text:
            raise ValueError(f"empty string: {text}")

        audio = self.__model.apply_tts(text=text,
                                    speaker=self.speaker,
                                    sample_rate=self.sample_rate)

        sf.write(TtsBase.TEMP_WAV_FILE, audio, self.sample_rate)
        if self._sound_device:
            play_audio_file(TtsBase.TEMP_WAV_FILE,self._sound_device, self._force_stop)
            return True

        return False


