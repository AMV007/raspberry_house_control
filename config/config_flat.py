# -*- coding: utf-8 -*-

# HARDWARE CONFIG GPIO
#GPIO_GET_TEMP_HUMID             = 4    # pin to get temperature and humidity values
# pin for enable power temperature and humidity, not not using it ???
#GPIO_ENABLE_POWER_TEMP_HUM      = 6
#GPIO_RUN_PUMP                   = 8          # pin for run water pump
GPIO_SWITCH_CO2_PARTICLES       = 9     # low CO2, HIGH - particles
#GPIO_WATER_DROP_SENSOR          = 12        # pin for water rain drop detect sensor
GPIO_LIGHT_DETECT               = 17        # pin for light detect sensor
GPIO_IR_WRITE                   = 18    # for write IR port, namely this GPIO, because supporting hardware PWM on it
#GPIO_MOISTURE                   = 22                 # pin for detect mosture
#GPIO_OUT_LEVEL                  = 23           # pin for water level check - out 5V
#GPIO_IN_LEVEL                   = 24               # pin for water level check - in
#GPIO_RUN_FAN                    = 25                 # pin for enable room fan
# pin for enable power temperature and humidity, not not using it ???
GPIO_IR_READ                    = 27    # gpio for infrared read
# pin for enable power temperature and humidity, not not using it ???
#GPIO_SLEEP_PARTICLES            = 13
#GPIO_OUTLET_ENABLE              = 26   # enable-disable outlet

# CONSTANTS
TEMP_DHT_VER = 22  # version of temperature chip
DEF_CHECK_TEMP = 22           # default temperature, after switch on fans
TEMP_LOW_WARNING = 13           # default temperature, after switch on fans
TEMP_HIGH_WARNING = 30           # default temperature, after switch on fans

# time for watering process, seconds, minimum 5s - to measure water level
DEF_TIME_WATER_S = 100
DEF_TIME_WAIT_DAYS = 3    # delay time between waterings, days

START_CHECK_TIME = 8  # time for all noisy actions
STOP_CHECK_TIME = 21  # end time for noisy actions

SENSOR_POLL_PERIOD_S = 60*5  # period for sensor poll and write data to database
# period for sensor poll and write data to database
SENSOR_PARTICLES_POLL_PERIOD_S = 60*60


#   MESSAGES
place = "Квартира"
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

pyowm_key="xxx"
