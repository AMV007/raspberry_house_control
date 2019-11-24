import subprocess
import picamera
from time import sleep
from picamera import PiCamera


from RootDevice import RootDevice

class Camera(RootDevice):
    def __init__(self):
        super().__init__(self.__class__.__name__)

    def probe(self):
        pipe = subprocess.Popen("/opt/vc/bin/vcgencmd get_camera", shell=True, stdout=subprocess.PIPE).stdout
        out=pipe.read()
        if "detected=1" in str(out):
            return True
        else:
            return False

    def do_photo(self):
        with self.lock:
            camera = PiCamera()
            # camera.resolution = (1680, 1050) #for some reason - don't know how switch to photo mode
            camera.start_preview()
            # Camera warm-up time
            sleep(2)
            camera.capture('/dev/shm/camera.jpg')
            camera.stop_preview()
            camera.close()

    def get_status_str(self):
        ret = "Camera: "
        if self.enabled:
            ret += "working now"
        else:
            ret += "disabled"
        return ret
