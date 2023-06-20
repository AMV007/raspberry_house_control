import sys
import os
import queue
import vosk
from vosk import SetLogLevel
import json
import wave
import sounddevice as sd
import zipfile
import numpy

import noisereduce as nr
from scipy.io import wavfile
import cffi

#for support C
import pyximport; pyximport.install()

import stt_vosk

from utils_common import download_file_progress
from utils_sound import convert_to_wav
from utils_sound import get_audio_device_sd_samplerate
from SttBase import SttBase

pathname = os.path.dirname(sys.argv[0])
work_dir = os.path.abspath(pathname)


class SttVosk(SttBase):
    REC_SAMPLERATE=48000 #recommended by vosk 8000 or 16000 or may be multiplication 8000 also working, using when there are no physical device
    BLOCK_SIZE=1024*16
    __model = None # Create a decoder with certain model
    __device_index = 0 #audio microphone device index
    __samplerate = REC_SAMPLERATE
    __data_queue = queue.Queue()
    ffi = None

    def check_download_model(self, model_name):
        dir_path=os.path.join(work_dir,model_name)
        if not os.path.exists(dir_path):
            self._logger.info(f"model {model_name} not exist, downloading it ...")
            file_name=download_file_progress(f"https://alphacephei.com/vosk/models/{model_name}.zip",os.path.join(work_dir,f"{model_name}.zip"))

            self._logger.info(f"extracting {file_name} ...")
            with zipfile.ZipFile(file_name, 'r') as zip_ref:
                zip_ref.extractall()

            os.remove(file_name)

    def __init__(self, logger, model_name: str, device_index:int=-1, keywords=None):
        super().__init__(logger, keywords)

        self.__device_index = device_index

        self.check_download_model(model_name)
        SetLogLevel(-1) # for remove vosk stdout
        self.__model = vosk.Model(model_name)

        self.__samplerate = get_audio_device_sd_samplerate(device_index)
        self.ffi = cffi.FFI()

    def recognize_wav(self, wav_filename:str, samplerate):
        wf = wave.open(wav_filename)

        try:
            rec = vosk.KaldiRecognizer(self.__model, samplerate)

            while True:
                data = wf.readframes(4000)
                if len(data) == 0:
                    break
                rec.AcceptWaveform(data)

            recognized_data=json.loads(rec.FinalResult())['text']
            return recognized_data
        except Exception:
            self._logger.exception("vosk exception:")

        return self.recognize_data(data, samplerate)

    def recognize_ogg(self, ogg_filename:str):
        wav_filename, samplerate=convert_to_wav(ogg_filename, SttVosk.REC_SAMPLERATE)
        return self.recognize_wav(wav_filename, samplerate)

    ################### threaded function
    def status_callback(self, indata, frames, time, status):
        """This is called (from a separate thread) for each audio block."""
        if status:
            self._logger.error(status)

        array = numpy.arange(len(indata)//2, dtype=numpy.int16)
        data = array.__array_interface__['data'][0]
        cptr = self.ffi.cast ( "char*" , data )
        self.ffi.memmove(cptr, indata, len(indata))

        self.__data_queue.put(array)

    def recognize(self, voice_required_try=None, noise_detect_len=None):
        del voice_required_try, noise_detect_len #for compatibility with another voice recognition parameters

        try:
            with sd.RawInputStream(samplerate=self.__samplerate, blocksize=self.BLOCK_SIZE, device=self.__device_index, dtype='int16',
                                channels=1, callback=self.status_callback):
                rec = vosk.KaldiRecognizer(self.__model, self.__samplerate)
                while not self.is_force_stop():
                    data = self.__data_queue.get()

                    reduced_noise = nr.reduce_noise(y=data, sr=self.__samplerate)
                    #stt_vosk.normalize(memoryview(reduced_noise))

                    if rec.AcceptWaveform(bytes(reduced_noise)):
                        text=json.loads(rec.Result())['text']
                        if text :
                            return text
                    else:
                        # print(rec.PartialResult())
                        # partial result not analyzing now
                        pass
        except Exception:
            self._logger.exception("vosk exception:")




