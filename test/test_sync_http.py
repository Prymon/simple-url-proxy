import tornado.web
import tornado.httpserver
import tornado.ioloop
from tornado.gen import coroutine, Return
from concurrent.futures import ThreadPoolExecutor
from tornado.httpclient import AsyncHTTPClient, HTTPRequest as TornadoHttpRequest, HTTPClientError
import random


class StartTornado:
    def __init__(self):
        self.http_server = None
        self.tornado = tornado.web.Application(handlers=[
            (r'/test', TestHandler),
            (r'/V1/ComparisonServer.*', ProxyHandler)
        ])

    def start_web(self):
        self.http_server = tornado.httpserver.HTTPServer(self.tornado)
        self.http_server.bind(18888)
        self.http_server.start(10)
        tornado.ioloop.IOLoop.instance().start()


class ProxyHandler(tornado.web.RequestHandler):
    #executor = ThreadPoolExecutor(100)
    executor = ThreadPoolExecutor(40)

    def data_received(self, chunk):
        pass

    @tornado.gen.coroutine
    def post(self, *args, **kwargs):
        request_uri = self.request.uri
        request_body = self.request.body if random.randint(1, 10) % 2 is 1 else str.encode('{"element": []}')

        request_result = yield HttpRequest().async_post('http://127.0.0.1:18888/test?%s' % request_uri, request_body)
        #print request_result
        self.write(request_result)
        self.finish()


class HttpRequest:
    http_client = None

    def __init__(self):
        if HttpRequest.http_client is None:
            HttpRequest.http_client = AsyncHTTPClient()
        pass

    @tornado.gen.coroutine
    def async_post(self, request_url, body):
        request = TornadoHttpRequest(url=request_url, method='POST', body=body)
        response = yield HttpRequest.http_client.fetch(request)
        ret = response.body
        raise Return(ret)


class TestHandler(tornado.web.RequestHandler):

    def data_received(self, chunk):
        pass

    def post(self, *args, **kwargs):
        self.write({'body': len(self.request.body), 'request': self.request.uri})
        self.finish()


if __name__ == '__main__':
    StartTornado().start_web()
