from time import sleep
from threading import Thread
from babel.dates import format_date, format_datetime, format_time
from datetime import date, datetime, time, timedelta

from RootSkill import RootSkill
import app_logger
import utils.common

hour_names=['час','два','три','четыре','пять', 'шесть','семь','восемь','девять','десять','одинадцать','двенадцать','тринадцать',
            'четырнадцать','пятнадцать',
            'шестнадцать','семнадцать','восемьнадцать','девятнадцать','двадцать','двадцать один','двадцать два','двадцать три','двадцать четыре']

minutes_names=['одну','две','три','четыре','пять','шесть','семь','восемь','девять','десять','одинадцать','двенадцать','тринадцать',
               'четырнадцать','пятнадцать',
               'шестнадцать','семнадцать','восемьнадцать','девятнадцать','двадцать','двадцать одну','двадцать две','двадцать три','двадцать четыре',
               'двадцать пять','двадцать шесть','двадцать семь','двадцать восемь','двадцать девять','тридцать','тридцать одну','тридцать две',
               'тридцать три','тридцать четыре','тридцать пять','тридцать шесть','тридцать семь', 'тридцать восемь','тридцать девять','сорок',
               'сорок одну','сорок две','сорок три','сорок четыре','сорок пять','сорок шесть','сорок семь','сорок восемь','сорок девять','пятьдесят',
               'пятьдесят одну','пятьдесят две','пятьдесят три','пятьдесят четыре','пятьдесят пять','пятьдесят шесть','пятьдесят семь','пятьдесят восемь',
               'пятьдесят девять']

minutes_names_timer=['одна','две','три','четыре','пять','шесть','семь','восемь','девять','десять','одинадцать','двенадцать','тринадцать',
               'четырнадцать','пятнадцать',
               'шестнадцать','семнадцать','восемьнадцать','девятнадцать','двадцать','двадцать одна','двадцать две','двадцать три','двадцать четыре',
               'двадцать пять','двадцать шесть','двадцать семь','двадцать восемь','двадцать девять','тридцать','тридцать одна','тридцать две',
               'тридцать три','тридцать четыре','тридцать пять','тридцать шесть','тридцать семь', 'тридцать восемь','тридцать девять','сорок',
               'сорок одна','сорок две','сорок три','сорок четыре','сорок пять','сорок шесть','сорок семь','сорок восемь','сорок девять','пятьдесят',
               'пятьдесят одна','пятьдесят две','пятьдесят три','пятьдесят четыре','пятьдесят пять','пятьдесят шесть','пятьдесят семь','пятьдесят восемь',
               'пятьдесят девять']

#get hour, minute and remained phrase from splitted phrase
#from voice recognition phrase
def get_time(split_data):
    measure_hour=""
    measure_min=""
    act_hour=0
    act_minute=0

    if len(split_data)>=2:
        value = split_data[0]
        measure_hour = split_data[1]


    if measure_hour == "часов" or measure_hour == "час" or measure_hour == "часа":
        del split_data[0:2]
        for i in range(len(hour_names)):
            if value.startswith(hour_names[i]):
                act_hour=i+1
                break

    if len(split_data)>=2:
        value = split_data[0]
        measure_min = split_data[1]

    if measure_min == "минут" or measure_min == "минуту" or measure_min == "минуты" or measure_min == "минута":
        del split_data[0:2]
        for i in range(len(minutes_names)):
            if value.startswith(minutes_names[i]) or value.startswith(minutes_names_timer[i]):
                act_minute=i+1
                break

    act_action=''.join(split_data)
    return act_hour, act_minute, act_action, measure_hour, measure_min


class Notify(RootSkill):
    wakeup_list = []
    remainder_list = []
    thread_notify = None

    def get_desc(self):
        return "напоминания, таймер"

    def __init__(self):
        super().__init__(self.__class__.__name__)
        self.thread_notify = Thread(target=self.notify_thread)
        self.thread_notify.kill_received = False
        self.thread_notify.start()

    def deinit(self):
        if self.thread_notify:
            self.thread_notify.kill_received = True
            self.thread_notify.join()
            self.thread_notify = None

    def process(self, command:str)->bool:
        # wake up
        if command.startswith("разбуди завтра в "):
            split_data=command.split()
            del split_data[0:3]
            up_hour, up_minute, up_action=get_time(split_data)

            next_date = datetime.now() + timedelta(days=1)
            next_date = next_date.replace(hour=up_hour, minutes=up_minute)
            self.wakeup_list.append(next_date)
            self.say(f"Хорошо, разбужу в {up_hour}")

        elif command.startswith("напомни через ") or command.startswith("напомню через ") or command.startswith("напомнить через ") or command.startswith("таймер "):


            if command.startswith("таймер "):
                command=f"{command} таймер дзынь дзынь дзынь"
                split_data=command.split()
                del split_data[0:1]
            else:
                split_data=command.split()
                del split_data[0:2]

            rem_hour, rem_minute, rem_action, measure_hour, measure_minute=get_time(split_data)

            next_date = datetime.now() + timedelta(hours=rem_hour,minutes=rem_minute)
            self.remainder_list.append((next_date, rem_action))

            phrase = "Хорошо, напомню через "
            if rem_hour>0:
                phrase+=f" {rem_hour} {measure_hour} "
            if rem_minute>0:
                phrase+=f" {rem_minute} {measure_minute} "

            dt = format_datetime(
                    next_date, "HH:mm", locale='ru')

            phrase+=f" в {dt} "
            phrase+=rem_action
            self.say(phrase)
        else:
            return False
        return True

    def notify_thread(self):
        while not self.thread_notify.kill_received:
            try:
                self.notify_check()
                sleep(1)
            except Exception:
                app_logger.exception("Notify thread exception:")
        app_logger.warn("notify thread exited")

    #notifications check
    def notify_check(self):
        try:
            # check alarm in cycle )
            for wakeup_date in self.wakeup_list:
                now = datetime.now()
                if now >= wakeup_date:
                    dt = format_datetime(
                        datetime.now(), "dd MMMM HH:mm", locale='ru')
                    self.say("пора вставать, солнце встало :) ")
                    self.say("Сейчас : "+dt)
                    self.say(utils.common.get_weather_desc())
                    self.wakeup_list.remove(wakeup_date)

            # check alarm in cycle )
            for reminder in self.remainder_list:
                now = datetime.now()
                if now >= reminder[0]:
                    dt = format_datetime(
                        datetime.now(), "dd MMMM HH:mm", locale='ru')
                    self.say("Напоминание : "+dt)
                    self.say(reminder[1])
                    self.send_telegram_warning(reminder[1])
                    self.remainder_list.remove(reminder)
        except Exception:
            app_logger.exception("notify_check:")
