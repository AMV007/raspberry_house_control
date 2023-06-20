import os
import sys
import serial
import threading
from time import sleep

import config
from Singleton import Singleton


class DataBus(metaclass=Singleton):
    __lock = None

    __temperature=None
    __humidity=None
    __particles=None
    __CO2=None
    __light=None
    __moisture=None
    __water_level=None

    def __init__(self):
        self.__lock = threading.Lock()

    def __getTemp(self):
        with self.__lock:
            return self.__temperature

    def __setTemp(self, data):
        with self.__lock:
            self.__temperature=data

    def __getHum(self):
        with self.__lock:
            return self.__humidity

    def __setHum(self, data):
         with self.__lock:
            self.__humidity=data

    def __getParticles(self):
        with self.__lock:
            return self.__particles

    def __setParticles(self, data):
        with self.__lock:
            self.__particles=data

    def __getCO2(self):
        with self.__lock:
            return self.__CO2

    def __setCO2(self, data):
        with self.__lock:
            self.__CO2=data

    def __getLight(self):
        with self.__lock:
            return self.__light

    def __setLight(self, data:bool):
        with self.__lock:
            self.__light=data

    def __getMoisture(self):
        with self.__lock:
            return self.__moisture

    def __setMoisture(self, data):
        with self.__lock:
            self.__moisture=data

    def __getWaterLevel(self):
        with self.__lock:
            return self.__water_level

    def __setWaterLevel(self, data):
        with self.__lock:
            self.__water_level=data

    temperature =   property(__getTemp, __setTemp, None)
    humidity =      property(__getHum, __setHum, None)
    particles =     property(__getParticles, __setParticles, None)
    CO2 =           property(__getCO2, __setCO2, None)
    light =         property(__getLight, __setLight, None)
    moisture =      property(__getMoisture, __setMoisture, None)
    waterLevel =    property(__getWaterLevel, __setWaterLevel, None)

