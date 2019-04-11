import functools
import logging
from seemmo.tools.time import *


# can`t use for async func
def log_time(text='execute function'):
    def decorator(func):
        @functools.wraps(func)
        def warpper(*args, **kw):
            time_interval = ms_now()
            result = func(*args, **kw)
            time_interval = mseconds_between(ms_now(), time_interval)
            logging.info('%sms %s.%s %s' % (time_interval, text, func.__module__, func.__name__))
            return result

        return warpper

    return decorator
