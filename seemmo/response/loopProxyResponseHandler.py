# coding=utf-8
from seemmo.response.baseProxyResponseHandler import BaseProxyResponseHandler
from seemmo.response.responseEntity import ResponseEntity
import ujson as json
import logging


# 处理轮询代理(loop)方式下的结果合并
class LoopProxyResponseHandler(BaseProxyResponseHandler):
    def __init__(self):
        BaseProxyResponseHandler.__init__(self)

    def merge_result(self, response_entity_list):
        response_detail = dict()
        try:
            response_entity = response_entity_list[0]
            response_detail[response_entity.request_url] = {'httpCode': response_entity.error_code, 'httpMessage': response_entity.error_message, 'body': response_entity.return_body,
                                                            'return_body': response_entity.return_body}
            # 如果有http异常，返回http错误码
            if response_entity.error_code:
                body = response_entity.return_body or {'errorCode': response_entity.error_code, 'message': response_entity.error_message, 'proxy_detail': response_detail}
                return ResponseEntity.create_failed_entity(None, None, response_entity.error_code, response_entity.error_message, body)
            # 否则返回原文
            body = response_entity.return_body or {'errorCode': '-1', 'message': 'remote server no response', 'proxy_detail': response_detail}
            if type(body) is str:
                body = json.loads(body)
            body['proxy_target'] = response_entity.request_url
            return ResponseEntity.create_success_entity(None, None, body)
        except Exception as e:
            logging.exception('unexpect error %s' % e.message)
            body = {'errorCode': -99, 'message': e.message, 'proxy_detail': response_detail}
            return ResponseEntity.create_success_entity(None, None, body)
