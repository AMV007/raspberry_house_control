import os
import subprocess
import sounddevice as sd
import soundfile as sf
import wave
import pyaudio
import threading

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide" #for hide pygame import message
import pygame

"""
common sount utils

    for get alsa devices: python3 -m sounddevice

"""

def convert_to_wav(filename:str, samplerate, wav_filename=None, noise_reduction=False, filter=None, normalize=True):
    """
    function to convert any format to wav with specified in class sample rate
    Parameters:
    samplerate - out samplerate
    filename - input filename
    filter - filtername from https://github.com/GregorR/rnnoise-models,
            for example : cb.rnnn, but this filter file must be in app folder
    normalize - normalize audio level or not
    """
    if not wav_filename:
        wav_filename=os.path.splitext(filename)[0]+".wav"

    parameters=['ffmpeg','-y', '-loglevel','error','-i', filename]
    if noise_reduction:
        #apply filter
        if filter:
            parameters.extend(['-af', f"arnndn=m={filter}"])
        else:
            parameters.extend(['-af', "afwtdn=adaptive=1"])

    parameters.extend(['-ar', f"{samplerate}"]) #change samplerate
    parameters.append(wav_filename)
    process = subprocess.run(parameters)
    if process.returncode != 0:
        raise ValueError("Something went wrong with ffmpeg")

    if normalize:
        process = subprocess.run(['normalize-audio', '-q', wav_filename])
        if process.returncode != 0:
            raise ValueError("Something went wrong with normalization")
    return wav_filename, samplerate

################# SD ######################
def play_wav(filename, device_id=None):
    if not os.path.isfile(filename):
        raise ValueError(f"file not found {filename}")
    data, fs = sf.read(filename)
    sd.play(data, fs, device=device_id, blocking=True)

def print_audio_devices_sd():
    devices = sd.query_devices()
    for i, device in enumerate(devices):
        print("device: {i} : {name}".format(i=i, name=device['name']))

def get_audio_device_sd_samplerate(device_id:int):
    devices = sd.query_devices()
    for i, device in enumerate(devices):
        if i == device_id:
            return int(device['default_samplerate'])

def get_audio_device_sd_samplerate_by_name(device_name:str):
    devices = sd.query_devices()
    for i, device in enumerate(devices):
        if device['name'] == device_name:
            return int(device['default_samplerate'])

################# pyaudio ##################
def play_wav_pyaudio(name, device_id=None):
    print(f"play name={name}, device_id={device_id}")
    # define stream chunk
    chunk = 32768

    # open a wav format music
    f = wave.open(name, "rb")

    p = pyaudio.PyAudio()
    # open stream
    stream = p.open(format=p.get_format_from_width(f.getsampwidth()),
                    channels=f.getnchannels(),
                    rate=f.getframerate(),
                    output=True, output_device_index=device_id)
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

############### pygame ################
#play file in any format
lock = threading.Lock() #pygame playing only one thread per time
def play_audio_file(filename, device_name=None, force_stop=[False]):

    if not os.path.isfile(filename):
            return

    with lock:
        try:
            pygame.mixer.init(devicename=device_name, buffer=2048) #for some reason got buffer underrun with default buffer

            #play
            pygame.mixer.music.load(filename)
            pygame.mixer.music.play()

            while pygame.mixer.music.get_busy() and not force_stop[0]:
                pygame.time.wait(100)  # 100 ms

        finally:
            pygame.mixer.quit()

