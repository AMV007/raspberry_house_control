import controls

from RootSkill import RootSkill

class DeviceControl(RootSkill):

    def get_desc(self):
        return "управлять устройствами, если они прописаны в конфиге"

    def __init__(self):
        super().__init__(self.__class__.__name__)

    def process(self, command:str)->bool:
         # devices control
        if command in ["вентилятор", "включи вентилятор", "включить вентилятор",  "выключи вентилятор", "выключить вентилятор"]:
            self.say_ok(command)
            controls.get(controls.control_TempHum).switch(external_command=True)
        elif command in ["вентилятор авто"]:
            self.say_ok(command)
            controls.get(controls.control_TempHum).set_auto()
        elif command in ["розетка", "включи розетку", "включить розетку",  "выключи розетку", "выключить розетку"]:
            self.say_ok(command)
            controls.get(controls.control_Outlet).switch(external_command=True)
        elif command in ["розетка авто"]:
            self.say_ok(command)
            controls.get(controls.control_Outlet).set_auto()
        elif command in ["кондиционер","включи кондиционер","выключи кондиционер","жарко"]:
            self.say_ok(command)
            controls.get(controls.control_ConditionerControl_IR).switch(external_command=True)
        elif command in ["кондиционер авто"]:
            self.say_ok(command)
            controls.get(controls.control_ConditionerControl_IR).set_auto()
        elif command in ["включи все"]:
            self.say_ok(command)
            controls.enable()
        elif command in ["выключи все"]:
            self.say_ok(command)
            controls.disable()
        elif command in ["все авто"]:
            self.say_ok(command)
            controls.set_auto()
        elif command in ["полить","полив","полив сйчас","полить сейчас"]:
            self.say_ok(command)
            controls.get(controls.control_Watering).do_watering("force from STT")

        # noise control
        elif command in ["тихо"]:
            self.say_ok(command)
            controls.get(controls.control_NoisyActions).force_silent = True
        elif command in ["говори"]:
            self.say_ok(command)
            controls.get(controls.control_NoisyActions).force_silent = False

        else:
            return False
        return True
