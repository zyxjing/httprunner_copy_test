import requests
from httprunner import utils

def run_single_testcase(testcase_dict):
    '''
    读取demo.json里的内容.一个demo.json相当于一个TestCase.
    '''
    # 获取demo里边的request
    req_kwargs = testcase_dict['request']
    
    # 获取request里边的url,method
    url = None
    method = None
    try:
        url = req_kwargs.pop('url')
        method = req_kwargs.pop('method')
    except KeyError:
        raise Exception('Params Error')
    
    # 发送request请求，获取response
    resp_obj = requests.request(method = method, url = url, **req_kwargs)
    
    # 比较实际响应内容，预期响应内容
    diff_content = utils.diff_response(resp_obj, testcase_dict['response'])
    
    # 如果和预期不一致，则返回False
    success = False if diff_content else True
    return success, diff_content