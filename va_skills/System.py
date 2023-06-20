import subprocess
from datetime import date, datetime, time, timedelta
from babel.dates import format_date, format_datetime, format_time

from RootSkill import RootSkill

class System(RootSkill):

    def get_desc(self):
        return "управлять системой"

    def __init__(self):
        super().__init__(self.__class__.__name__)

    def process(self, command:str)->bool:
        if command in ["перезагрузись","ребутнись"]:
            self.say("перезагружаюсь")
            subprocess.Popen("sudo reboot", shell=True)

        else:
            return False
        return True
