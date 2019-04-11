# coding=utf-8
import logging
import os
import signal

import time
import psutil
import tornado.httpclient
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web

from conf.settings import HTTP_SERVER_SETTING
from seemmo.common.zooHandler import ZooHandler
from seemmo.http.proxyHandler import ProxyHandler
from seemmo.http.zooHttpHandler import ZooHttpHandler


class HttpServer(tornado.web.Application):
    def __init__(self):
        self.handlers = None
        self.proc_pool = None
        self.http_server = None
        self.zooHandler = None
        self.http_setting = HTTP_SERVER_SETTING
        self.init_handler()
        self.pid = psutil.Process(os.getpid())
        self.processId = os.getpid()
        logging.info('current pid:%d' % self.processId)
        tornado.web.Application.__init__(self, handlers=self.handlers, autoreload=False, debug=False)

    # init http request handler
    def init_handler(self):
        self.handlers = [
            (r'/zoo.*', ZooHttpHandler),
            (r'/V1/ComparisonServer.*', ProxyHandler),
            (r'/proxy.*', ProxyHandler)
        ]

    def init_zookeeper(self):
        logging.info('starting zookeeper...')
        self.zooHandler = ZooHandler()
        logging.info('finished register zookeeper')

    # start http server
    def start_web(self):
        signal.signal(signal.SIGTERM, self.signal_handler)
        signal.signal(signal.SIGINT, self.signal_handler)

        # register zookeeper
        self.init_zookeeper()
        logging.info('finish start zookeeper')
        self.http_server = tornado.httpserver.HTTPServer(self)
        self.http_server.bind(self.http_setting['port'])
        self.http_server.start(self.http_setting['process_num'])
        logging.info("begin to start http instance, pid:%d" % (os.getpid()))
        tornado.ioloop.IOLoop.instance().start()

    # 要平滑停止，每个tornado的（子）进程都要正确关闭（IOLoop.instance().stop()）
    # 只有主进程的zookeeper handler需要停止
    def signal_handler(self, sigNum, frame):
        logging.info("begin to deal signal handler 【CURRENT_PID: %s, MAIN_PID: %s】" % (os.getpid(), self.processId))
        # 主进程停止
        if os.getpid() == self.processId:
            if self.zooHandler:
                self.zooHandler.stop()
            logging.info("main stopped, pid: %s" % os.getpid())
            tornado.ioloop.IOLoop.instance().stop()
        # 子进程停止
        else:
            if tornado.ioloop.IOLoop.instance():
                tornado.ioloop.IOLoop.instance().stop()
            logging.info("tornado child process stopped, pid: %s" % os.getpid())
