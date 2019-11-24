from multiprocessing.connection import Listener
from threading import Thread

import my_logging
import STT

# client


def child(conn):
    try:
        while Running:
            msg = conn.recv()
            my_logging.logger.info(msg[0])
            if msg[0] == "computer":
                command = STT.listen_phrase()
                STT.exec_command(command)
            break
    except Exception as e:
        my_logging.logger.exception("voice recognition exception:")
    finally:
        conn.send("done")

# server


def mother(address):
    global Running
    serv = Listener(address)
    while Running:
        client = serv.accept()
        child(client)


def listen_thread(arg):
    mother(('', 5000))


def init():
    global thread
    global Running

    Running = True

    thread = Thread(target=listen_thread, args=(10, ))
    thread.start()
    # thread.join()


def deinit():
    global thread
    global Running
    Running = False
    my_logging.logger.info("start stop sopare")
    if thread != None:
        thread.join()
    my_logging.logger.info("end stop sopare")
