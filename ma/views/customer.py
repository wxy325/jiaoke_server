#coding=utf-8
__author__ = 'wxy325'

from ma.models import *
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
            order_type = int(request.POST['order_type'])
            latitude = float(request.POST['latitude'])
            longitude = float(request.POST['longitude'])
            des_latitude = float(request.POST['des_latitude'])
            des_longitude = float(request.POST['des_longitude'])
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



        driver = DriverInfo.objects.get(id=1)
        return responseJson(driver.toDict())

    else:
        return responseError(1000)



@csrf_exempt
def customerCreateOrder(request):
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


        o = customer.order_set.exclude(state=3)
        if len(o) != 0:
            return responseError(1014)

        try:
            driverId = int(request.POST['driver_id'])
            type = int(request.POST['order_type'])
            male_number = int(request.POST['male_number'])
            female_number = int(request.POST['female_number'])
            destination_longitude = float(request.POST['des_longitude'])
            destination_latitude = float(request.POST['des_latitude'])
            from_latitude = float(request.POST['from_latitude'])
            from_longitude = float(request.POST['from_longitude'])
        except KeyError:
            return responseError(1001)

        try:
            driver = DriverInfo.objects.get(id = driverId)
        except DriverInfo.DoesNotExist:
            return responseError(1012)

        o = Order()
        o.customer = customer
        o.driver = driver
        o.type = type
        o.male_number = male_number
        o.female_number = female_number
        o.state = 0
        o.create_date = datetime.now()

        o.destination_latitude = destination_latitude
        o.destination_longitude = destination_longitude
        o.from_latitude = from_latitude
        o.from_longitude = from_longitude

        o.save()

        return responseJson(o.toDict())

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

        o = customer.order_set.exclude(state=3)

        if len(o) == 0:
            return responseError(1013)
        else:
            return responseJson(o[0].toDict())
    else:
        return responseError(1000)


@csrf_exempt
def customerGetNearDriver(request):
    if request.method == 'POST':
        '''
        #获取customer
        try:
            customer = getCustomerFromRequest(request)
        except UserSession.DoesNotExist, UserSession.SessionExpireException:
            return responseError(1005)
        except KeyError:
            return responseError(1001)
        except UserEntity.ShouldBeDriverException:
            return responseError(1007)
        '''

        try:
            latitude = float(request.POST['latitude'])
            longitude = float(request.POST['longitude'])
            delta_latitude = float(request.POST['delta_latitude'])
            delta_longitude = float(request.POST['delta_longitude'])
        except KeyError:
            return responseError(1001)

        driverList = getNearDriver(latitude, longitude, delta_latitude, delta_longitude)

        rJson = [d.toDict() for d in driverList]
        return responseJson(rJson)

    else:
        return responseError(1000)


