from datetime import date, datetime, time, timedelta
from babel.dates import format_date, format_datetime, format_time

from OpenAi import OpenAi

from RootSkill import RootSkill
import config
import app_logger
import TTS

class OpenAI(RootSkill):
    openai = None

    def get_desc(self):
        return "чатгпт"

    def __init__(self):
        super().__init__(self.__class__.__name__)
        self.openai = OpenAi(config.openai_api_key)

    def process(self, command:str)->bool:
        app_logger.info(f"unknown command, trying chatGpt: {command}")
        self.say(TTS.Commands.THINK)
        self.say(self.openai.get_chat_gpt_answer(command))
        app_logger.info(f"end trying chatGpt: {command}")
        return True
