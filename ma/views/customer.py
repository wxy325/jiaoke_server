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
        except KeyError:
            return responseError(1001)

            reject_driver_ids = []
        try:
            reject_driver_ids = request.POST['reject_driver_ids']
            str_id_list = reject_driver_ids.split('|')
            reject_driver_ids = [int(i) for i in str_id_list]
        except (KeyError, SyntaxError, ValueError):

            pass

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



############################
        CONSTANT_RADIUS_SMALL = 0.01
        CONSTANT_RADIUS_BIG = 0.02
        CONSTANT_Lrx = 50


        smallCircleDrivers = getNearDriverCircle(latitude, longitude, CONSTANT_RADIUS_SMALL) #获取小圈所有司机
        smallCircleDrivers = [d for d in smallCircleDrivers if d.id not in reject_driver_ids]
        jihe_U1 = [d for d in smallCircleDrivers if d.order_set.exclude(state=3).exclude(state=0).count() == 1] #筛选未完成Req为1的driver


        jihe_U1_ = []
        driver_to_sm = {}

        for d in jihe_U1:
            try:
                dOrder = d.order_set.exclude(state=3).exclude(state=0).get()

                orderLocationFrom = Location(dOrder.from_latitude, dOrder.from_longitude)
                orderLocationTo = Location(dOrder.destination_latitude, dOrder.destination_longitude)
                driverLocation = Location(d.location_info.latitude, d.location_info.longitude)



                if dOrder.state == 2:
                    #情况I
                    distanceA = getDistanceWithLocation(driverLocation, locationTo, (locationFrom, orderLocationTo))
                    distanceB = getDistanceWithLocation(driverLocation,orderLocationTo, (locationFrom, locationTo))
                    distanceC = getDistanceWithLocation(driverLocation, locationTo, (orderLocationTo, locationFrom))

                    minDistance = min(distanceA, distanceB, distanceC)
                    if distanceA == minDistance:
                        #情况a
                        dSM = getDistanceWithLocation(driverLocation, orderLocationTo) + getDistanceWithLocation(locationFrom, locationTo) - distanceA

                        if (getDistanceWithLocation(driverLocation, orderLocationTo, (locationFrom,)) - getDistanceWithLocation(driverLocation, orderLocationTo)) <= CONSTANT_Lrx and (getDistanceWithLocation(locationFrom, locationTo, (orderLocationTo,)) - getDistanceWithLocation(locationFrom, locationTo)) <= CONSTANT_Lrx:
                            jihe_U1_.append(d)
                            driver_to_sm[d] = dSM

                    elif distanceB == minDistance:
                        #情况b
                        dSM = getDistanceWithLocation(driverLocation, orderLocationTo) + getDistanceWithLocation(locationFrom, locationTo) - distanceA
                        if distanceB - getDistanceWithLocation(driverLocation, orderLocationTo) <= CONSTANT_Lrx:
                            jihe_U1_.append(d)
                            driver_to_sm[d] = dSM
                    else:
                        #情况c
                        dSM = 0
                        jihe_U1_.append(d)
                        driver_to_sm[d] = dSM

                else:
                    #情况II

                    distanceA = getDistanceWithLocation(driverLocation, locationTo, (orderLocationFrom, locationFrom, orderLocationTo))
                    distanceB = getDistanceWithLocation(driverLocation, orderLocationTo, (orderLocationFrom, locationFrom, locationTo))
                    distanceC = getDistanceWithLocation(driverLocation, locationTo, (orderLocationFrom, orderLocationTo, locationFrom))

                    minDistance = min(distanceA, distanceB, distanceC)
                    if distanceA == minDistance:
                        #情况a
                        dSM = getDistanceWithLocation(orderLocationFrom, orderLocationTo) + getDistanceWithLocation(locationFrom, locationTo) - getDistanceWithLocation(orderLocationFrom, locationTo, (locationFrom, orderLocationTo))
                        if (getDistanceWithLocation(orderLocationFrom, orderLocationTo, (locationFrom,)) - getDistanceWithLocation(orderLocationFrom, orderLocationTo)) <= CONSTANT_Lrx and (getDistanceWithLocation(locationFrom, locationTo, (orderLocationTo,)) - getDistanceWithLocation(locationFrom, locationTo)) <= CONSTANT_Lrx :
                            jihe_U1_.append(d)
                            driver_to_sm[d] = dSM
                    elif distanceB == minDistance:
                        dSM = getDistanceWithLocation(orderLocationFrom, orderLocationTo) + getDistanceWithLocation(locationFrom, locationTo) - getDistanceWithLocation(orderLocationFrom, orderLocationTo, (locationFrom, locationTo))
                        if (getDistanceWithLocation(orderLocationFrom, orderLocationTo, (locationFrom, locationTo)) - getDistanceWithLocation(orderLocationFrom, orderLocationTo)) <= CONSTANT_Lrx:
                            jihe_U1_.append(d)
                            driver_to_sm[d] = dSM
                        pass
                    else:
                        #情况c
                        dSM = 0
                        jihe_U1_.append(d)
                        driver_to_sm[d] = dSM
            except:
                pass

        #至此jihe_U1_与driver_to_sm完成，选取最大dSM
        if len(jihe_U1_):
            #U_有车，选取最大dSM的车并结束
            driver = max(jihe_U1_, key=lambda x:driver_to_sm[x])
            #TODO 更新路线信息
        else:#没车，执行(2)
            jihe_U2 = [d for d in smallCircleDrivers if d.order_set.exclude(state=3).exclude(state=0).count() == 0] #筛选未完成Req为1的driver

            if len(jihe_U2):
                #有车，继续执行

                driverToDistance = {}
                for d in jihe_U2:
                    try:
                        driverLocation = Location(d.location_info.latitude, d.location_info.longitude)
                        distance = getDistanceWithLocation(driverLocation, locationFrom)
                        driverToDistance[d] = distance
                    except:
                        pass
                driver = min(jihe_U2, key=lambda x:driverToDistance[x])
                #TODO 更新路线信息
            else:#没车，执行(3)
                bigCircleDrivers = getNearDriverCircle(latitude, longitude, CONSTANT_RADIUS_BIG) #获取大圈所有司机
                bigCircleDrivers = [d for d in bigCircleDrivers if d.id not in reject_driver_ids]
                jihe_U3 = [d for d in bigCircleDrivers if d.order_set.exclude(state=3).exclude(state=0).count() < 2]
                jihe_U3_ = []
                driver_to_lmi = {}

                for d in jihe_U3:
                    if d.order_set.exclude(state=3).exclude(state=0).count() == 1:
                        #情况I II
                        dOrder = d.order_set.exclude(state=3).exclude(state=0).get()
                        if dOrder.state==2:
                            #情况I
                            distanceA = getDistanceWithLocation(driverLocation, locationTo, (locationFrom, orderLocationTo))
                            distanceB = getDistanceWithLocation(driverLocation, orderLocationTo, (locationFrom, locationTo ))
                            distanceC = getDistanceWithLocation(driverLocation, locationTo, (orderLocationFrom, locationFrom))
                            minDistance = min(distanceA, distanceB, distanceC)
                            if minDistance == distanceA:
                                #a
                                lmi = getDistanceWithLocation(driverLocation, locationFrom)
                                if (getDistanceWithLocation(driverLocation, orderLocationTo, (locationFrom,)) - getDistanceWithLocation(driverLocation, orderLocationTo)) <= CONSTANT_Lrx and (getDistanceWithLocation(locationFrom, locationTo, (orderLocationTo)) - getDistanceWithLocation(locationFrom, locationTo)) <= CONSTANT_Lrx:
                                    jihe_U3_.append(d)
                                    driver_to_lmi[d] = lmi
                            elif minDistance == distanceB:
                                #b
                                lmi = getDistanceWithLocation(driverLocation, locationFrom)
                                if (getDistanceWithLocation(driverLocation, orderLocationFrom, (locationFrom, locationTo)) - getDistanceWithLocation(driverLocation, orderLocationTo)) <= CONSTANT_Lrx:
                                    jihe_U3_.append(d)
                                    driver_to_lmi[d] = lmi
                            else:
                                #c
                                lmi = getDistanceWithLocation(driverLocation, locationFrom, (orderLocationTo,))
                                jihe_U3_.append(d)
                                driver_to_lmi[d] = lmi
                        else:
                            #Dil            P0            Pid             Pd         Pi0
                            #driverLocation locationFrom  orderLocationTo locationTo orderLocationFrom
                            #情况II
                            distanceA = getDistanceWithLocation(driverLocation, locationTo, (orderLocationFrom, locationFrom, orderLocationTo))
                            distanceB = getDistanceWithLocation(driverLocation, orderLocationTo , (orderLocationFrom, locationFrom, locationTo))
                            distanceC = getDistanceWithLocation(driverLocation, locationTo, (orderLocationFrom, orderLocationTo, locationFrom))
                            minDistance = min(distanceA, distanceB, distanceC)


                            if minDistance == distanceA:
                                #a
                                lmi = getDistanceWithLocation(driverLocation, locationFrom, (orderLocationFrom,))
                                if (getDistanceWithLocation(orderLocationFrom, orderLocationTo, (locationFrom,)) - getDistanceWithLocation(orderLocationFrom, orderLocationTo)) <= CONSTANT_Lrx and (getDistanceWithLocation(locationFrom, locationTo, (orderLocationTo,)) - getDistanceWithLocation(locationFrom, locationTo)) <= CONSTANT_Lrx:
                                    jihe_U3_.append(d)
                                    driver_to_lmi[d] = lmi
                            elif minDistance == distanceB:
                                #b
                                lmi = getDistanceWithLocation(driverLocation, locationFrom, (orderLocationFrom,))
                                if (getDistanceWithLocation(orderLocationFrom, orderLocationTo, (locationFrom, locationTo)) - getDistanceWithLocation(orderLocationFrom, orderLocationTo)) <= CONSTANT_Lrx:
                                    jihe_U3_.append(d)
                                    driver_to_lmi[d] = lmi
                            else:
                                #c
                                lmi = getDistanceWithLocation(driverLocation, locationFrom, (orderLocationFrom, orderLocationTo,))
                    else:
                        #情况III
                        #count==0
                        lmi = getDistanceWithLocation(driverLocation, locationFrom)
                        jihe_U3_.append(d)
                        driver_to_lmi[d] = lmi

                #到此jihe_U3_更新完成
                if len(jihe_U3_):
                    driver = min(jihe_U3_, key=lambda x:driver_to_lmi[x])
                else:
                    #(4)未找到
                    driver = None






############################



        #driver = DriverInfo.objects.get(id=1)
        if driver is None:
            return responseError(1015)
            pass
        else:
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


