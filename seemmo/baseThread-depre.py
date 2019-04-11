import logging
import mapping
import traceback
import time
import ctypes
from threading import Thread
from Queue import Empty as QueueEmpty, Full as QueueFull

__author__ = 'wct'

class BaseThread(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.isStop = False

    def stop(self):
        self.isStop = True


    def process(self):
        pass

    def threadInit(self):
        pass

    def threadUnInit(self):
        pass

    def run(self):
        self.threadId = ctypes.CDLL('libc.so.6').syscall(186)
        self.threadInit()
        logging.info('thread is starting %s' % (self.name))
        while not self.isStop:
            try:
                self.process()
            except Exception as e:
                logging.error('exception occurs when get data! %s' % (traceback.format_exc()))
                time.sleep(1)
        logging.info('thread is stopped %s' % (self.name))
        self.threadUnInit()

