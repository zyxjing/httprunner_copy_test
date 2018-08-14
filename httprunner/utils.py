#encoding:utf-8
import hmac
import hashlib
import random
import string

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