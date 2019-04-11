# coding=utf-8

import tornado.web
from tornado.gen import coroutine
from conf.settings import ZOOKEEPER_SETTING
from conf.settings import PROXY_SETTING


# tornado http handler, offer kafka topic input ability

class ZooHttpHandler(tornado.web.RequestHandler):
    zoo_nodes = None

    def initialize(self):
        pass

    # handler injection hook
    @tornado.gen.coroutine
    def get(self):
        ret = {'errorCode': 0, 'message': 'success', 'proxy_settings': PROXY_SETTING}
        self.write(ret)
        self.finish()

    def data_received(self, chunk):
        pass
