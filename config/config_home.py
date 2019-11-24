# -*- coding: utf-8 -*-

############## HARDWARE CONFIG GPIO
GPIO_GET_TEMP_HUMID         = 4     # pin to get temperature and humidity values
# pin for enable power temperature and humidity, not not using it ???
GPIO_ENABLE_POWER_TEMP_HUM  = 6
GPIO_WATER_DROP_SENSOR      = 12    # pin for water rain drop detect sensor
GPIO_LIGHT_DETECT           = 17    # pin for light detect sensor
GPIO_RUN_PUMP               = 18    # pin for run water pump
GPIO_MOISTURE               = 22    # pin for detect mosture
GPIO_OUT_LEVEL              = 23    # pin for water level check - out 5V
GPIO_IN_LEVEL               = 24    # pin for water level check - in
GPIO_RUN_FAN                = 25    # pin for enable room fan
# pin for enable power temperature and humidity, not not using it ???
GPIO_SWITCH_CO2_PARTICLES   = 27    # low CO2, HIGH - particles
# pin for enable power temperature and humidity, not not using it ???
GPIO_SLEEP_PARTICLES        = 13
GPIO_OUTLET_ENABLE          = 26    # enable-disable outlet

############## CONSTANTS
TEMP_DHT_VER = 22  # version of temperature chip DHT22
DEF_CHECK_TEMP = 23                 # minimum temperature, when switch on fans
TEMP_LOW_WARNING = 13               # warning about low temperature
TEMP_HIGH_WARNING = 30              # warning about high temperature

# time for watering process, seconds, minimum 5s - to measure water level
DEF_TIME_WATER_S = 20
DEF_TIME_WAIT_DAYS = 3    # delay time between waterings, days

START_CHECK_TIME = 8  # time for all noisy actions
STOP_CHECK_TIME = 21  # end time for noisy actions

############### DELAYS
SENSOR_POLL_PERIOD_S = 60*5  # period for sensor poll and write data to database
SENSOR_PARTICLES_POLL_PERIOD_S = 30*60 # period for sensor poll and write data to database
CHECK_PERIOD_S = 1 #period for controllers check loop
FAN_ON_OFF_DELAY_PERIOD_S = 5*60  #minimum time for fans for on off so they will be not such noisy


#   MESSAGES
place = "Дом"
warning_message_water = "Внимание !, закончилась вода для полива цветов в "+place+" !"
warning_message_temperature = "Внимание !, недопустимая температура в "+place+" !"
warning_message_co2 = "Внимание !, высокий уровень углекислого газа в "+place+" !"
warning_message_particles = "Внимание !,  высокая концентрация частиц в "+place+" !"

########### SENSITIVE INFORMATION

#   email
smtp_server = 'smtp.mail.ru'
smtp_user = "xxx@mail.ru"
smtp_pass = "xxx"
email_sender = 'xxx@mail.ru'
email_destination = ['xxx@gmail.com']

#   telegram
my_telegram_id = xxx
tokenBot = 'xxx:xxx'
botProxySocksProxy="socks5h://sproxy:xxx@xxx:1234"

# STT
google_key="xxxx"

WOL_PC_MAC=['11:11:11:11:11:11']

pyowm_key="xxx"