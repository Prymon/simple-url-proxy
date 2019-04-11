from seemmo.http.httpServer import HttpServer
from seemmo.tools import utils
from tornado.httpclient import AsyncHTTPClient
import logging


def start():
    try:
        AsyncHTTPClient.configure(None, max_clients=1000)
        http_server = HttpServer()
        http_server.start_web()
    except Exception as e:
        logging.exception(e.message)


if __name__ == '__main__':
    utils.initLogging()
    start()
