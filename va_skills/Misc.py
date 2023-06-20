import utils.common
import sound
import STT
import TTS

import va_skills

from RootSkill import RootSkill

class Misc(RootSkill):

    def get_desc(self):
        return "немного общаться"

    def __init__(self):
        super().__init__(self.__class__.__name__)

    def process(self, command:str)->bool:
        # misc, just for fun
        if command in ["как тебя зовут","твое имя", "кто ты", "имя"]:
            self.say("я автоматизировнный помощник по дому, пока не до конца доделанный")
            keywords=" и ".join(STT.keywords)
            self.say(f"отзываюсь на : {keywords}")
        elif command in ["что ты умеешь", "что умеешь"]:
            self.say("я умею: "+va_skills.get_desc())
        elif command in ["отзовись", "привет", "ты меня слышишь"]:
            self.say(TTS.Commands.HELLO)
        elif command in ["спокойной ночи", "спокойной"]:
            self.say("Спокойной ночи")
        elif command in ["доброе утро", "доброе", "с добрым утром"]:
            self.say("С добрым утром")
        elif command in ["как дела", "как жизнь"]:
            self.say("Отлично, температура " +
                str(utils.common.get_cpu_temperature())+", у тебя как ?")
        elif command in ["ты хороший", "умный","ты хорошая","умная"]:
            self.say("спасибо за комплимент, вы мне тоже нравитесь")
        elif command in ["ты плохой", "ты тупой"]:
            self.say("прошу прощения исправлючь")
        elif command in ["люблю", "тебя люблю"]:
            self.say("и я тебя тоже люблю в силу своих электронных мозгов")
        elif command in ["голос"]:
            self.say("гав гав хозяин")
        elif command in ["отмена", "отмена комманды"]:
            self.say("всего хорошего")
        elif command in ["триста", "тристо", "скажи триста", "скажи тристо"]:
            self.say("явно дело тут не чисто !")
        else:
            return False
        return True
