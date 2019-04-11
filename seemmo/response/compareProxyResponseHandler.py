# coding=utf-8
from seemmo.response.baseProxyResponseHandler import BaseProxyResponseHandler
from seemmo.response.responseEntity import ResponseEntity
import ujson as json
import logging


class CompareProxyResponseHandler(BaseProxyResponseHandler):

    def __init__(self):
        BaseProxyResponseHandler.__init__(self)
        self.ignore_error_response = False

    # 1. 如果全部请求都成功，合并结果，返回成功
    # 2. 至少有一个请求返回成功，合并结果，返回成功，附带detail
    # 2. 所有请求失败（http error或response errorCode!=0），返回失败，附带detail
    # 3. http status code 恒返回200
    def merge_result(self, response_entity_list):
        success_entity_list = list()
        failed_entity_list = list()
        proxy_detail = dict()
        request_body = response_entity_list[0].request_body

        try:
            for response_entity in response_entity_list:
                proxy_detail[response_entity.request_url] = {'httpCode': response_entity.error_code, 'httpMessage': response_entity.error_message, 'body': response_entity.request_body,
                                                             'return_body': response_entity.return_body}
                if response_entity.error_code:
                    failed_entity_list.append(response_entity)
                    continue
                if not response_entity.return_body:
                    failed_entity_list.append(response_entity)
                    continue
                body = json.loads(response_entity.return_body)
                if ('errorCode' not in body) or cmp(str(body['errorCode']), '0') != 0:
                    failed_entity_list.append(response_entity)
                    continue
                else:
                    success_entity_list.append(response_entity)
            # 全都失败
            if not success_entity_list:
                body = {'errorCode': 1, 'message': 'error', 'proxy_detail': proxy_detail}
                return ResponseEntity.create_success_entity(None, None, body)
            # 至少有部分成功，合并结果
            success_body = dict()
            if not request_body:
                body = {'errorCode': 1, 'message': 'got empty post data', 'proxy_detail': proxy_detail}
                return ResponseEntity.create_success_entity(None, None, body)
            request_body = json.loads(request_body)
            if 'sourceDetail' in request_body:
                top_n = request_body['sourceDetail']['topN']
            else:
                top_n = request_body['sourceFaceDetail']['topN']
            for success_entity in success_entity_list:
                success_body = self.merge_body(success_body, success_entity.return_body, top_n)
            # 没有查询结果
            if not success_body:
                success_body = json.loads(success_entity_list[0].return_body)

            # 部分成功，返回结果+细节
            if failed_entity_list and not self.ignore_error_response:
                success_body = self.merge_proxy_detail(success_body, proxy_detail)
                return ResponseEntity.create_success_entity(None, None, success_body)
            # 全部成功，返回结果
            else:
                return ResponseEntity.create_success_entity(None, None, success_body)
        except Exception as e:
            logging.exception('fatal error %s' % e.message)
            body = {'errorCode': -99, 'message': e.message, 'proxy_detail': proxy_detail}
            return ResponseEntity.create_failed_entity(None, None, -99, e.message, body)

    @staticmethod
    def merge_body(result_body, body_tobe_merge, top_n):
        body_tobe_merge_dict = json.loads(body_tobe_merge)
        if not result_body:
            if ('data' not in body_tobe_merge_dict) or ('matchResults' not in body_tobe_merge_dict['data']):
                return result_body
            if (not body_tobe_merge_dict['data']['matchResults']) or ('topIds' not in body_tobe_merge_dict['data']['matchResults'][0]) or (
            not body_tobe_merge_dict['data']['matchResults'][0]['topIds']):
                return result_body
            result_body = body_tobe_merge_dict
        else:
            merge_match_results = dict()
            # 1. no result to merge
            if ('data' not in body_tobe_merge_dict) or ('matchResults' not in body_tobe_merge_dict['data']):
                return result_body
            if (not body_tobe_merge_dict['data']['matchResults']) or ('topIds' not in body_tobe_merge_dict['data']['matchResults'][0]) or (
            not body_tobe_merge_dict['data']['matchResults'][0]['topIds']):
                return result_body
            # 2. start merge
            for matchResults in result_body['data']['matchResults']:
                key_id = CompareProxyResponseHandler.get_key_id_in_match_result(matchResults)
                merge_match_results[key_id] = matchResults
            for matchResults in body_tobe_merge_dict['data']['matchResults']:
                key_id = CompareProxyResponseHandler.get_key_id_in_match_result(matchResults)
                if key_id in merge_match_results:
                    merge_match_results[key_id]['topIds'] = merge_match_results[key_id]['topIds'] + matchResults['topIds']
                else:
                    merge_match_results[key_id] = matchResults

            # sort by score
            def take_score(arr):
                return float(arr['matchingScore'])

            for node in merge_match_results.values():
                node['topIds'].sort(key=take_score, reverse=True)
                node['topIds'] = node['topIds'][0:top_n]
            result_body['data']['matchResults'] = list(merge_match_results.values())
            logging.error(json.dumps(result_body))
        return result_body

    @staticmethod
    def merge_proxy_detail(body, proxy_detail):
        body['proxy_detail'] = proxy_detail
        return body

    @staticmethod
    def get_key_id_in_match_result(match_result):
        key_id = 1
        if 'compareId' in match_result:
            key_id = match_result['compareId']
        if 'channelId' in match_result:
            key_id = match_result['channelId']
        return key_id
