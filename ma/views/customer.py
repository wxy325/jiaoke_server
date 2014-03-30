#coding=utf-8
__author__ = 'wxy325'

from ma.models import UserEntity
from django.views.decorators.csrf import csrf_exempt
from utility import *
from ma.baidu.location import Location
from ma.baidu.api import getDistanceWithLocation
import random


@csrf_exempt
def customerSearchDriver(request):
    #获取经纬度参数

    if request.method == 'POST':

        #获取参数
        try:
            latitude = request.POST['latitude']
            longitude = request.POST['longitude']
            des_latitude = request.POST['des_latitude']
            des_longitude = request.POST['des_longitude']
            reject_driver_ids = request.POST['reject_driver_ids']
        except KeyError:
            return responseError(1001)

        #获取customer
        try:
            customer = getCustomerFromRequest(request)
        except UserSession.DoesNotExist, UserSession.SessionExpireException:
            return responseError(1005)
        except KeyError:
            return responseError(1001)
        except UserEntity.ShouldBeDriverException:
            return responseError(1007)

        locationFrom = Location(latitude,longitude)
        locationTo = Location(des_latitude,des_longitude)



    else:
        return responseError(1000)



@csrf_exempt
def customerSubmitOrder(request):
    if request.method == 'POST':
        #获取customer
        try:
            customer = getCustomerFromRequest(request)
        except UserSession.DoesNotExist, UserSession.SessionExpireException:
            return responseError(1005)
        except KeyError:
            return responseError(1001)
        except UserEntity.ShouldBeDriverException:
            return responseError(1007)


    else:
        return responseError(1000)


@csrf_exempt
def customerGetOrder(request):
    if request.method == 'POST':
        #获取customer
        try:
            customer = getCustomerFromRequest(request)
        except UserSession.DoesNotExist, UserSession.SessionExpireException:
            return responseError(1005)
        except KeyError:
            return responseError(1001)
        except UserEntity.ShouldBeDriverException:
            return responseError(1007)


    else:
        return responseError(1000)


@csrf_exempt
def customerGetNearDriver(request):
    if request.method == 'POST':
        #获取customer
        try:
            customer = getCustomerFromRequest(request)
        except UserSession.DoesNotExist, UserSession.SessionExpireException:
            return responseError(1005)
        except KeyError:
            return responseError(1001)
        except UserEntity.ShouldBeDriverException:
            return responseError(1007)


    else:
        return responseError(1000)


