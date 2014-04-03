#coding=utf-8
__author__ = 'wxy325'

from ma.models import UserEntity
from django.views.decorators.csrf import csrf_exempt
from ma.models import DriverLocationInfo
from ma.models import Order
from django.db.models import Q
from utility import *

@csrf_exempt
def driverUpdateLocation(request):
    if request.method == 'POST':
        #获取经纬度参数
        try:
            latitude = request.POST['latitude']
            longitude = request.POST['longitude']
        except KeyError:
            return responseError(1001)

        #获取driver
        try:
            driver = getDriverFromRequest(request)
        except UserSession.DoesNotExist, UserSession.SessionExpireException:
            return responseError(1005)
        except KeyError:
            return responseError(1001)
        except UserEntity.ShouldBeDriverException:
            return responseError(1006)

        #更新Location信息
        try:
            location = driver.location_info
        except DriverLocationInfo.DoesNotExist:
            location = DriverLocationInfo()
            driver.location_info = location;
            driver.save()

        location.latitude = float(latitude)
        location.longitude = float(longitude)

        location.update_time = datetime.now()
        location.save()

        return responseSuccess()
    else:
        return responseError(1000)



@csrf_exempt
def driverGetInfo(request):
    if request.method == 'POST':
        #获取driver
        try:
            driver = getDriverFromRequest(request)
        except UserSession.DoesNotExist, UserSession.SessionExpireException:
            return responseError(1005)
        except KeyError:
            return responseError(1001)
        except UserEntity.ShouldBeDriverException:
            return responseError(1006)

        return responseJson(driver.toDict())
    else:
        return responseError(1000)

@csrf_exempt
def driverGetLocation(request):
    if request.method == 'POST':
        #获取driver
        try:
            driver = getDriverFromRequest(request)
        except UserSession.DoesNotExist, UserSession.SessionExpireException:
            return responseError(1005)
        except KeyError:
            return responseError(1001)
        except UserEntity.ShouldBeDriverException:
            return responseError(1006)

        #返回地理位置信息
        try:
            location = driver.location_info
            dict = {key:location.__dict__[key] for key in ['longitude','latitude', 'update_time']}
            return responseJson(dict)
        except DriverLocationInfo.DoesNotExist:
            return responseError(1008)
    else:
        return responseError(1000)


@csrf_exempt
def driverGetOrder(request):
    if request.method == 'POST':
        #type 0新订单 1当前所有订单 2历史订单

        try:
            type = request.POST['type']
            type = int(type)
        except KeyError:
            return responseError(1001)

        #获取driver
        try:
            driver = getDriverFromRequest(request)
        except UserSession.DoesNotExist, UserSession.SessionExpireException:
            return responseError(1005)
        except KeyError:
            return responseError(1001)
        except UserEntity.ShouldBeDriverException:
            return responseError(1006)

        if type == 0:
            orders = driver.order_set.filter(state=0)
        elif type == 1:
            orders = driver.order_set.filter(Q(state=1)|Q(state=2))
        else:
            orders = driver.order_set.all()
        orders = orders.order_by('-create_date')

        response = [o.toDict() for o in orders]
        return responseJson(response)

    else:
        return responseError(1000)

@csrf_exempt
def driverUpdateOrder(request):
    if request.method == 'POST':
        #获取参数
        try:
            orderId = int(request.POST['order_id'])
            orderState = int(request.POST['order_state'])
        except KeyError:
            return responseError(1001)

        #获取driver
        try:
            driver = getDriverFromRequest(request)
        except UserSession.DoesNotExist, UserSession.SessionExpireException:
            return responseError(1005)
        except KeyError:
            return responseError(1001)
        except UserEntity.ShouldBeDriverException:
            return responseError(1006)

        try:
            order = Order.objects.get(id=orderId)
        except Order.DoesNotExist:
            return responseError(1010)

        if order.driver != driver:
            return responseError(1011)
        else:
            order.state = orderState
            order.save()
            order.driver.updateRoad()
            order.driver.save()
            return responseSuccess()
    else:
        return responseError(1000)