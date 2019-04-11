import requests
import logging
import ujson as json
from seemmo.tools.time import *

def post(url, param=None, timeout=3, **kwargs):
    param_json = param and json.dumps(param)

    with requests.Session() as session:
        lasterr = ''
        for i in range(3):
            try:
                result = session.post(url, data=param_json, timeout=timeout, **kwargs)
                return result
            except Exception as e:
                lasterr = e
                time.sleep(1)

        if param:
            for key in param.keys():
                if type(param[key]) in [str, unicode] and len(param[key]) >=1000:
                    del param[key]
            logging.error('exception occurs when post url[%s], param[%s]. [%s]' % (url, json.dumps(param), lasterr))
        else:
            logging.error('exception occurs when post url[%s], param[%s]. [%s]' % (url, param_json, lasterr))
        return None


def get(url, param=None, timeout=3):
    param_json = param and json.dumps(param)

    with requests.Session() as session:
        lasterr = ''
        for i in range(3):
            try:
                result = session.get(url, data=param_json, timeout=timeout)
                return result
            except Exception as e:
                lasterr = e
                time.sleep(1)

        if param:
            logging.error('exception occurs when get url[%s], param[%s]. [%s]' % (url, param_json, lasterr))
        else:
            logging.error('exception occurs when get url[%s]. [%s]' % (url, lasterr))
        return None


def download(url):
    lasterr = ''
    for i in range(3):
        try:
            pic = requests.get(url, timeout=10)
	    logging.error('return code %d' % (pic.status_code))
	    if pic.status_code == 200:
                return pic.content
	    else:
		logging.error('image download error! url %s, return code:%d' % (url, pic.status_code))
		return None
        except Exception as e:
            # logging.debug('exception occurs in %d download rounds! url: %s, exception: %s' % (i+1, url, e))
            lasterr = e
            time.sleep(1)
            continue

    logging.error('exception occurs when downloading! url: %s, exception: %s' % (url, lasterr))
    return None


if __name__ == '__main__':
    link = 'http://pic32.photophoto.cn/20140710/0011024086081224_b.jpg'
    result = download(link)
    print result



