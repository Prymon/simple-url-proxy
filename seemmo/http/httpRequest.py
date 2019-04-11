# coding=utf-8
from tornado.gen import coroutine, Return
from tornado.httpclient import AsyncHTTPClient, HTTPRequest as TornadoHttpRequest, HTTPClientError
from seemmo.tools.time import *
from conf.settings import DEBUG
import logging


# offer async http request
class HttpRequest:
    http_client = None

    def __init__(self):
        if HttpRequest.http_client is None:
            HttpRequest.http_client = AsyncHTTPClient()
        pass

    @coroutine
    def async_get(self, request_url, header_dict, connect_timeout=1, request_timeout=5):
        time_interval = ms_now()
        ret = None
        try:
            if isinstance(header_dict, list):
                header_dict.append(("Connection", "keep-alive"))

            request = TornadoHttpRequest(url=request_url, headers=header_dict, connect_timeout=int(connect_timeout),
                                         request_timeout=int(request_timeout))
            response = yield HttpRequest.http_client.fetch(request)
            ret = response.body
            # raise Return(ret)
        except Exception as e:
            logging.error('async get error, request_url: %s, message: %s' % (request_url, e.message))
        finally:
            time_interval = mseconds_between(ms_now(), time_interval)
            logging.debug('%sms async get %s' % (time_interval, request_url))
            logging.debug('%sms async get %s result: %s' % (time_interval, request_url, ret))
        if ret is not None:
            raise Return(ret)
        else:
            raise Return(False)

    @coroutine
    def async_post(self, request_url, header_dict, body='', connect_timeout=1, request_timeout=5):
        time_interval = ms_now()
        ret = None
        try:
            if isinstance(header_dict, list):
                header_dict.append(("Connection", "keep-alive"))
            request = TornadoHttpRequest(url=request_url, headers=header_dict, method='POST', body=body,
                                         connect_timeout=int(connect_timeout), request_timeout=int(request_timeout))
            response = yield HttpRequest.http_client.fetch(request)
            ret = response.body
        except Exception as e:
            logging.error('async post error, request_url: %s, message: %s' % (request_url, e.message))
        finally:
            time_interval = mseconds_between(ms_now(), time_interval)
            logging.debug('%sms async post %s' % (time_interval, request_url))
            logging.debug(
                '%sms async post %s request_body: %s result: %s' % (time_interval, request_url, body, ret))
        if ret is not None:
            raise Return(ret)
        else:
            raise Return(False)
