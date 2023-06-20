import bus

from RootSkill import RootSkill
import sensors

class Sensors(RootSkill):
    data_bus = None

    def get_desc(self):
        return "озвучивать сенсоры если они прописаны в конфиге"

    def __init__(self):
        super().__init__(self.__class__.__name__)
        self.data_bus=bus.DataBus.DataBus()

    def process(self, command:str)->bool:
        #temperature and humidity and co2
        if command in ["температура", "какая температура", "температура в комнате"]:
            temp_str = "{:.1f}".format(self.data_bus.temperature).replace('.', ',')
            self.say("Температура в комнате: "+temp_str+" градусов")
            if self.data_bus.temperature < 22:
                self.say("прохладно, оденься потеплее")
            if self.data_bus.temperature > 30:
                self.say("тебе не жарко, может открыть окно ?")

        elif command in ["влажность", "какая влажность", "влажность в комнате"]:
            hum_str = "{:.1f}".format(self.data_bus.humidity).replace('.', ',')
            self.say("Влажность в комнате: "+str(hum_str)+" %")
            if self.data_bus.humidity < 35:
                self.say("суховато, можно увлажнить")

        elif command in ["углекислый газ", "газ", "какой уровень углекислого газа"]:
            self.say("Уровень углекислого газа в комнате: "+str(self.data_bus.CO2)+" ppm")
            if self.data_bus.CO2 > 800:
                self.say("можно открыть окно")
            elif self.data_bus.CO2 > 1200:
                self.say("нужно срочно открыть окно")

        elif command in ["частицы", "загрязнение","уровень частиц","уровень загряднения"]:
            pm25 = self.data_bus.particles['data']['10']
            self.say("Частиц 2.5 в комнате: "+str(pm25[1])+"микрограмм на кубометр")
            if pm25[1] > 100:
                self.say("надевай маску, загрязнение высокое !")
        elif command in ["углекислый газ калибровка","калибровка узгекислого газа"]:
            sensors.CO2.zero_calibrate()
        else:
            return False
        return True
