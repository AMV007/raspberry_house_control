import signal
from threading import Event

import app_logger

#   HANDLE CTRL+C and app exit
class GracefulKiller:
    app_running = True
    __run_at_exit = None # function for run at the app exit
    __exit_event = Event()

    def __init__(self, run_at_exit=None):
        self.__run_at_exit=run_at_exit
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)

    def exit(self):
        self.app_running = False
        self.__exit_event.set()
        app_logger.info('You pressed Ctrl+C, wait until all finish !...')
        #os.kill(os.getpid(), 9)  # otherwise bot will not stop

    def wait_app_exit(self, timeout=None):
        self.__exit_event.wait(timeout)

    def exit_gracefully(self, *args):
        self.exit()
        if self.__run_at_exit:
            self.__run_at_exit()