# from seemmo.tools.utils import initLogging
# from tornado.httpserver import HTTPServer
from tornado.web import *
import logging
import tornado.ioloop
import tornado.gen
import tornado.gen


class ProxyHandler(RequestHandler):

    def get(self):
        # tornado.gen.IOLoop.run_sync(self.sleep)
        tornado.gen.IOLoop.current().run_sync(self.sleep)
        self.write('123')
        self.finish()

    @tornado.gen.coroutine
    def sleep(self):
        yield gen.sleep(2)
        logging.info("begin to start http instance, pid:%d" % (os.getpid()))


import ujson as json


def merge_body(result_body, body_tobe_merge, top_n):
    body_tobe_merge_dict = json.loads(body_tobe_merge)
    if not result_body:
        result_body = body_tobe_merge_dict
    else:
        merge_match_results = dict()
        # 1. no result to merge
        if ('data' not in body_tobe_merge_dict) or ('matchResults' not in body_tobe_merge_dict['data']):
            return result_body
        # 2. start merge
        for matchResults in result_body['data']['matchResults']:
            merge_match_results[matchResults['compareId']] = matchResults
        for matchResults in body_tobe_merge_dict['data']['matchResults']:
            compareId = matchResults['compareId']
            if compareId in merge_match_results:
                merge_match_results[matchResults['compareId']]['topIds'] = merge_match_results[matchResults['compareId']]['topIds'] + matchResults['topIds']
            else:
                merge_match_results[matchResults['compareId']] = matchResults

        # sort by score
        def take_score(arr):
            return float(arr['matchingScore'])

        for node in merge_match_results.values():
            node['topIds'].sort(key=take_score, reverse=True)
            node['topIds'] = node['topIds'][0:top_n]
        result_body['data']['matchResults'] = list(merge_match_results.values())
    return result_body


if __name__ == '__main__':
    # initLogging()
    # app = Application(handlers=[(r'.*', ProxyHandler)], autoreload=False, debug=False)
    # server = tornado.httpserver.HTTPServer(app)
    # server.bind(8888)
    # server.start(1)
    # tornado.ioloop.IOLoop.instance().start()
    src = r'{"errorCode":0,"message":"success","data":{"taskId":1929,"srcFaceId":786786876,"matchResults":[{"compareId":123,"libraryId":89898,"topIds":[{"id":1,"matchingScore":98.8,' \
          r'"timestamp":1234567890000},{"id":2,"matchingScore":98.1,"timestamp":null}]}]}} '
    meg = r'{"errorCode":0,"message":"success","data":{"taskId":1929,"srcFaceId":786786876,"matchResults":[{"compareId":234,"libraryId":89898,"topIds":[{"id":5,"matchingScore":91.8,' \
          r'"timestamp":7415616565},{"id":5,"matchingScore":95.8,"timestamp":7415616565},{"id":5,"matchingScore":93.8,"timestamp":7415616565}]}]}} '
    res = merge_body(json.loads(src), meg, 2)
    print(json.dumps(res, indent=2))
