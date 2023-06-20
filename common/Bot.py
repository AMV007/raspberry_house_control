import os
import json
from ppretty import ppretty

from threading import Thread
from threading import Event
from datetime import datetime, time as datetime_time, timedelta, date as datetime_date

import telebot
from telebot import apihelper

class Bot:
    _bot=None
    __force_stop=False
    __exit = Event()
    __proxy = None
    __thread=None
    _logger=None
    _default_channel=None
    _token=None

    _commands = {  # command description used in the "help" command
        'start'       : 'Get used to the bot',
        'help'        : 'Gives you information about the available commands',
    }

    @staticmethod
    def get_api_exception_info(e):
        if e.result.status_code == 429:
            #too frequent try
            retry_after=None
            description=None
            data = e.result.json()
            if not data.get('ok'):  # pragma: no cover
                description = data.get('description')
                parameters = data.get('parameters')
                if parameters:
                    retry_after = parameters.get('retry_after')
            return description, retry_after
        msg=str(e)
        return msg, None

    @staticmethod
    def log_message(filename:str, message):
        with open(filename, "a") as myfile:
            myfile.write("user: " + str(message.from_user)+", time : "+datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        + "\nMessage: "+str(message.text)+"\n")

    def __start_separate_thread(self):
        fail_count = 0
        while not self.__force_stop:
            try:
                self._logger.info("bot start polling")
                self._bot.infinity_polling()
                self._logger.info("bot end polling")
            except Exception:
                fail_count += 1
                if self.__proxy == "socks5h://localhost:9050" and (fail_count % 10) == 0 :
                    #we are using tor, let's restart it
                    self._logger.info("restarting tor service, failt count: "+str(fail_count))
                    os.system("sudo service tor restart")
                self._logger.exception("bot exception:")
                self.__exit.wait(60)
        self._logger.info("end bot thread")

    def start(self):
        if not self._token: return

        self.__thread = Thread(target=self.__start_separate_thread)
        self.__thread.kill_received = False
        self.__thread.start()

    def stop(self):
        self._logger.info("bot stopping ...")
        if not self.__force_stop:
            self.__force_stop=True
            self.__exit.set()
            self._bot.stop_polling()
            if self.__thread:
                self.__thread.kill_received = True
                self.__thread.join()
                self.__thread = None
            self._logger.info("bot stopped")

    def send_msg_bot_long_check(self, channel, message, reply_markup=None, parse_mode='Markdown'):
        if not self._token: return

        if not channel:
            channel=self._default_channel
        while not self.__force_stop:
            try:
                if not message:
                    return # not allowed empty messages
                #remove escape characterrs, that telegram not processing in messages
                if parse_mode and parse_mode!='HTML':
                    message = message.replace("_", "\\_").replace("*", "\\*").replace("[", "\\[").replace("`", "\\`")

                # because telegram not sending very long messages, we divide it into small parts
                msgs = [message[i:i + 4096] for i in range(0, len(message), 4096)]

                for text in msgs[:-1]:
                    self._bot.send_message(channel, text, parse_mode=parse_mode)
                message = self._bot.send_message(
                    channel, msgs[-1], reply_markup=reply_markup, parse_mode=parse_mode)
                return message.message_id
            except telebot.apihelper.ApiException as e:
                description, retry_after=Bot.get_api_exception_info(e)
                if retry_after :
                    self._logger.info(f"send message waiting {retry_after} seconds")
                    self.__exit.wait(retry_after)
                else:
                    self._logger.exception("send message:")
                    return None

    def edit_message_text(self, chat_id, message_id, message, parse_mode=None, markup=None):
        if not chat_id:
            chat_id=self._default_channel
        while not self.__force_stop:
            try:
                message = self._bot.edit_message_text(message, chat_id, message_id, reply_markup=markup, parse_mode=parse_mode)
                return message.message_id
            except telebot.apihelper.ApiException as e:
                description, retry_after=Bot.get_api_exception_info(e)
                if retry_after :
                    self._logger.info(f"send message waiting {retry_after} seconds")
                    self.__exit.wait(retry_after)
                else:
                    self._logger.exception(f"edit message, channel={chat_id}, message_id={message_id}")
                    return

    def delete_bot_message(self,chat_id, message_id):
        if not chat_id:
            chat_id=self._default_channel
        while not self.__force_stop:
            try:
                self._bot.delete_message(chat_id, message_id)
                return
            except telebot.apihelper.ApiException as e:
                description, retry_after=self._bot.get_api_exception_info(e)
                if retry_after :
                    self._logger.info(f"send message waiting {retry_after} seconds")
                    self.__exit.wait(retry_after)
                else:
                    self._logger.exception(f"delete message message_id={message_id}")
                    return

    def handle_exception_with_msg(self, channel, bot_text="[!] error", exc_text="error"):
        self._logger.exception(exc_text)
        self.send_msg_bot_long_check(channel, bot_text)


    def command_start(self,message):
        self.command_help(message)

    def command_help(self,message):
        help_text = "The following commands are available: \n"
        for key in self._commands:  # generate help text out of the commands dictionary defined at the top
            help_text += "/" + key + ": "
            help_text += self._commands[key] + "\n"
        self.send_msg_bot_long_check(message.chat.id, help_text)  # send the generated help page

    def __init__(self, token:str, logger, bot_channel=None, proxy:str=None):
        logger.info(f"{__name__} initing ...")
        if proxy: #apply proxy if exist for telegram blocking
            telebot.apihelper.proxy = {'https': proxy}
            __proxy=proxy

        bot = telebot.TeleBot(token)
        self._logger=logger
        self._default_channel=bot_channel
        self._bot = bot
        self._token=token

        # handle the "/start" command
        @bot.message_handler(commands=['start'])
        def command_start(m):
            self.command_start(m)

        # help page
        @bot.message_handler(commands=['help'])
        def command_help(m):
            self.command_help(m)

