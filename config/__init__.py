import pkgutil
import socket
import sys

__all__ = []
for loader, module_name, is_pkg in pkgutil.walk_packages(__path__):
    hostname=socket.gethostname()
    load_module=""
    if hostname == "raspberryhome":
        if module_name != "config_home":
            continue
    elif hostname == "raspberryflat":
        if module_name != "config_flat":
            continue
    else:
        raise ValueError(f"unknown host name: {hostname}")
    
    __all__.append(module_name)
    _module = loader.find_module(module_name).load_module(module_name)
    globals()[module_name] = _module

    print("configuration loaded for : "+module_name)
    sys.modules[__name__] = __import__(module_name)
    break