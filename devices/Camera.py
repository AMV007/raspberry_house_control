import subprocess
from time import sleep
from picamera2 import Picamera2, Preview


from RootDevice import RootDevice

class Camera(RootDevice):

    def probe(self):
        pipe = subprocess.Popen("vcgencmd get_camera", shell=True, stdout=subprocess.PIPE).stdout
        out=pipe.read()
        if "detected=1" in str(out):
            return True
        else:
            return False

    def do_photo(self):
        with self.lock:
            picam2 = Picamera2()
            # camera.resolution = (1680, 1050) #for some reason - don't know how switch to photo mode
            picam2.start_preview(Preview.QTGL)
            picam2.start()
            # Camera warm-up time
            sleep(2)
            picam2.capture_file("/dev/shm/camera.jpg")
            picam2.close()

    def get_status_str(self):
        ret = "Camera: "
        if self.enabled:
            ret += "working now"
        else:
            ret += "disabled"
        return ret
