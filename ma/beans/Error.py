#coding=utf-8
__author__ = 'wxy325'

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
        1006:'请使用司机登录',
        1007:'请使用乘客登录',
        1008:'该司机暂无位置信息',
        1009:'查询结果为空',
        1010:'订单不存在',
        1011:'权限不足',
        1012:'此司机不存在',
        1013:'当前乘客暂无订单',
        1014:'当前乘客有未完成的订单，请不要重复下单'


    }
    @staticmethod
    def errorWithCode(error_code):
        return Error(error_code, Error.errorDict[error_code])
