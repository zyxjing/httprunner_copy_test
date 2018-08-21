#encoding:utf-8
import threading
import ctypes
import inspect

def create_thread(thread_target, thread_name):
    '''
    创建一个新进程
    '''
    new_thread = threading.Thread(target = thread_target, name = thread_name)
    return new_thread

def _async_raise(tid, exctype):
    '''
    raises the exception, performs cleanup if needed
    '''
    tid = ctypes.c_long(tid)
    if not inspect.isclass(exctype):
        exctype = type(exctype)
        
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(ctypes))
    if res == 0:
        raise ValueError('invalid thread id')
    elif res != 1:
        ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
        raise SystemError('PyThreadState_SetAsyncExc failed')
    
def stop_thread(thread):
    '''
    关闭进程
    '''
    _async_raise(thread.ident, SystemExit)