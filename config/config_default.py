# -*- coding: utf-8 -*-

from config.config_common import *

############## HARDWARE CONFIG GPIO
# GPIO_GET_TEMP_HUMID         = 27     # pin to get temperature and humidity values
# # pin for enable power temperature and humidity, not using it
# GPIO_ENABLE_POWER_TEMP_HUM  = 6 # it's fake - not using right now
# GPIO_WATER_DROP_SENSOR      = 12    # pin for water rain drop detect sensor
# GPIO_LIGHT_DETECT           = 17    # pin for light detect sensor
# GPIO_MOISTURE               = 22    # pin for detect mosture
# GPIO_RUN_PUMP               = 7    # pin for run water pump
# GPIO_OUTLET_ENABLE          = 8    # enable-disable outlet
# GPIO_RUN_FAN                = 25    # pin for enable room fan

# # pin for enable power temperature and humidity, not not using it ???
# GPIO_SWITCH_UART0                = 23    # low CO2, HIGH - particles
# GPIO_SWITCH_UART1                = 24    # low CO2, HIGH - particles
# # pin for enable power temperature and humidity, not not using it ???

# ############## CONSTANTS
# TEMP_DHT_VER = 22  # version of temperature chip DHT22

# # time for watering process, seconds, minimum 5s - to measure water level
# DEF_TIME_WATER_S = 23
# DEF_TIME_WAIT_DAYS = 3    # delay time between waterings, days

# NEXTION_DISPLAY_EXITS = True
############## CONSTANTS

# time for watering process, seconds, minimum 5s - to measure water level
DEF_TIME_WATER_S = 40
DEF_TIME_WAIT_DAYS = 3    # delay time between waterings, days

TTS_KEYWORD="железка"

##############   MESSAGES
place = "Неизвестное место"
warning_message_water = "Внимание !, закончилась вода для полива цветов в "+place+" !"
warning_message_temperature = "Внимание !, недопустимая температура в "+place+" !"
warning_message_co2 = "Внимание !, высокий уровень углекислого газа в "+place+" !"
warning_message_particles = "Внимание !,  высокая концентрация частиц в "+place+" !"

############## SENSITIVE INFORMATION
botToken = None
WOL_PC_MAC=[None]
