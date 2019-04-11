# coding=utf-8
import random
import re

import logging
from seemmo.response.responseEntity import ResponseEntity
from tornado.gen import Return
from tornado.gen import coroutine
from tornado.httpclient import HTTPError
from conf.settings import PROXY_SETTING, FAKEREQUEST
from seemmo.common.proxyException import ProxyException
from seemmo.http.httpRequest import HttpRequest
from seemmo.tools.utils import getReflectClass, halt
from seemmo.tools.time import *


# 根据settings.py的路由规则和代理策略，请求上层服务,将返回结果交给ProxyResponseHandler
class ProxyRouter:
    # request_uri = None
    # header_dict = None
    # request_body = None
    # method = None
    # proxy_setting = None
    # request_url_list = list()

    def __init__(self, request_uri, header_dict, request_body, method):
        self.request_uri = request_uri
        self.header_dict = header_dict
        self.request_body = request_body
        self.method = method
        self.proxy_setting = None
        self.request_url_list = list()

    @coroutine
    def process(self):
        if FAKEREQUEST is True:
            raise Return(ResponseEntity.create_success_entity(None, None, {'errorCode': 0, 'message': 'success'}))
        for setting in PROXY_SETTING:
            for rule in setting['url_pattern']:
                if re.match(rule, self.request_uri):
                    self.proxy_setting = setting
                    proxy_type = setting['proxy_type']
                    if proxy_type == 'all':
                        result = yield self.proxy_request_all()
                        raise Return(result)
                    elif proxy_type == 'face_lib_mixed':
                        result = yield self.proxy_request_face_lib_mixed()
                        raise Return(result)
                    else:
                        result = yield self.proxy_request_loop()
                        raise Return(result)
        raise ProxyException(-2, 'can`t find valid url pattern, please check url: %s' % self.request_uri)

    # 轮询请求配置的节点
    @coroutine
    def proxy_request_loop(self):
        server_list = self.proxy_setting['server_list']
        rand_server = self.get_priority_server_choice(server_list)
        request_url = 'http://%s:%s%s' % (rand_server['ip'], rand_server['port'], self.request_uri)
        response_entity = None
        try:
            if self.method == 'GET':
                request_result = yield HttpRequest().async_get(request_url, self.header_dict, request_timeout=self.proxy_setting['request_timeout'])
                response_entity = ResponseEntity.create_success_entity(request_url, self.request_body, request_result)
            if self.method == 'POST':
                request_result = yield HttpRequest().async_post(request_url, self.header_dict, self.request_body, request_timeout=self.proxy_setting['request_timeout'])
                response_entity = ResponseEntity.create_success_entity(request_url, self.request_body, request_result)
        except HTTPError as e:
            response_entity = ResponseEntity.create_failed_entity(request_url, self.request_body, e.code, e.message, e.response.body)
            logging.error('request %s got http error,code %s, message %s' % (request_url, e.code, e.message))
        response_handler_class_name = self.proxy_setting['response_handler']
        response_handler_module_path = 'seemmo.response'
        response_handler = getReflectClass(response_handler_module_path, response_handler_class_name)
        if not response_handler:
            halt('invalid response_handler: %s, please check settings.py!')
        merge_result = response_handler().merge_result([response_entity])
        raise Return(merge_result)

    # 给每个请求的节点都镜像发送请求
    @coroutine
    def proxy_request_all(self):
        response_entity_list = None
        try:
            if self.method == 'GET':
                yield_list = self.batch_async_get_request()
                request_result_list = yield yield_list
                response_entity_list = self.format_batch_async_result(request_result_list)
            if self.method == 'POST':
                yield_list = self.batch_async_post_request()
                request_result_list = yield yield_list
                response_entity_list = self.format_batch_async_result(request_result_list)
        except HTTPError as e:
            response_entity_list = [ResponseEntity.create_failed_entity(self.request_uri, self.request_body, e.code, e.message, e.response.body)]
            logging.error('request %s got http error,code %s, message %s' % (self.request_uri, e.code, e.message))
        response_handler_class_name = self.proxy_setting['response_handler']
        response_handler_module_path = 'seemmo.response'
        response_handler = getReflectClass(response_handler_module_path, response_handler_class_name)
        if not response_handler:
            halt('invalid response_handler: %s, please check settings.py!')
        merge_result = response_handler().merge_result(response_entity_list)
        raise Return(merge_result)

    '''
    人像库混合比对模式，较特殊，详阅读下说明：
    假设有如下场景，我们有ABC三台比对节点
    A: 内存库(libId=1)
    B: 显存库(libId=5)
    C: 显存库(libId=5)
    应用层想通过一次请求，同时对这两个库进行比对请求。
    例如： request proxt compareMemAndGpu(libId=1,5)
    但比对服务一次只支持请求一种类型的库，那么就需要对每台机器进行2次请求，一次内存比对，一次显存比对
    第一次： request A compareMem(libId=1,5)
    第二次： request A compareGpu(libId=1,5)
    第三次： request B compareMem(libId=1,5)
    第四次： request B compareGpu(libId=1,5)
    第五次： request C compareMem(libId=1,5)
    第六次： request C compareGpu(libId=1,5)
    再将他们的结果合并
    目前用于--结构化平台--人像库比对/布控
    '''

    @coroutine
    def proxy_request_face_lib_mixed(self):
        response_entity_list = None
        try:
            if self.method == 'GET':
                yield_list = self.batch_async_mixed_get_request()
                request_result_list = yield yield_list
                response_entity_list = self.format_batch_async_result(request_result_list)
            if self.method == 'POST':
                yield_list = self.batch_async_mixed_post_request()
                request_result_list = yield yield_list
                response_entity_list = self.format_batch_async_result(request_result_list)
        except HTTPError as e:
            response_entity_list = [ResponseEntity.create_failed_entity(self.request_uri, self.request_body, e.code, e.message, e.response.body)]
            logging.error('request %s got http error,code %s, message %s' % (self.request_uri, e.code, e.message))
        response_handler_class_name = self.proxy_setting['response_handler']
        response_handler_module_path = 'seemmo.response'
        response_handler = getReflectClass(response_handler_module_path, response_handler_class_name)
        if not response_handler:
            halt('invalid response_handler: %s, please check settings.py!')
        merge_result = response_handler().merge_result(response_entity_list)
        raise Return(merge_result)

    @staticmethod
    def get_priority_server_choice(server_list):
        rand_list = list()
        for server in server_list:
            for i in range(int(server['priority'])):
                rand_list.append(server)
        return random.choice(rand_list)

    def batch_async_get_request(self):
        yield_list = []
        for server in self.proxy_setting['server_list']:
            request_url = 'http://%s:%s%s' % (server['ip'], server['port'], self.request_uri)
            self.request_url_list.append(request_url)
            yield_list.append(HttpRequest().async_get(request_url, self.header_dict, request_timeout=self.proxy_setting['request_timeout']))
        return yield_list

    def batch_async_post_request(self):
        yield_list = []
        for server in self.proxy_setting['server_list']:
            request_url = 'http://%s:%s%s' % (server['ip'], server['port'], self.request_uri)
            self.request_url_list.append(request_url)
            yield_list.append(HttpRequest().async_post(request_url, self.header_dict, body=self.request_body, request_timeout=self.proxy_setting['request_timeout']))
        return yield_list

    def batch_async_mixed_get_request(self):
        yield_list = []
        real_request_urls = self.proxy_setting['real_request_urls']
        for server in self.proxy_setting['server_list']:
            for tail_url in real_request_urls:
                request_url = 'http://%s:%s%s' % (server['ip'], server['port'], tail_url)
                self.request_url_list.append(request_url)
                yield_list.append(HttpRequest().async_get(request_url, self.header_dict, request_timeout=self.proxy_setting['request_timeout']))
        return yield_list

    def batch_async_mixed_post_request(self):
        yield_list = []
        real_request_urls = self.proxy_setting['real_request_urls']
        for server in self.proxy_setting['server_list']:
            for tail_url in real_request_urls:
                request_url = 'http://%s:%s%s' % (server['ip'], server['port'], tail_url)
                self.request_url_list.append(request_url)
                yield_list.append(HttpRequest().async_post(request_url, self.header_dict, body=self.request_body, request_timeout=self.proxy_setting['request_timeout']))
        return yield_list

    def format_batch_async_result(self, batch_result):
        response_entity_list = list()
        index = 0
        for result in batch_result:
            response_entity_list.append(ResponseEntity.create_success_entity(self.request_url_list[index], self.request_body, result))
            index = index + 1
        return response_entity_list
