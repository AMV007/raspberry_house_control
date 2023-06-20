
import os
import sounddevice as sd
import alsaaudio as audio
from utils_common import minmax

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide" #for hide pygame import message
os.environ['SDL_AUDIODRIVER'] = "alsa" #for use ALSA in pygame, by default Jabra not visible

import pygame
import pygame._sdl2 as sdl2

from utils_sound import play_audio_file

jabra_device_name_pygame = ""
jabra_device_name = ""
jabra_device_id = ""
jabra_out_mixer = ""

def get_jabra_device_name_pygame():
    pygame.mixer.init()
    names=sdl2.audio.get_audio_device_names(False)
    pygame.mixer.quit()
    for name in names:
        if name.startswith("Jabra"):
            return name
    return None

def get_jabra_device_sd():
    devices = sd.query_devices()
    for i, device in enumerate(devices):
        if device['name'].startswith("Jabra"):
            return i, device['name']
    return -1, None

def get_jabra_out_mixer():
    scan_cards = audio.cards()
    cardindex=0
    for card in scan_cards:
        if card == "USB":
            scan_mixers = audio.mixers(scan_cards.index(card))
            for mixer in scan_mixers:
                if mixer == "PCM":
                    return audio.Mixer(mixer, cardindex=cardindex)
        cardindex+=1

def init(logger):
    global jabra_device_name_pygame
    global jabra_device_name
    global jabra_device_id
    global jabra_out_mixer

    jabra_device_name_pygame = get_jabra_device_name_pygame()
    jabra_device_id, jabra_device_name = get_jabra_device_sd()
    jabra_out_mixer=get_jabra_out_mixer()

    logger.info(f"sd jabra audio device id: {jabra_device_id}, name: {jabra_device_name}, ")
    logger.info(f"pygame jabra audio device:{jabra_device_name_pygame}")

def deinit():
    """ for now not using """
    pass

def beep(duration_s=3):  # duration in floating point !
    freq = 600  # Hz
    audio_file="/dev/shm/beep.wav"
    os.system(f"ffmpeg -y -loglevel error -f lavfi -i \"sine=frequency={freq}:duration={duration_s}\" {audio_file}")
    play_audio_file(audio_file, jabra_device_name_pygame)

def get_master_volume():
    return int(jabra_out_mixer.getvolume()[0])

def set_master_volume(change_volume:int):
    new_volume = minmax(get_master_volume()+change_volume,0,100)
    jabra_out_mixer.setvolume(new_volume)
