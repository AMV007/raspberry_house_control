import fcntl
import logging
import os, sys
import signal
from time import sleep

import app_logger
import pathlib
from utils_common import create_dir_if_not_exist

#   CHECK ONLY 1 INSTANCE of APPLICATION RUNNING

def check_pid(pid):
    """ Check For the existence of a unix pid. """
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    else:
        return True

def check_only_one_instance():
    global inst_logger

    unique_app_id=str(pathlib.Path().absolute()).replace("/","_").replace(".","_")

    pathname = os.path.dirname(sys.argv[0])
    work_dir=os.path.abspath(pathname)
    pid_file = work_dir+"/lock/"+unique_app_id+".pid"
    lock_file = work_dir+"/lock/"+unique_app_id+".lock"

    create_dir_if_not_exist(pid_file)

    try:
        check_only_one_instance.fp = open(lock_file, "w")
        while True:
            try:
                fcntl.lockf(check_only_one_instance.fp,
                            fcntl.LOCK_EX | fcntl.LOCK_NB)
                app_logger.info("instance lock acquired sucessfully")
                with open(pid_file, "w") as fw:
                    fw.write(str(os.getpid()))
                return
            except IOError:
                # another instance is running
                with open(pid_file, "r") as fr:
                    curr_pid = int(fr.readline())

                app_logger.info(
                    "found running process with pid : "+str(curr_pid))
                check_only_one_instance.fp = open(lock_file, "w")

                if check_pid(curr_pid):
                    app_logger.info("trying to kill :"+str(curr_pid))
                    os.kill(curr_pid, signal.SIGTERM)  # or signal.SIGKILL
                    sleep(1)  # waiting for process exitting
                else:
                    app_logger.info("detected pid : "+str(
                        curr_pid)+", but not found in current system, and lock file locked\n looking process running at another system, can't kill it, exitting ...")
                    sys.exit(1)
    except Exception as e:
        app_logger.exception("unk exception occured during check instance, exitting\nyou can try to delete all files in lock directory and restart application ")
        sys.exit(1)
