# tests/api_server.py
#encoding:utf-8
import json
from httprunner import utils
from flask import Flask, request, make_response
from functools import wraps
'''
api接口服务
搭建一套简单的API接口服务，也就是Mock Server.
然后我们在采用TDD开发模式的时候，就可以随时随地将框架代码跑起来，开发效率也会大幅提升。
'''
app = Flask(__name__)

''' storage/存储 all users'data
data structure:
    users_dict = {
       'uid1': {
           'name': 'name1',
           'password': 'pwd1'
       },
       'uid2': {
           'name': 'name2',
           'password': 'pwd2'
       }
    }
'''
users_dict = {}

''' storage all token data
data structure:
    token_dict = {
        'device_sn1' : 'token1',
        'device_sn2' : 'token2'
    }
'''
token_dict = {}

'''
装饰器：验证request请求headers中是否有device_sn、token参数
'''
def validate_request(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        '''
        @summary:验证请求的headers含有{device_sn, token}，且
        @param headers{device_sn, token}
        
        @return headers{'Content-Type':'application/json'},content{'success' : False,'msg' : 'Authorization failed!'}
        '''
        # 获取request headers中的device_sn、token
        device_sn = request.headers.get('device_sn', '')
        token = request.headers.get('token', '')
        
        # 判断request headers中是否存在device_sn、token
        if not device_sn or not token:
            # 构建response的content
            result = {
                'success' : False,
                'msg' : 'device_sn or token is null'
            }
            # 构建response
            response = make_response(json.dumps(result), 401)
            # 构建response的headers
            response.headers['Content-Type'] = 'application/json'    
            # 返回response
            return response
        
        # 判断request headers中的device_sn、token 是否和 之前存储的token 一致
        if token_dict[device_sn] != token:
            result = {
                'success' : False,
                'msg' : 'Authorization failed!'
            }
            response = make_response(json.dumps(result), 403)
            response.headers['Content-Type'] = 'application/json'
            return response
        
        return func(*args, **kwargs)
    
    return wrapper
            

@app.route('/')
def index():
    return 'Hello World!'

@app.route('/api/get-token', methods = ['POST'])
def get_token():
    '''
    @summary:获取token
    @param ：headers{User-Agent, device_sn, os_platform, app_version}、json{sign:@sign}
    
    @return response({success, msg/token}, status_code)
    '''
    # post请求的headers：User-Agent，device_sn，os_platform，app_version
    user_agent = request.headers.get('User-Agent', '')
    device_sn = request.headers.get('device_sn', '')
    os_platform = request.headers.get('os_platform', '')
    app_version = request.headers.get('app_version', '')
    # post请求的内容 {sign : @sign}
    data = request.get_json()
    sign = data.get('sign', '')
    
    # 通过post请求的headers计算出签名sign
    expected_sign = utils.get_sign(user_agent, device_sn, os_platform, app_version)

    # 构建response
    response = None
    if expected_sign != sign:# 如果计算出的签名 和 传过来的签名不一致
        result = {
            'success' : False,
            'msg' : 'Authorization failed!'
        }
        response = make_response(json.dumps(result), 403)
    else: # 如果签名一致
        token = utils.gen_random_string(16) # 创建一个随机字符串，当做token
        token_dict[device_sn] = token
        
        result = {
            'success' : True,
            'token' : token
        }
        response = make_response(json.dumps(result), 200)
    # 构建response的headers  
    response.headers['Content-Type'] = 'application/json'
    
    # 返回response
    return response
    
@app.route('/customize-response', methods = ['POST'])
def get_customized_response():
    '''
    @summary: 获取定制的response
    @param request body: {status_code : <int>, headers : <dict>, body : <dict>}
    
    @return response(body, status_code)
    '''
    expected_resp_json = request.get_json() # 获取post请求内容，示例：{status_code, headers, body}
    
    # 分解post 内容json
    status_code = expected_resp_json.get('status_code', 200)
    headers_dict = expected_resp_json.get('headers', {})
    body = expected_resp_json.get('body', {})
    
    # 构建 response content
    response = make_response(json.dumps(body), status_code)
    
    # 构建response headers
    for header_key, header_value in headers_dict.items():
        response.headers[header_key] = header_value
    
    # 返回response
    return response        

@app.route('/api/users/<int:uid>', methods = ['POST'])
@validate_request
def create_user(uid):
    '''
    @summary:创建一个用户。URL为：/api/users/1000。（1000也是用户自己填的）
    @param json:{'name': 'name1','password': 'pwd1'}
    
    @return response({success, msg}, status_code)
    '''
    result = {}
    status_code = 0
    
    user = request.get_json() #返回json参数  示例：{'name': 'name1','password': 'pwd1'}
    if uid not in users_dict: #如果此用户之前并未创建
        result = {
            'success' : True,
            'msg' : 'user created successfully.'
        } #响应结果
        status_code = 201 #响应状态
        users_dict[uid] = user #将新用户放入dict中。
    else: #如果此用户之前已经创建了
        result = {
            'success' : False,
            'msg' : 'user already existed.'
        } #响应结果
        status_code = 500 #响应状态
    
    #json.dumps将python数据结构转换为JSON
    response = make_response(json.dumps(result), status_code) #创建一个响应结果
    response.headers['Content-Type'] = 'application/json' #设置响应的headers
    return response #返回响应结果

@app.route('/api/users/<int:uid>', methods = ['PUT'])
@validate_request
def update_user(uid):
    '''
    @summary:更新用户信息
    @parms uid:用户ID
    
    @return response({success, data}, status_code)
    '''
    success = False
    status_code = 0
    
    user = users_dict.get(uid, {}) #根据uid获取用户，如果存在，则返回所有信息；如果不存在，则返回空dict
    if user: #如果用户真的存在
        user = request.get_json() #示例：'uid2': {'name': 'name2','password': 'pwd2'}
        success = True
        status_code = 200
        users_dict[uid] = user
    else: #如果用户不存在
        success = False
        status_code = 404

    #构建response的content
    result = {
        'success' : success,
        'data' : user
    }
    
    #构建response
    response = make_response(json.dumps(result), status_code)
    response.headers['Content-Type'] = 'application/json'
    
    #返回response
    return response
    
@app.route('/api/users/<int:uid>')
@validate_request
def get_user(uid):
    '''
    @summary: 获取指定uid的用户
    
    @return response
    '''
    # 获取指定uid的user
    user = users_dict.get(uid, {}) #示例：{'name': 'name2','password': 'pwd2'}
    # 构建response的content
    if user:
        result = {
            'success' : True,
            'data' : user
        }
        status_code = 200
    else:
        result = {
            'success' : False,
            'data' : user
        }
        status_code = 404
    
    # 构建response
    response = make_response(json.dumps(result), status_code)
    # 构建response.headers
    response.headers['Content-Type'] = 'application/json'
    # 返回response
    return response


@app.route('/api/users')
@validate_request
def get_users():
    '''
    @summary:获取所有的用户
    
    @return response(user, status_code)
    '''
    # user          ->    'uid1': {'name': 'name1','password': 'pwd1'}
    # users_list    ->     [{'name': 'name1','password': 'pwd1'},{'name': 'name2','password': 'pwd2'}]
    # 获取所有的用户
    users_list = [user for uid, user in users_dict.items()]
    # 构建response content
    users = {
        'success' : True,
        'count' : len(users_list),
        'items' : users_list
    }
    # 构建response
    response = make_response(json.dumps(users), 200)
    # 构建response headers
    response.headers['Content-Type'] = 'application/json'
    #返回response
    return response

@app.route('/api/users/<int:uid>', methods = ['DELETE'])
@validate_request
def delete_user(uid):
    '''
    @summary: 删除指定uid的用户
    
    @return response
    '''
    user = users_dict.pop(uid, {}) # 删除指定用户
    
    # 判断用户是否存在
    if user:
        success = True
        status_code = 200
    else:
        success = False
        status_code = 404
        
    # 构建response content    
    result = {
        'success' : success,
        'data' : user
    }
    # 构建response
    response = make_response(json.dumps(result), status_code)
    # 构建response headers
    response.headers['Content-Type'] = 'application/json'
    # 构建response
    return response

@app.route('/api/reset-all')
@validate_request
def clear_users():
    '''
    @summary: 清除所有的用户
    
    @return response.content{success}
    '''
    users_dict.clear() # 清除所有用户
    # 构建response content
    result = {
        'success' : True
    }
    # 构建response
    response = make_response(json.dumps(result), 200)
    # 构建response.headers
    response.headers['Content-Type'] = 'application/json'
    # 返回response
    return response