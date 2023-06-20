import subprocess

from RootSkill import RootSkill

class Radio(RootSkill):
    relaxfm_proc = None

    def get_desc(self):
        return "радио релакс фм"

    def __init__(self):
        super().__init__(self.__class__.__name__)

    def stop(self):
        #stop relaxfm
        subprocess.Popen("pkill mpv",stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT, shell=True)
        if self.relaxfm_proc:
            self.relaxfm_proc.kill()
            self.relaxfm_proc = None

        # if self.relaxfm_proc:
        #     if self.relaxfm_proc.poll() is None:
        #         self.relaxfm_proc.kill()
        #     self.relaxfm_proc = None

    def process(self, command:str)->bool:
        if command in ["запусти релаксфм", "запусти релакс","включи релакс","релакс"]:
            if not self.relaxfm_proc:
                self.relaxfm_proc=subprocess.Popen("mpv https://pub0302.101.ru:8443/stream/air/aac/64/200?d4fa --audio-device=alsa/sysdefault:CARD=USB",
                                            stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT, shell=True)
        elif command in ["останови релаксфм", "останови релакс", "выключи релакс"]:
            self.stop()
        else:
            return False
        return True
