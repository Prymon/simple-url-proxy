import os
import logging


# same as 'nohup ... 2>&1 &'
def create():
    try:
        if os.fork() > 0:
            os._exit(0)
    except OSError as error:
        logging.debug("Failed to fork the first child: %s." % error.strerror)
        os._exit(-1)
        # end try

    os.chdir("/")
    os.setsid()
    os.umask(0)

    try:
        pid = os.fork()
        if pid > 0:
            os._exit(0)
    except OSError as error:
        logging.debug("Failed to fork the second child: %s." % error.strerror)
