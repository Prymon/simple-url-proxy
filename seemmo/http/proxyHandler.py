# coding=utf-8
import logging

import tornado.web
from tornado import escape
from concurrent.futures import ThreadPoolExecutor
from tornado.gen import coroutine
from tornado.httpclient import AsyncHTTPClient
from seemmo.router.proxyRouter import ProxyRouter


# tornado http handler, offer kafka topic input ability
# current proxy:
# 1. request uri
# 2. http headers
# 3. request body(post)

class ProxyHandler(tornado.web.RequestHandler):
    executor = ThreadPoolExecutor(40)

    # handler injection hook
    def initialize(self):
        pass

    @tornado.gen.coroutine
    def get(self):
        request_uri = self.request.uri
        request_header = list(self.request.headers.get_all())
        try:
            router = ProxyRouter(request_uri, request_header, None, 'GET')
            result = yield router.process()
            if result.error_code:
                logging.error('http error, code: %s, message: %s, body: result.return_body' % (result.error_code, result.error_message))
                self.send_error(result.error_code, body=result.return_body)
            else:
                self.write(result.return_body)
                self.finish()
        except tornado.httpclient.HTTPError as e:
            data = e.response.body or {'errorCode': -1, 'message': e.message}
            logging.error('http error, code: %s, message: %s' % (e.code, e.message))
            self.send_error(e.code, body=data)
        except Exception as e:
            data = {'errorCode': -1, 'message': e.message}
            logging.exception(e.message)
            self.send_error(522, body=data)

    @tornado.gen.coroutine
    def post(self):

        request_uri = self.request.uri
        request_header = list(self.request.headers.get_all())
        request_body = self.request.body
        try:
            router = ProxyRouter(request_uri, request_header, request_body, 'POST')
            result = yield router.process()
            if result.error_code:
                logging.error('http error, code: %s, message: %s, body: result.return_body' % (result.error_code, result.error_message))
                self.send_error(result.error_code, body=result.return_body)
            else:
                self.write(result.return_body)
                self.finish()
        except tornado.httpclient.HTTPError as e:
            data = e.response.body or {'errorCode': -1, 'message': e.message}
            logging.error('http error, code: %s, message: %s' % (e.code, e.message))
            self.send_error(e.code, body=data)
        except Exception as e:
            data = {'errorCode': -1, 'message': e.message}
            logging.exception(e.message)
            self.send_error(522, body=data)

    def data_received(self, chunk):
        pass

    def write_error(self, status_code, **kwargs):
        if 'body' in kwargs and kwargs['body']:
            self.write(kwargs['body'])

    def write(self, chunk):
        if chunk and type(chunk) is list:
            chunk = {'errorCode': -1, 'message': 'invalid proxy return', 'proxy_detail': chunk}
        return super(ProxyHandler, self).write(chunk)

    # @tornado.gen.coroutine
    # def get(self):
    #     request_uri = self.request.uri
    #     request_header = list(self.request.headers.get_all())
    #     try:
    #         request_url = 'http://192.168.1.15:18088%s' % request_uri
    #         result = yield HttpRequest().async_get(request_url, request_header)
    #         result = {'result': result, 'errorCode': 0, 'message': 'success', 'data': {'uri': request_uri, 'headers': request_header}}
    #         self.write(result)
    #         self.finish()
    #     except tornado.httpclient.HTTPError as e:
    #         data = e.response.body or {'errorCode': -1, 'message': e.message}
    #         logging.error('http error, code: %s, message: %s' % (e.code, e.message))
    #         self.send_error(e.code, body=data)
    #     except Exception as e:
    #         data = {'errorCode': -1, 'message': e.message}
    #         logging.exception(e.message)
    #         self.send_error(522, body=data)
