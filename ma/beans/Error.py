#coding=utf-8

class Error:
    def __init__(self,error_code, error_desc):
        self.error_code = error_code
        self.error_desc = error_desc

    errorDict = {
        1000:'请使用Post方法',
        1001:'参数不完整',
        1002:'用户名或密码错误',
        1003:'用户名已存在',
        1004:'session过期，请重新登录',
        1005:'session不存在或过期，请重新登录',

    }
    @staticmethod
    def errorWithCode(error_code):
        return Error(error_code, Error.errorDict[error_code])
