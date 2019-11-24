#!/usr/bin/env python3
# Requires PyAudio and PySpeech.
# Speech To Text

import sys,os
import io
from threading import Thread
from ctypes import *
from datetime import date, datetime, time, timedelta
from babel.dates import format_date, format_datetime, format_time
from time import sleep

import speech_recognition as sr

import my_logging
import utils.common
import sound
import TTS

import config
import devices
import sensors
import controls
import STT_psphinx

pathname = os.path.dirname(sys.argv[0])
work_dir=os.path.abspath(pathname)

jabra_microphone_id=0
thread = None
Running = None
wakeup_list = []

#for google licensing
UseKey = True
UseKeyDay = datetime.now().day
recognizer = None

keywords = ["computer","pi","forward","железка","пи","компьютер"]

def print_all_microphones():
    mic_list = sr.Microphone.list_microphone_names()
    for i, microphone_name in enumerate(mic_list):
        print("microphone {i} : {microphone_name}".format(i=i, microphone_name=microphone_name))

def get_jabra_microphone_id():
    mic_list = sr.Microphone.list_microphone_names()
    for i, microphone_name in enumerate(mic_list):
        if microphone_name.startswith("Jabra"):
            return i
    return -1

def init(use_thread=False):
    global thread
    global Running
    global jabra_microphone_id

    Running = True

    #print_all_microphones()
    jabra_microphone_id=get_jabra_microphone_id()
    my_logging.logger.info(f"jabra microphone id: {jabra_microphone_id}")

    STT_psphinx.init(keywords, jabra_microphone_id)
    if use_thread:
        thread = Thread(target=listen_thread, args=(10, ))
        thread.start()


def deinit():
    global thread
    global Running
    Running = False

    STT_psphinx.stop_wait()
    print("start stoping "+os.path.basename(__file__))
    if thread != None:
        thread.join()
    print(__file__+" stopped")



def say_ok(command):
    if not TTS.say("Выполняю : "+command):
        sound.play_command("execute")

def listen_thread(arg):
    # just thread started and ready for commands
    sound.beep(0.05)
    while Running:
        listen_cycle()

def listen_cycle():

    # check alarm in cycle )
    for wakeup_date in wakeup_list and Running:
        now = datetime.now()
        if now > wakeup_date:
            dt = format_datetime(
                datetime.now(), "dd MMMM HH:mm", locale='ru')
            TTS.say("дорог'ой, ты просил разбудить, солнце встало :) ")
            TTS.say("Сейчас : "+dt)
            TTS.say(utils.common.get_weather_desc())
            wakeup_list.remove(wakeup_date)

    try:
        #STT_psphinx.wait_for_keyword() - not stable working, reacting on noise
        command = wait_keyword_recognize()

        if not command:
            command = listen_phrase()

        exec_command(command)

    except Exception as e:
        my_logging.logger.exception("voice recognition exception:")
        sleep(10)

#this one working not good with online keyword recognition, because online service don't like multiple requests
def wait_keyword_recognize():

    while Running:
        phrase = recognize()

        if len(phrase.split()) < 1:
            continue

        if len(phrase.split()) == 1:
            # just only keyword
            key = phrase.split()[0]
            if key in keywords:
                return None
        else:
            # normal command
            command=None
            (key_detect_start, phrase_start) = phrase.split(maxsplit=1)
            (phrase_end, key_detect_end) = phrase.split(maxsplit=1)

            if key_detect_start in keywords:
                command = phrase_start
            elif key_detect_end in keywords:
                command = phrase_end

            if not command :
                continue

            return command

    return None

# Speech recognition using Google Speech Recognition
def recognize(voice_required_try=None, noise_detect_len=None):
    global UseKey
    global UseKeyDay
    global Running
    global recognizer

    # Record Audio
    if recognizer == None:
        recognizer = sr.Recognizer()

    phrase = ""

    speechListenedAndRecognized = False
    while not speechListenedAndRecognized and Running:
        try:
            # for minimize lag between input and start listening - specifying microphone device by number
            with sr.Microphone(device_index=jabra_microphone_id) as source:
                if noise_detect_len != None:
                    # recognizer.adjust_for_ambient_noise(source, duration=noise_detect_len) # to remove noise environment
                    pass

                #print("Say something!")
                if(voice_required_try != None):
                    sound.beep(0.05, True)
                audio = recognizer.listen(source, timeout=5)

            # for testing purposes, we're just using the default API key
            # to use another API key, use `r.recognize_google(audio, key="GOOGLE_SPEECH_RECOGNITION_API_KEY")`
            # key="xxx"
            # instead of `r.recognize_google(audio)`

            #print("start recognize")

            speechRecognized = False
            while not speechRecognized and Running:
                # because google service can not approve my key due to limit of requests
                try:
                    if UseKey:
                        # if using my key, recognition working faster
                        key = config.google_key
                        phrase = recognizer.recognize_google(
                            audio, language="ru-RU", key=key)
                        speechRecognized = True
                    else:
                        phrase = recognizer.recognize_google(
                            audio, language="ru-RU")
                        if UseKeyDay != datetime.now().day:
                            UseKey = True  # day changed, trying 50 call limitations on next day
                        speechRecognized = True
                except sr.RequestError as e:
                    print(
                        "Could not request results from Google Speech Recognition service; {0}".format(e))
                    UseKey = False
                    UseKeyDay = datetime.now().day

            speechListenedAndRecognized = True
        except sr.WaitTimeoutError:
            pass
        except sr.UnknownValueError:
            # error recognize, looking like empty request lets try again
            #print("Google Speech Recognition could not understand audio")
            if voice_required_try != None:
                voice_required_try -= 1
                if voice_required_try == 0:
                    return None
                TTS.say("Не понятно, повтори ?")
            pass

    phrase = phrase.lower()

    print("You said: " + phrase+",  "+str(datetime.now()))
    with open(work_dir+"/log/speech.txt", "a") as myfile:
            myfile.write(phrase+",  "+str(datetime.now())+"\n")
    return phrase


def listen_phrase():
    TTS.say("Слушаю")
    command = recognize(3, 0.5)
    if command == None:
        TTS.say("Ни шанса понять, давай все заново")
    return command


def exec_command(command):
    my_logging.logger.info("command:"+command)

    # devices control
    if command in ["вентилятор", "включи вентилятор", "включить вентилятор",  "выключи вентилятор", "выключить вентилятор"]:
        say_ok(command)
        controls.get(controls.control_TempHum).switch(external_command=True)
    elif command in ["вентилятор авто"]:
        say_ok(command)
        controls.get(controls.control_TempHum).set_auto()
    elif command in ["розетка", "включи розетку", "включить розетку",  "выключи розетку", "выключить розетку"]:
        say_ok(command)
        controls.get(controls.control_Outlet).switch(external_command=True)
    elif command in ["розетка авто"]:
        say_ok(command)
        controls.get(controls.control_Outlet).set_auto()
    elif command in ["кондиционер","включи кондиционер","выключи кондиционер","жарко"]:
        say_ok(command)
        controls.get(controls.control_ConditionerControl_IR).switch(external_command=True)
    elif command in ["кондиционер авто"]:
        say_ok(command)
        controls.get(controls.control_ConditionerControl_IR).set_auto()
    elif command in ["включи все"]:
        say_ok(command)
        controls.enable()
    elif command in ["выключи все"]:
        say_ok(command)
        controls.disable()
    elif command in ["все авто"]:
        say_ok(command)
        controls.set_auto()


    # noise control
    elif command in ["тихо"]:
        say_ok(command)
        controls.get(controls.control_NoisyActions).force_silent = True
    elif command in ["говори"]:
        say_ok(command)
        controls.get(controls.control_NoisyActions).force_silent = False

     #temperature and humidity and co2
    elif command in ["температура", "какая температура", "температура в комнате"]:
        temperature, humidity, num_cycles_wrong = sensors.get(sensors.TempHum)[0].read_val()
        temp_str = "{:.1f}".format(temperature).replace('.', ',')
        TTS.say("Температура в комнате: "+temp_str+" градусов")
        if temperature < 22:
            TTS.say("прохладно, оденься потеплее")
    elif command in ["влажность", "какая влажность", "влажность в комнате"]:
        temperature, humidity, num_cycles_wrong = sensors.get(sensors.TempHum)[0].read_val()
        hum_str = "{:.1f}".format(humidity).replace('.', ',')
        TTS.say("Влажность в комнате: "+str(hum_str)+" %")
        if humidity < 35:
            TTS.say("суховато, можно увлажнить")
    elif command in ["углекислый газ", "газ", "какой уровень углекислого газа"]:
        co2 = sensors.get(sensors.CO2)[0].read_val()
        TTS.say("Уровень углекислого газа в комнате: "+str(co2)+" ppm")
        if co2 > 800:
            TTS.say("можно открыть окно")
    elif command in ["частицы", "загрязнение"]:
        particles = sensors.get(sensors.Particles_pms7003)[0].read_val()
        pm25 = particles['data']['10']
        TTS.say("Частиц 2.5 в комнате: "+str(pm25[1])+"микрограмм на кубометр")
        if pm25[1] > 100:
            TTS.say("надевай маску, загрязнение высокое !")

    #time, weather,news
    elif command in ["время", "сколько время", "сколько времени"]:
        TTS.say('{0:%H:%M}'.format(datetime.now()))
    elif command in ["дата", "какой день", "какой сегодня день"]:
        dt = format_datetime(datetime.now(), "dd MMMM HH:mm", locale='ru')
        TTS.say("Сейчас : "+dt)
    elif command in ["погода", "прогноз погоды", "что на улице", "что с погодой"]:
        TTS.say(utils.common.get_weather_desc())
    elif command in ["новости", "что нового"]:
        count=1
        TTS.say("Новости от РосБизнесКонсалтинг:")
        for news in utils.common.get_news():
            TTS.say(f"Новость {count}: {news}")
            count+=1

    # misc, just for fun
    elif command in ["отзовись", "привет"]:
        sound.play_command("hello")
    elif command in ["спокойной ночи", "спокойной"]:
        TTS.say("Спокойной ночи дорог'ой")
    elif command in ["доброе утро", "доброе", "с добрым утром"]:
        TTS.say("С добрым утром дорог'ой")
    elif command in ["как дела", "как жизнь"]:
        TTS.say("Отлично, температура " +
            str(utils.common.get_cpu_temperature())+", у тебя как ?")
    elif command in ["как тебя зовут","твое имя", "кто ты"]:
        TTS.say("я автоматизировнный помощник по дому, пока не до конца доделанный")

    # wake up
    elif command in ["разбуди завтра в 7", "разбуди завтра в 7:00", "разбуди в 7:00"]:
        next = datetime.now() + timedelta(days=1)
        next = next.replace(hour=7)
        wakeup_list.append(next)
        TTS.say("Хорошо, разбужу в 7")
    elif command in ["разбуди завтра в 8", "разбуди завтра в 8:00", "разбуди в 8:00"]:
        next = datetime.now() + timedelta(days=1)
        next = next.replace(hour=8)
        wakeup_list.append(next)
        TTS.say("Хорошо, разбужу в 8")
    elif command in ["отмена", "отмена комманды"]:
        TTS.say("всего хорошего")

    #unknown, error
    else:
        if not TTS.say("непонятная комманда : "+command):
            sound.play_command("repeat")
        my_logging.logger.info("unknown command: "+command)

