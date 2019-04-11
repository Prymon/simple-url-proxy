import ctypes
import logging
from logging import Formatter, getLogger, DEBUG, INFO, ERROR
from cloghandler import ConcurrentRotatingFileHandler

from seemmo.tools.paths import logging_path


def getReflectClass(module_path, class_name):
    module_name = class_name[0].lower() + class_name[1:]
    module_file_path = module_path + '.' + module_name
    # 'seemmo.' + settings.PROC_SETTING['location']+'.' + module_name
    module_object = __import__(module_file_path, fromlist=True)
    module_class = getattr(module_object, class_name)
    return module_class


def increase(stats, key, threadId, num):
    # pid = os.getpid()
    key = '%s-%d' % (key, threadId)
    if stats.has_key(key):
        stats[key] = stats[key] + num
    else:
        stats[key] = num


def getCurrentThreadID():
    return ctypes.CDLL('libc.so.6').syscall(186)


def initLogging(dir_path=logging_path('compare-proxy'), logger_level=INFO):
    formatter = Formatter('%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s')

    error = ConcurrentRotatingFileHandler(
        ('%s/%s' % (dir_path, 'error.log')),
        'a', 100 * 1024 * 1024,
        backupCount=10)
    error.setLevel(ERROR)
    error.setFormatter(formatter)

    info = ConcurrentRotatingFileHandler(
        ('%s/%s' % (dir_path, 'info.log')),
        'a', 100 * 1024 * 1024,
        backupCount=10)
    info.setLevel(INFO)
    info.setFormatter(formatter)

    debug = ConcurrentRotatingFileHandler(
        ('%s/%s' % (dir_path, 'debug.log')),
        'a', 100 * 1024 * 1024,
        backupCount=10)
    debug.setLevel(DEBUG)
    debug.setFormatter(formatter)

    from logging import StreamHandler
    console = StreamHandler()
    console.setLevel(INFO)
    console.setFormatter(formatter)

    logger = getLogger('')

    logger.addHandler(debug)
    logger.addHandler(info)
    logger.addHandler(error)
    logger.addHandler(console)
    logger.setLevel(logger_level)
    getLogger('tornado').level = ERROR


def halt(message):
    print('system halt: %s' % message)
    logging.fatal('system halt: %s' % message)
    import sys
    sys.exit()
