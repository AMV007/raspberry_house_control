#for weather
import pyowm
from pyowm.utils.config import get_default_config

from RootSkill import RootSkill

def get_weather_desc():
    config_dict = get_default_config()
    config_dict['language'] = 'ru'

    owm = pyowm.OWM(api_key=config.pyowm_key, config=config_dict)
    mgr = owm.weather_manager()
    observation = mgr.weather_at_place('Moscow, ru')
    w = observation.weather
    min_temp = w.temperature('celsius')['temp_min']
    wind = w.wind()['speed']
    hum = w.humidity
    rain = w.rain
    snow = w.snow
    text = "временами {} с минимальной температурой {} °C ".format(
        w.detailed_status, int(min_temp))
    if int(hum) > 50 and min_temp < 15:
        text += f", высокая влажность,{hum}%, одевайся потеплее"
    if int(wind) > 5:
        text += f", сильный ветер, {wind} м/с, смотри чтобы тебя не продуло"
    if rain:
        text += f", не забудь взять зонт, возможен дождь в течении :{rain}"
    if snow:
        text += f", возможно будет снег в течении : {snow}, играем в снежки ? "
    return text

class Weather(RootSkill):

    def get_desc(self):
        return "говорить о погоде"

    def __init__(self):
        super().__init__(self.__class__.__name__)

    def process(self, command:str)->bool:
        if command in ["погода", "прогноз погоды", "что на улице", "что с погодой"]:
            self.say(get_weather_desc())
        else:
            return False
        return True
