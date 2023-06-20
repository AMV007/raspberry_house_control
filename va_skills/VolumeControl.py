import sound

from RootSkill import RootSkill

class VolumeControl(RootSkill):

    def get_desc(self):
        return "управлять громкостью"

    def __init__(self):
        super().__init__(self.__class__.__name__)

    def process(self, command:str)->bool:
        if command in ["громче"]:
            sound.set_master_volume(+11)
            sound.beep(1)
        elif command in ["тише"]:
            sound.set_master_volume(-11)
            sound.beep(1)
        elif command in ["громкость максимум"]:
            sound.set_master_volume(+100)
            sound.beep(1)
        elif command.startswith("громкость"):
            split_data=command.split()
            del split_data[0:2]
            if len(split_data) == 0:
                self.say(f"Громкость: {int(sound.get_master_volume()/10)}")
            else:
                sound.set_master_volume(int(split_data[0]))
        elif command in ["замолчи","тихо","выключи звук"]:
            sound.beep(1)
            sound.set_master_volume(-101)
        else:
            return False
        return True
