#encoding:utf-8
import hmac
import hashlib
import random
import string
import json

'''
HMAC是密钥相关的哈希运算消息认证码，HMAC运算利用哈希算法，以一个密钥和一个消息为输入，生成一个消息摘要作为输出
hashlib提供了常见的摘要算法，如MD5，SHA1等等。
什么是摘要算法呢？摘要算法又称哈希算法、散列算法。它通过一个函数，把任意长度的数据转换为一个长度固定的数据串（通常用16进制的字符串表示）。
SHA1的结果是160 bit字节，通常用一个40位的16进制字符串表示。
'''

SECRET_KEY = 'DebugTalk'

def get_sign(*args):
    '''
    @summary:根据传进来的参数，返回加密的sign签名
    
    @return sign
    '''
    content = ''.join(args).encode('ascii')
    sign_key = SECRET_KEY.encode('ascii') # str to bytes
    sign = hmac.new(sign_key, content, hashlib.sha1).hexdigest()
    return sign

def gen_random_string(str_len):
    '''
    @summary: 返回指定长度的字符串
    
    @return str
    '''
    return ''.join(
        random.choice(string.ascii_letters + string.digits) for _ in range(str_len)
    )

def diff_response(actual_resp, expected_resp_json):
    '''
    比较实际响应结果、预期响应结果对应的json
    '''
    diff_content = {}
    actual_resp_json = parse_response_object(actual_resp)
    
    # 比较status_code，如果有不同，则加入到diff_content内
    status_code_diff = diff_statusCode(actual_resp_json.get('status_code'), expected_resp_json.get('status_code'))
    # 比较headers，如果有不同，则加入到diff_content内
    #headers_diff = diff_json(actual_resp_json.get('headers'), expected_resp_json.get('headers'))
    # 比较body，如果有不同，则加入到diff_content内
    body_diff = diff_json(actual_resp_json.get('body'), expected_resp_json.get('body'))
    
    if status_code_diff:
        diff_content['status_code'] = status_code_diff
     
    #diff_content['headers'] = headers_diff
    if body_diff:
        diff_content['body'] = body_diff
    
    return diff_content
    
def parse_response_object(actual_resp):
    '''
    将请求响应结果转换为指定的格式{status_code, headers, body}，
    和demo.json中定义的response格式一致，
    方便比较。
    '''
    resp_body = None
    try:
        resp_body = actual_resp.json()
    except ValueError:
        resp_body = actual_resp.text
    return {
        "status_code" : actual_resp.status_code,
        "headers" : actual_resp.headers,
        "body" : resp_body
    }         
    

def diff_statusCode(current_int, expected_int):
    '''
    比较两相同格式的json，如果不同，则将差异存入dict中
    '''
    json_diff = {} # 比较
    if current_int != expected_int:
        json_diff['status_code'] = {
                'value' : current_int,
                'expected' : expected_int
            }
    return json_diff

def diff_json(current_json, expected_json):
    '''
    比较两相同格式的json，如果不同，则将差异存入dict中
    '''
    if not isinstance(current_json, dict) or not isinstance(expected_json, dict):
        return {
            'value' : current_json,
            'expected' : expected_json
        }
    json_diff = {} # 比较
    
    for key, expected_value in expected_json.items():
        current_value = current_json.get(key) # 实际响应结果对应json的value值
        if current_value != expected_value:
            json_diff[key] = {
                'value' : current_value,
                'expected' : expected_value
            }
            
    return json_diff


def load_test_cases(path):
    with open(path , 'r', encoding='utf-8') as f:
        return json.load(f)
