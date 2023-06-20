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

################################################################################
import inspect
from pathlib import Path

active=[]

#init all devices
def init(logger, telegram_warning_handle):
    global active
    logger.info(f"{__name__} initing ...")
    for cls in RootControl.RootControl.__subclasses__():
        new_cls=cls()
        if new_cls.probe():
            logger.info (f"control exist: {type(new_cls).__name__}")
            new_cls.set_telegram_warning_handle(telegram_warning_handle)
            active.append(new_cls)

def disable():
    for entry in active:
        entry.disable()

def enable():
    for entry in active:
        entry.enable()

def set_auto():
    for entry in active:
        entry.set_auto()

#because there must be only 1 control for each class - it will simplyfy me task slightly
def get(dev_module):
    name = dev_module.__name__
    for entry in active:
        filename=Path(inspect.getfile(entry.__class__)).resolve().stem
        if name==filename:
            return entry
    return None

def get_status_str():
    info = ""
    for entry in active:
        status=entry.get_status_str()
        if status:
            info+=status+"\n"
    return info