import os, sys
import RPi.GPIO as GPIO

from wakeonlan import send_magic_packet
from datetime import datetime, time as datetime_time, timedelta, date as datetime_date

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from telebot import types
import numpy as np

#my import
from Bot import Bot
import config
import devices
import sensors
import controls
import app_logger
import database

#  ------------------------------------------------------------ GLOBAL
pathname = os.path.dirname(sys.argv[0])
work_dir=os.path.abspath(pathname)

#   ------------------------------------------------------------ HELPERS
def make_co2_graph():
    start_date = datetime.now() - timedelta(days=1)
    end_date = datetime.now()
    rows = database.get_co2(start_date, end_date)

    labels = []
    values = []
    for row in rows:
        date = row[1]
        value = row[2]
        if value == None:
            value = 0
        date_str = date.strftime('%H')
        if date_str in labels:
            continue
        labels.append(date_str)
        values.append(value)

    fig = plt.figure()
    ax = plt.subplot(111)
    ax.plot(labels, values, label='CO2, ppm')
    ax.set_xlabel('time (h)')
    plt.title('CO2 day chart')
    plt.grid(True)
    ax.legend()
    # plt.show()

    fig.savefig('/dev/shm/plot.png')

def make_temp_hum_graph():
    start_date = datetime.now() - timedelta(days=1)
    end_date = datetime.now()
    rows = database.get_temp_humid(start_date, end_date)

    labels = []
    values_temp = []
    values_hum = []
    for row in rows:
        date = row[1]
        date_str = date.strftime('%H')
        if date_str in labels:
            continue
        labels.append(date_str)
        temp = row[2]
        hum = row[3]
        values_temp.append(temp)
        values_hum.append(hum)

    fig = plt.figure()
    ax = plt.subplot(111)
    ax.plot(labels, values_temp, label='Temperature, °C')
    ax.plot(labels, values_hum, label='Humidity, %')
    ax.set_xlabel('time (h)')
    plt.title('Temperature and humidity day chart')
    plt.grid(True)
    ax.legend()
    # plt.show()

    fig.savefig('/dev/shm/plot.png')

def make_particles_graph():
    start_date = datetime.now() - timedelta(days=1)
    end_date = datetime.now()
    rows = database.get_particles(start_date, end_date)

    labels = []
    values_PM1 = []
    values_PM25 = []
    values_PM10 = []
    for row in rows:
        date = row[1]
        date_str = date.strftime('%H')
        if date_str in labels:
            continue
        labels.append(date_str)
        values_PM1.append(row[2])
        values_PM25.append(row[3])
        values_PM10.append(row[4])

    fig = plt.figure()
    ax = plt.subplot(111)
    ax.plot(labels, values_PM1, label='PM1, μg/m³')
    ax.plot(labels, values_PM25, label='PM2.5, μg/m³')
    ax.plot(labels, values_PM10, label='PM10, μg/m³')
    ax.set_xlabel('time (h)')
    plt.title('Particles day chart')
    plt.grid(True)
    ax.legend()
    # plt.show()

    fig.savefig('/dev/shm/plot.png')

#   ------------------------------------------------------------ TELEGRAM BOT HANDLERS

def get_markup():
    reply_markup = types.InlineKeyboardMarkup(row_width=2)
    reply_markup.add(
        types.InlineKeyboardButton("Get status",
                                    callback_data="get_status"),
        types.InlineKeyboardButton("Measure water level",
                                    callback_data="measure_water"),
        types.InlineKeyboardButton("Water plants now!",
                                    callback_data="do_watering_now"),
        types.InlineKeyboardButton("Fans in auto mode",
                                    callback_data="auto_fan"),
        types.InlineKeyboardButton("Manually run/Stop fan",
                                    callback_data="manual_run_stop_fan"),
        types.InlineKeyboardButton("On/Off outlet",
                                    callback_data="on_off_outlet"),
        types.InlineKeyboardButton("On/Off conditioner",
                                    callback_data="on_off_conditioner"),
        types.InlineKeyboardButton("Outlet in auto mode",
                                    callback_data="auto_outlet"),
        types.InlineKeyboardButton("Camera photo",
                                    callback_data="make_camera_photo"),
        types.InlineKeyboardButton("Day CO2 graph",
                                    callback_data="make_co2_graph"),
        types.InlineKeyboardButton("Day temp/humidity graph",
                                    callback_data="make_temp_hum_graph"),
        types.InlineKeyboardButton("Day particles graph",
                                    callback_data="make_particles_graph"),
        types.InlineKeyboardButton("Last 10 watering dates",
                                    callback_data="get_last_10_watering_dates"),
        types.InlineKeyboardButton("Calibrate CO2",
                                    callback_data="calibrate_co2"),
        types.InlineKeyboardButton("Wake my pc's",
                                    callback_data="wake_my_pc"),
    )

    return reply_markup

class BotImpl(Bot):
    watering_control = None
    _commands = {  # command description used in the "help" command
        'start'       : 'Get used to the bot',
        'help'        : 'Gives you information about the available commands',
    }

    def command_help(self,message):
        try:
            if message.text == "/help":
                self.send_msg_bot_long_check(str(config.my_telegram_id), "enter '/start' for commands list:")
            elif message.text == "/start":
                message_id=self.send_msg_bot_long_check(str(config.my_telegram_id),
                                "Choose:", reply_markup=get_markup())
            else:
                self.send_msg_bot_long_check("what are you meaning and how you are here ?")
        except Exception:
             self.handle_exception_with_msg(message.chat.id,"error","main exception:")

    def __init__(self):
        if not hasattr(config, "botToken"): return

        super().__init__(config.botToken, app_logger.logger)
        bot = self._bot

        self.watering_control=controls.get(controls.control_Watering)

        @bot.callback_query_handler(func=lambda call: True)
        def callback_inline(call):
            try:
                if call.message:
                    if call.data == "measure_water":
                        self.watering_control.do_watering("measure_water", 5, False)
                        self.send_msg_bot_long_check(
                            call.message.chat.id, watering_control.get_status_str()+"\n")
                    elif call.data == "do_watering_now":
                        self.watering_control.do_watering("force from telegram")
                        self.send_msg_bot_long_check(call.message.chat.id, "Watering done !")
                    elif call.data == "get_status":
                        self.send_msg_bot_long_check(call.message.chat.id,
                                        controls.get_status_str()+sensors.get_status_str())
                    elif call.data == "manual_run_stop_fan":
                        controls.get(controls.control_TempHum).switch(external_command=True)
                        self.send_msg_bot_long_check(call.message.chat.id,
                                        controls.get(controls.control_TempHum).get_status_str())
                    elif call.data == "auto_fan":
                        controls.get(controls.control_TempHum).set_auto()
                        self.send_msg_bot_long_check(call.message.chat.id, "Fans auto !")
                    elif call.data == "on_off_outlet":
                        controls.get(controls.control_Outlet).switch(external_command=True)
                        self.send_msg_bot_long_check(call.message.chat.id,
                                        devices.get(devices.Outlet)[0].get_status_str())
                    elif call.data == "on_off_conditioner":
                        controls.get(controls.control_ConditionerControl_IR).switch(external_command=True)
                        self.send_msg_bot_long_check(call.message.chat.id,
                                        devices.get(devices.IrConditioner)[0].get_status_str())
                    elif call.data == "auto_outlet":
                        controls.get(controls.control_Outlet).set_auto()
                        self.send_msg_bot_long_check(call.message.chat.id, "Outlet auto !")
                    elif call.data == "wake_my_pc":
                        if hasattr(config, "WOL_PC_MAC"):
                            for pc_mac in config.WOL_PC_MAC:
                                send_magic_packet(pc_mac)
                            self.send_msg_bot_long_check(call.message.chat.id, "Command sended !")
                        else:
                            self.send_msg_bot_long_check(call.message.chat.id, "no MAC addresses provided in config !")
                    elif call.data == "check_light":
                        self.send_msg_bot_long_check(call.message.chat.id, sensors.get(sensors.Light)[0].get_status_str())
                    elif call.data == "make_camera_photo":
                        devices.get(devices.Camera)[0].do_photo()
                        photo = open('/dev/shm/camera.jpg', 'rb')
                        bot.send_photo(call.message.chat.id, photo)
                    elif call.data == "make_co2_graph":
                        make_co2_graph()
                        photo = open('/dev/shm/plot.png', 'rb')
                        bot.send_photo(call.message.chat.id, photo)
                    elif call.data == "make_temp_hum_graph":
                        make_temp_hum_graph()
                        photo = open('/dev/shm/plot.png', 'rb')
                        bot.send_photo(call.message.chat.id, photo)
                    elif call.data == "make_particles_graph":
                        make_particles_graph()
                        photo = open('/dev/shm/plot.png', 'rb')
                        bot.send_photo(call.message.chat.id, photo)
                    elif call.data == "get_last_10_watering_dates":
                        values = database.get_last_10_watering_info()
                        self.send_msg_bot_long_check(call.message.chat.id, values)
                    elif call.data == "calibrate_co2":
                        sensors.CO2.zero_calibrate()
                        self.send_msg_bot_long_check(call.message.chat.id, "done")
                    else:
                        self.send_msg_bot_long_check(
                            str(config.my_telegram_id), "unknown call data: "+call.data, get_markup())
                        app_logger.error("unknown call.data " + call.data)
                elif call.inline_message_id:
                    if call.data == "test":
                        bot.edit_message_text(
                            inline_message_id=call.inline_message_id, text="forbidden !!!")
            except Exception as e:
                self.handle_exception_with_msg(call.message.chat.id,"error", f"callback_inline:"+str(e))
            finally:
                filenames = ["/dev/shm/plot.png", "/dev/shm/camera.jpg"]
                for filename in filenames:
                    if os.path.exists(filename):
                        os.remove(filename)

        # @bot.message_handler(commands=['water_status'])
        # def handle_water_status(message):
        #    check_water_status_and_send_responce()

        # @bot.message_handler(commands=['measure_water'])
        # def handle_measure_water(message):
        #    watering_control.do_watering(5)
        #    check_water_status_and_send_responce()

        # @bot.message_handler(commands=['do_watering_now'])
        # def handle_do_watering_now(message):
        #    watering_control.do_watering()


        @bot.message_handler(content_types=["text"])
        def repeat_all_messages(message):
            self.send_msg_bot_long_check(message.chat.id, "sorry, I not understand you ?",reply_markup=types.ReplyKeyboardRemove())

            try:
                user = message.from_user
                if user.id != config.my_telegram_id:
                    self.send_msg_bot_long_check(str(config.my_telegram_id),
                                    user.username+"\n"+message.text)
                with open(work_dir+"/log/messages.txt", "a") as myfile:
                    myfile.write("user: " + str(user)+"\nMessage: " +
                                str(message.text.encode('utf8'))+",  "+str(datetime.now())+"\n")
            except Exception:
                self.handle_exception_with_msg(message.chat.id,"error")
