from nextion import Nextion, EventType
import time
import struct
from datetime import datetime

import config
import bus
import app_logger


from RootDevice import RootDevice

class NextionDisplay(RootDevice):

    uart_bus = None
    last_waveform_update_minute=0

    def __init__(self):
        super().__init__()
        self.uart_bus=bus.UartBus.UartBus()

    def write_command(self, cmd: str):
        eof = "\xff\xff\xff"
        self.uart_bus.write(cmd+eof)
        result=self.uart_bus.read(4)
        if not cmd.startswith("add"): # for some reason for add not returning result
            if not result or len(result) < 1:
                #app_logger.info (f" nextion cmd={cmd} result empty")
                pass
            elif result[0] != 1:
                app_logger.info (f" nextion cmd={cmd} result: {result[0]}")

    def set_baud(self, baud):
        self.write_command(f"bauds={baud}")

    def set_backlight(self, percent):
        self.write_command(f"dims={percent}")

    def clear_screen(self, color:int):
        self.write_command(f"cls {color}")

    #for my sensors
    def set_temperature(self, val, update_waveform):
        if not val:
            self.write_command(f"t0.txt=\"None\"")
            return

        self.write_command(f"t0.txt=\"{str('%.1f' % val)} °C\"")

        if update_waveform:
            self.write_command(f"add 3,0,{int(val*140/40)}") # set return result after every command

    def set_humidity(self, val):
        if not val:
            self.write_command(f"t1.txt=\"\"")
            return
        self.write_command(f"t1.txt=\"{str('%.1f' % val)} %\"")

    def set_CO2(self, val, update_waveform):
        if not val:
            self.write_command(f"t2.txt=\"None\"")
            return

        self.write_command(f"t2.txt=\"{str(val)} ppm\"")
        if update_waveform:
            self.write_command(f"add 2,0,{int(val*90/1500)}") # set return result after every command

    def set_particles(self, data):

        if data:
            pm1 = data['data']['8']
            pm25 = data['data']['10']
            pm10 = data['data']['12']

            header_str=str(pm1[0])
            header_str+="  "+str(pm25[0])
            header_str+="  "+str(pm10[0])
            header_str+=" "+pm1[2]

            header_str=header_str.replace('μ','u')

            particles_str=str(pm1[1])
            particles_str+="  "+str(pm25[1])
            particles_str+="  "+str(pm10[1])
        else:
            header_str="none"
            particles_str="none"

        self.write_command(f"t3.txt=\"{header_str}\"")
        self.write_command(f"t4.txt=\"{particles_str}\"")

    def display(self, temperature, humidity, CO2, particles_str, backlight):
        with self.lock:
            update_waveform=False

            try:
                self.uart_bus.acqure_lock_switch_to_nextion()

                if datetime.now().minute!=self.last_waveform_update_minute:
                    update_waveform=True
                    self.last_waveform_update_minute=datetime.now().minute

                self.write_command("bkcmd=3") # set return result after every command
                #write_command("page 0") #set screen to page 1 for multiple page setups

                self.set_backlight(backlight)
                self.set_CO2(CO2, update_waveform)
                self.set_temperature(temperature, update_waveform)
                self.set_humidity(humidity)
                self.set_particles(particles_str)


            except Exception:
                app_logger.exception("nextion display exception:")
            finally:
                self.uart_bus.release_lock_switch()


    def probe(self):
        if not self.uart_bus or not self.uart_bus.probe(): #UART bus not exist
            return False
        if not hasattr(config, "NEXTION_DISPLAY_EXITS"):
            return False
        return True




