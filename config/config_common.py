# -*- coding: utf-8 -*-

############## CONSTANTS
DEF_CHECK_TEMP = 24                 # minimum temperature, when switch on fans
TEMP_LOW_WARNING = 10               # warning about low temperature
TEMP_HIGH_WARNING = 40              # warning about high temperature

CO2_WARNING_VALUE = 1200 #warning messabe about open window will be displayed

START_CHECK_TIME = 8  # time for all noisy actions
STOP_CHECK_TIME = 21  # end time for noisy actions

NOTIFY_DEVICE_START = True

############## DELAYS
SENSOR_POLL_PERIOD_S = 60*5  # period for sensor poll and write data to database
SENSOR_PARTICLES_POLL_PERIOD_S = 30*60 # period for sensor poll and write data to database
CHECK_PERIOD_S = 1 #period for controllers check loop
FAN_ON_OFF_DELAY_PERIOD_S = 5*60  #minimum time for fans for on off so they will be not such noisy

############## STT
vosk_model_path_small = "vosk-model-small-ru-0.22"
vosk_model_path_big = "vosk-model-ru-0.42"

############## SENSITIVE INFORMATION

# email
smtp_server = 'xxx'
smtp_user = "xxx@xxx.ru"
smtp_pass = "xxx"
email_sender = 'xxx@xxx.ru'
email_destination = ['xxx@xxx.ru']

# telegram
my_telegram_id = xxx

# STT
google_key="xxx"

# TTS
yandex_key="xxx"

#openai. chatGpt
openai_api_key = "xxx"

#weather
pyowm_key="xxx"
