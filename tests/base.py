# tests/base.py
#encoding:utf-8
import unittest
from multiprocessing import Process
import time
import requests
from httpbin import app as httpbin_app
from httprunner import utils
from tests.api_server import app as flask_app

import threading

'''
为什么没有选择多线程模式（threading）？
是因为线程不支持显示终止（terminate），要实现终止服务会比使用multiprocessing更为复杂。
'''
debug = False
FLASK_APP_PORT = 5000
HTTPBIN_APP_PORT = 3458

def run_flask():
    flask_app.run(debug = debug, port = FLASK_APP_PORT)

def run_httpbin():
    httpbin_app.run(port = HTTPBIN_APP_PORT)

'''
ApiServerUnittest基类就绪后，对于需要用到Mock Server的单元测试用例集，只需要继承ApiServerUnittest即可；
其它的写法跟普通的单元测试完全一致。
'''
class ApiServerUnittest(unittest.TestCase):
    '''
    启动一个被应用在此测试的HTTP服务。
    '''
    @classmethod
    def setUpClass(cls):
        '''
        @summary:启动Flask Api接口服务进程（Mock Server）。
        采用多进程的方式，为了方便我们的单元测试用例可以和API接口服务同时运行。
        '''
        '''
        ## 方法一：采用多进程的模式（PS:但此模式不可在命令行里运行代码）
        cls.flask_process = Process(
            target = run_flask
        )
        cls.httpbin_process = Process(
            target = run_httpbin
        )
        # 启动自写的flask接口服务，可以使用其api发送请求（有逻辑判断，自己写）
        cls.flask_process.start()
        # 启动httpbin服务，可以向其发送请求（没有逻辑判断，需要替换host的port为HTTPBIN_APP_PORT)
        cls.httpbin_process.start()
        
        PS：运行此模块，需要在tearDownClass里边关闭子进程
        '''
        
        # 方法二：采用多线程的模式（后续：1）所有的测试运行完后，直接杀死子进程；2）将子线程设置未守护线程，主线程执行完毕后，守护线程会一起退出。）
        cls.flask_thread = threading.Thread(target = run_flask, name = 'flask_thread')
        cls.flask_thread.setDaemon(True)
        cls.flask_thread.start()
        #cls.flask_thread.join() # 不能等待子线程执行完毕，因为子线程运行不会执行完毕
        '''
        #httpbin服务不用启动
        cls.httpbin_thread = threading.Thread(thread_target = run_httpbin, thread_name = 'httpbin_thread')
        cls.httpbin_thread.start()
        '''
        
        # 等待服务启动完毕
        # 由于启动Server存在一定的耗时，因此在启动完毕后必须要等待一段时间（本例中0.1s就足够了）， 否则在执行单元测试用例时，调用的API接口可能还处于不可用状态。
        time.sleep(3)
        
        # 定义全局请求的host（子类自动继承此属性，可使用同一个host）
        cls.host = 'http://127.0.0.1:5000'
        # 定义全局请求的session（子类自动继承此属性，可用同一个api_client发送请求）
        cls.api_client = requests.Session()
    
    #@classmethod
    #def tearDownClass(cls):
        #'''
        #@summary:停止Flask API接口服务进程。
        #'''
        ##stop_thread(cls.flask_thread) # 强制结束一个子线程，会抛出SystemExit异常
        ##stop_thread(cls.httpbin_thread) # 强制结束一个子线程，会抛出SystemExit异常
        #print('当前活动的线程的个数：', threading.activeCount())
        #print('当前所有活动线程的列表：', threading.enumerate())
        
        
    def get_token(self, user_agent, device_sn, os_platform, app_version):
        '''
        @summary:向服务器发送请求，验证此客户端是否可信。
                 根据请求headers里边的数据计算出来的sign，和传过去的参数sign做比较，
                 如果一致，说明此客户端是被认可的（因为知道加密算法和秘钥），因此返回一个token（以后此客户端所有的请求都需要带上此token）。
                 
        @return token(16 length str)
        '''
        url = '%s/api/get-token' % self.host
        headers = {
            "Content-Type" : "application/json",
            "User-Agent" : user_agent,
            "device_sn" : device_sn,
            "os_platform" : os_platform,
            "app_version" : app_version
        }
        data = {
            "sign" : utils.get_sign(user_agent, device_sn, os_platform, app_version)
        }
        
        resp = self.api_client.post(url, json=data, headers = headers)
        self.assertEqual(resp.status_code, 200)
        resp_json = resp.json()
        self.assertTrue(resp_json.get('success'))
        self.assertIn('token', resp_json)
        token = resp_json.get('token')
        self.assertEqual(len(token), 16)
        return token
    
    def get_authenticated_headers(self):
        '''
        @summary:获取已经认证过的headers
        
        @return headers
        '''
        user_agent = "ios/10.3"
        device_sn = utils.gen_random_string(15) # 设备序列号
        os_platform = 'ios' # os平台
        app_version = '2.8.6' # app版本
        token = self.get_token(user_agent, device_sn, os_platform, 
                              app_version)
        headers = {
            "device_sn" : device_sn,
            "token" : token
        }
        return headers