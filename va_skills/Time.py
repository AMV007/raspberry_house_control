from datetime import date, datetime, time, timedelta
from babel.dates import format_date, format_datetime, format_time

from RootSkill import RootSkill

class Time(RootSkill):

    def get_desc(self):
        return "подсказывать время"

    def __init__(self):
        super().__init__(self.__class__.__name__)

    def process(self, command:str)->bool:
        if command in ["время", "сколько время", "сколько времени"]:
            self.say('{0:%H:%M}'.format(datetime.now()))
        elif command in ["дата", "какой день", "какой сегодня день"]:
            dt = format_datetime(datetime.now(), "dd MMMM HH:mm", locale='ru')
            self.say("Сейчас : "+dt)
        else:
            return False
        return True
