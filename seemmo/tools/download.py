from __future__ import absolute_import
import logging
import time

import urllib2

__author__ = 'fuxiangyu'

# import urllib
# def download(url):
#     url_opener = urllib.URLopener()
#     lasterr = ''
#
#     for i in range(3):
#         response = None
#         try:
#             response = url_opener.open(url)
#             result = response.read()
#             return result
#
#         except Exception as e:
#             logging.debug('exception occurs in %d download rounds! url: %s, exception: %s' % (i + 1, url, e))
#             lasterr = e
#             time.sleep(1)
#             continue
#
#         finally:
#             if response is not None:
#                 response.close()
#
#     logging.error('exception occurs when downloading! url: %s, exception: %s' % (url, lasterr))
#     return None



def download(url):
    req = urllib2.Request(url)
    lasterr = ''

    for i in range(3):
        try:
            response = urllib2.urlopen(req, timeout=10)
	
            if response and response.getcode() == (200 or 301 or 302):
                return response.read()
        except Exception as e:
            lasterr = e
            time.sleep(1)

        finally:
            try:
                response.close()
            except Exception:
                pass
    logging.error('exception occurs when downloading! url: %s, exception: %s' % (url, lasterr))
    return None

if __name__ == '__main__':
    link = 'http://pic32.photophoto.cn/20140711/0011024086081224_b.jpg'
    result = download(link)
    if result:
        print result
