# coding=utf-8
from seemmo.response.baseProxyResponseHandler import BaseProxyResponseHandler
from seemmo.response.responseEntity import ResponseEntity
import ujson as json
import logging


# 处理全部代理(all,即给每个节点发送同样的请求)方式下的结果合并
class AllProxyResponseHandler(BaseProxyResponseHandler):
    def __init__(self):
        BaseProxyResponseHandler.__init__(self)

    # 1. 如果全部请求都成功，返回成功
    # 2. 有任意请求失败（http error或response errorCode!=0），返回失败
    # 3. http status code 恒返回200
    def merge_result(self, response_entity_list):
        response_detail = dict()
        return_code = 0
        return_message = 'success'
        try:
            for response_entity in response_entity_list:
                response_detail[response_entity.request_url] = {'httpCode': response_entity.error_code, 'httpMessage': response_entity.error_message, 'body': response_entity.request_body,
                                                                'return_body': response_entity.return_body}
                if response_entity.error_code:
                    return_code = 1
                    return_message = response_entity.error_message or 'failed'
                    continue
                if not response_entity.return_body:
                    return_code = 99
                    return_message = response_entity.error_message or 'connect remote server failed'
                    continue
                try:
                    body = json.loads(response_entity.return_body)
                    if (not 'errorCode' in body) or cmp(str(body['errorCode']), '0') != 0:
                        return_code = 1
                        return_message = 'error'
                        continue
                except ValueError:
                    return_code = 1
                    return_message = 'json decode error'
                    continue
        except Exception as e:
            return_code = -99
            return_message = e.message
            logging.exception('unexpect error %s' % e.message)
        if return_code == 0:
            body = {'errorCode': 0, 'message': return_message}
            return ResponseEntity.create_success_entity(None, None, body)
        else:
            body = {'errorCode': return_code, 'message': return_message, 'proxy_detail': response_detail}
            return ResponseEntity.create_success_entity(None, None, body)
