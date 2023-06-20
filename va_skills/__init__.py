import pkgutil

__all__ = []

#first load parent class
for loader, module_name, is_pkg in pkgutil.walk_packages(__path__):
    if not module_name.startswith("Root"):
        continue

    __all__.append(module_name)
    _module = loader.find_module(module_name).load_module(module_name)
    globals()[module_name] = _module

#second - subclasses
for loader, module_name, is_pkg in pkgutil.walk_packages(__path__):
    if module_name.startswith("Root") or module_name.startswith("manage"):
        continue
    __all__.append(module_name)
    _module = loader.find_module(module_name).load_module(module_name)
    globals()[module_name] = _module

############################################################
import inspect
from pathlib import Path

active=[]

#init all skills
def init(logger, telegram_warning_handle):
    global active
    logger.info(f"{__name__} initing ...")
    for cls in RootSkill.RootSkill.__subclasses__():
        new_cls=cls()
        logger.info (f"skill exist: {type(new_cls).__name__}")
        new_cls.set_telegram_warning_handle(telegram_warning_handle)
        active.append(new_cls)

    #add OpenAI at the end it will be corner case if nothing good
    for entry in active:
        if entry.name == "skill OpenAI":
            active.remove(entry)
            active.append(entry)
            break

def get_desc()->str:
    res=""
    for entry in active:
        res+=entry.get_desc()+","
    return res

def process(command:str)->bool:
    for entry in active:
        if entry.process(command):
            return True
    return False

def stop():
    for entry in active:
        entry.stop()

def deinit():
    stop()
    for entry in active:
        entry.deinit()