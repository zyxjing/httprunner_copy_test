# tests/test_apiserver.py
#encoding:utf-8
from tests.base import ApiServerUnittest
import unittest
'''
继承ApiServerUnittest，使用Mock Server服务。
'''
class TestApiServer(ApiServerUnittest):    
    def setUp(self):
        super().setUp() # 调用父类ApiServerUnittest的setUp方法；但是父类的确没有setUp()方法；可能调用的是父类的setUpClass方法。--到时候调试看看
        self.headers = self.get_authenticated_headers()
        self.rest_all() # 清除上次运行代码创建出的用户
    
    def tearDown(self):
        super().tearDown() # 调用父类ApiServerUnittest的tearDown方法；但是父类的确没有tearDown()方法；可能调用的是父类的tearDownClass方法。--到时候调试看看
    
    def rest_all(self):
        '''
        公共方法：清空所有已创建的用户
        '''
        url = '%s/api/reset-all' % self.host
        return self.api_client.get(url, headers = self.headers)
    
    def create_user(self, uid, name, pwd):
        '''
        公共方法：创建用户
        '''
        url = '%s/api/users/%d' % (self.host, uid)
        data = {
            "name" : name,
            "password" : pwd
        }
        return self.api_client.post(url, json = data, headers = self.headers)
    
    def update_user(self, uid, name, pwd):
        uid = 1001
        url = '%s/api/users/%d' % (self.host, uid)
        data = {
            "name" : name,
            "password" : pwd
        }
        return self.api_client.put(url, json = data, headers = self.headers)
    
    def get_user(self, uid):
        url = '%s/api/users/%d' % (self.host, uid)
        return self.api_client.get(url, headers = self.headers)
    
    def get_all_user(self):
        url = '%s/api/users' % self.host
        return self.api_client.get(url, headers = self.headers)    
    
    def delete_user(self, uid):
        url = '%s/api/users/%d' % (self.host, uid)
        return self.api_client.delete(url, headers = self.headers)
    
    def get_customized_response(self, status_code, headers, body):
        url = '%s/customize-response' % self.host
        data = {
            "status_code" : status_code,
            "headers" : headers,
            "body" : body
        }
        return self.api_client.post(url, json = data)
        
    def test_index(self):
        '''
        测试进入首页
        '''
        url = '%s/' % self.host
        resp = self.api_client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.text,'Hello World!')
        

    def test_create_user_ok(self):
        '''
        测试成功创建用户
        '''
        uid = 1001
        name = 'user_1001',
        pwd = 'pwd_1001'
        resp = self.create_user(uid, name, pwd)
        
        self.assertEqual(resp.status_code, 201)
        resp_json = resp.json()
        self.assertTrue(resp_json.get('success'))
        self.assertEqual(resp_json.get('msg'), "user created successfully.")
        
    
    def test_create_user_fail(self):
        '''
        测试重复创建用户
        '''
        uid = 1001
        name = 'user_1001',
        pwd = 'pwd_1001'
        self.create_user(uid, name, pwd) # 先创建一个用户
        resp = self.create_user(uid, name, pwd) # 再用相同的参数创建一个用户
    
        self.assertEqual(resp.status_code, 500)
        resp_json = resp.json()
        self.assertFalse(resp_json.get('success'))
        self.assertEqual(resp_json.get('msg'), "user already existed.")
        
            
    def test_update_user_fail(self):
        '''
        测试更新用户信息失败
        '''
        uid = 1001
        name = 'user_1001'
        pwd = 'pwd_1001'
        resp = self.update_user(uid, name, pwd)
        
        self.assertEqual(resp.status_code, 404)
        resp_json = resp.json()
        self.assertFalse(resp_json.get('success'))
        self.assertEqual(resp_json.get('data'), {})
    
    
    def test_update_user_ok(self):
        '''
        测试更新用户信息成功
        '''
        uid = 1001
        name = 'user_1001'
        pwd = 'pwd_1001'
        self.create_user(uid, name, pwd) # 先创建一个用户
        
        new_pwd = 'pwd_0814'
        resp = self.update_user(uid, name, new_pwd) # 在更新用户信息
        
        self.assertEqual(resp.status_code, 200)
        resp_json = resp.json()
        self.assertTrue(resp_json.get('success'))
        self.assertEqual(resp_json.get('data'), {"name" : name, "password" : new_pwd})
    
    
    def test_get_user_fail(self):
        '''
        测试获取用户失败
        '''
        uid = 1001
        resp = self.get_user(uid)
        
        self.assertEqual(resp.status_code, 404)
        resp_json = resp.json()
        self.assertFalse(resp_json.get('success'))
        self.assertEqual(resp_json.get('data'), {})
    
    
    def test_get_user_ok(self):
        '''
        测试获取用户失败
        '''
        uid = 1001
        name = 'user_1001'
        pwd = 'pwd_1001'
        self.create_user(uid, name, pwd) # 先创建用户
        resp = self.get_user(uid) # 再获取用户
        
        self.assertEqual(resp.status_code, 200)
        resp_json = resp.json()
        self.assertTrue(resp_json.get('success'))
        self.assertEqual(resp_json.get('data'), {"name" : name, "password" : pwd})

    
    def test_get_all_user_zero(self):
        '''
        测试获取所有用户，当没有用户时
        '''
        resp = self.get_all_user()
        
        self.assertEqual(resp.status_code, 200)
        resp_json = resp.json()
        self.assertTrue(resp_json.get('success'))
        self.assertEqual(resp_json.get('count'), 0)
        self.assertEqual(resp_json.get('items'), [])

    
    def test_get_all_user_one(self):
        '''
        测试获取所有用户，当有一个用户时
        '''
        uid = 1001
        name = 'user_1001'
        pwd = 'pwd_1001'
        self.create_user(uid, name, pwd) # 先创建一个用户
        
        resp = self.get_all_user() # 再获取用户
        
        self.assertEqual(resp.status_code, 200)
        resp_json = resp.json()
        self.assertTrue(resp_json.get('success'))
        self.assertEqual(resp_json.get('count'), 1)
        self.assertEqual(resp_json.get('items'), [{'name': name, 'password': pwd}])

    
    def test_delete_user_fail(self):
        '''
        测试删除用户失败
        '''
        uid = 1001
        resp = self.delete_user(uid) # 再删除用户
        
        self.assertEqual(resp.status_code, 404)
        resp_json = resp.json()
        self.assertFalse(resp_json.get('success'))
        self.assertEqual(resp_json.get('data'), {})
    
     
    def test_delete_user_ok(self):
        '''
        测试删除用户成功
        '''
        uid = 1001
        name = 'user_1001'
        pwd = 'pwd_1001'
        self.create_user(uid, name, pwd) # 先创建一个用户
        
        resp = self.delete_user(uid) # 再删除用户
        self.assertEqual(resp.status_code, 200)
        resp_json = resp.json()
        self.assertTrue(resp_json.get('success'))
        self.assertEqual(resp_json.get('data'), {"name" : name, "password" : pwd})
        
    
    def test_rest_all(self):
        '''
        测试清空所有用户
        '''
        resp = self.rest_all()
        
        self.assertEqual(resp.status_code, 200)
        resp_json = resp.json()
        self.assertTrue(resp_json.get('success', True))
    
    
    def test_get_customized_response_ok(self):
        status_code = 200
        headers = {
            "Content-Type" : "application/json"
        }
        body = {
            "success" : True,
            "msg" : "Congratulations on your success !"
        }
        resp = self.get_customized_response(status_code, headers, body)
        
        self.assertEqual(resp.status_code, status_code)
        self.assertEqual(resp.json(), body)
        
    @unittest.SkipTest
    def test_get_customized_response_fail(self):
        status_code = 500
        headers = {
            "Content-Type" : "application/json"
        }
        body = {
            "success" : False,
            "msg" : "Very disappointed, you have failed !"
        }
        resp = self.get_customized_response(status_code, headers, body)
        
        self.assertEqual(resp.status_code, status_code)
        self.assertEqual(resp.json(), body)

if __name__ == '__main__':
    unittest.main()
    print('stoped')