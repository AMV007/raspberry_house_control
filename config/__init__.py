import pkgutil
import socket
import sys
import app_logger

# don't use underscores in hostnames, because system will ignore it

__all__ = []
for loader, module_name, is_pkg in pkgutil.walk_packages(__path__):
    hostname=socket.gethostname()
    load_module=""
    if hostname == "raspberrypihome":
        if module_name != "config_home":
            continue
    elif hostname == "raspberrypiflat":
        if module_name != "config_flat":
            continue
    elif hostname == "raspberrypiwork":
        if module_name != "config_work":
            continue
    else:
        if module_name != "config_default":
            continue

    __all__.append(module_name)
    _module = loader.find_module(module_name).load_module(module_name)
    globals()[module_name] = _module

    app_logger.warn("configuration loaded for : "+module_name)
    sys.modules[__name__] = __import__(module_name)
    break