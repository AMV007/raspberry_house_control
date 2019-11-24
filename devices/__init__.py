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

###############################################################################
import inspect
from pathlib import Path

active=[]

def set_all(all):
    for module in all:
        globals()[module] = __import__(module)

#init all devices
def init():
    global active
    for cls in RootDevice.RootDevice.__subclasses__():
        new_cls=cls()
        if new_cls.probe():
            print (f"device exist: {type(new_cls).__name__}")
            active.append(new_cls)

def disable():
    for entry in active:
        entry.disable()

def enable():
    for entry in active:
        entry.enable()

def get(dev_module):
    res=[]
    name = dev_module.__name__
    for entry in active:
        filename=Path(inspect.getfile(entry.__class__)).resolve().stem
        if name==filename:
            res.append(entry)
    if len(res) == 0:
        pass
    return res

def get_status_str():
    info = ""
    for entry in active:
        info+=entry.get_status_str()+"\n"
    return info
