# coding=utf-8
from seemmo.response.compareProxyResponseHandler import CompareProxyResponseHandler
from seemmo.response.responseEntity import ResponseEntity
import ujson as json
import logging


class CompareProxyMixedResponseHandler(CompareProxyResponseHandler):
    def __init__(self):
        CompareProxyResponseHandler.__init__(self)
        self.ignore_error_response = True
