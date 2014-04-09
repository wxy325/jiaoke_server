#coding=utf-8
from django.db import models
import datetime
from ma.baidu.api import getDistanceWithLocation
from ma.baidu.location import Location

# Create your models here.

#User
class UserEntity(models.Model):
    user_name = models.CharField(max_length=11)
    password = models.CharField(max_length=30)
    real_name = models.CharField(max_length=30, )

    gender = models.IntegerField()      #0male 1female
    type_id = models.IntegerField()     #0driver 1customer

    class ShouldBeCustomerException(Exception):
        pass
    class ShouldBeDriverException(Exception):
        pass

    def toDict(self):
        dict = {key:self.__dict__[key] for key in ['user_name',
                                                   'real_name',
                                                   'gender',
                                                   'type_id']}
        return dict


class UserSession(models.Model):
    #session_id = models.CharField(max_length=30)
    user = models.ForeignKey(UserEntity)
    expire_date = models.DateTimeField()

    def updateExpireDate(self):
        self.expire_date = datetime.datetime.now() + (datetime.date(2014,2,1) - datetime.date(2014,1,1))

    def checkSessionValid(self):
        expireDate = datetime.datetime.combine(self.expire_date.date(),self.expire_date.time())
        if datetime.datetime.now() > expireDate:
            return False
        else:
            return True

    class SessionExpireException(Exception):
        pass


#Infomation
class DriverLocationInfo(models.Model):
    longitude = models.FloatField()
    latitude = models.FloatField()
    update_time = models.DateTimeField()

    def toDict(self):
        return {'longitude':self.longitude,
                'latitude':self.latitude,
                'update_time':self.update_time}

class DriverInfo(models.Model):
    user = models.ForeignKey(UserEntity)
    car_number = models.CharField(max_length=10)
    state = models.IntegerField(default=0)   #0NO 1打车 2拼车
    location_info = models.ForeignKey(DriverLocationInfo)

    route_info = models.TextField();    #longitude,latitude|longitude,latitude

    company = models.CharField(max_length=20)


    def toDict(self):
        dict = {'driver_id':self.id,
                'car_number':self.car_number,
                'state':self.state,
                #'location_info':self.location_info.toDict(),
                'real_name':self.user.real_name,
                'company':self.company,
                'tel':self.user.user_name,
                }

        try:
            dict['location_info'] = self.location_info.toDict()
        except DriverLocationInfo.DoesNotExist:
            pass
        try:
            dict['route_info'] = self.route_info
        except:
            pass

        return dict

    def updateRoad(self):
        #计算路线
        driver = self
        orderCount = driver.order_set.exclude(state=3).count()
        if orderCount == 0:
            route = []
            pass
        elif orderCount == 1:
            dOrder = driver.order_set.exclude(state=3).get()

            locationFrom = Location(latitude=dOrder.from_latitude, longitude=dOrder.from_longitude)
            locationTo = Location(latitude=dOrder.destination_latitude, longitude=dOrder.destination_longitude)
            if dOrder.state == 2:
                route = [locationTo]
            else:
                route = [locationFrom, locationTo]
            pass
        elif orderCount == 2:

            dOrderList = driver.order_set.exclude(state=3).all()

            dOrder1 = dOrderList[0]
            locationFrom = Location(latitude=dOrder1.from_latitude, longitude=dOrder1.from_longitude)
            locationTo = Location(latitude=dOrder1.destination_latitude, longitude=dOrder1.destination_longitude)

            dOrder2 = dOrderList[1]
            orderLocationFrom = Location(dOrder2.from_latitude, dOrder2.from_longitude)
            orderLocationTo = Location(dOrder2.destination_latitude, dOrder2.destination_longitude)
            driverLocation = Location(driver.location_info.latitude, driver.location_info.longitude)


            if dOrder2.state == 2:
                distanceA = getDistanceWithLocation(driverLocation, locationTo, (locationFrom, orderLocationTo))
                distanceB = getDistanceWithLocation(driverLocation,orderLocationTo, (locationFrom, locationTo))
                distanceC = getDistanceWithLocation(driverLocation, locationTo, (orderLocationTo, locationFrom))
                minDistance = min(distanceA, distanceB, distanceC)
                if distanceA == minDistance:
                    route = [locationFrom, orderLocationTo, locationTo]
                elif distanceB == minDistance:
                    route = [locationFrom, locationTo, orderLocationTo]
                else:
                    route = [orderLocationTo, locationFrom, locationTo]
            else:


                distanceA = getDistanceWithLocation(driverLocation, locationTo, (orderLocationFrom, locationFrom, orderLocationTo))
                distanceB = getDistanceWithLocation(driverLocation, orderLocationTo, (orderLocationFrom, locationFrom, locationTo))
                distanceC = getDistanceWithLocation(driverLocation, locationTo, (orderLocationFrom, orderLocationTo, locationFrom))

                minDistance = min(distanceA, distanceB, distanceC)
                if distanceA == minDistance:
                    route = [orderLocationFrom, locationFrom, orderLocationTo, locationTo]
                elif distanceB == minDistance:
                    route = [orderLocationFrom, locationFrom, locationTo, orderLocationTo]
                else:
                    route = [orderLocationFrom, orderLocationTo, locationFrom, locationTo]

        fFirst = True
        routeStr = ''
        for lo in route:
            if fFirst:
                fFirst = False
            else:
                routeStr = routeStr + '|'
            routeStr = routeStr + str(lo.latitude) + ',' + str(lo.longitude)
        self.route_info = routeStr


class CustomerInfo(models.Model):
    user = models.ForeignKey(UserEntity)

    def toDict(self):
        return {'real_name':self.user.real_name,
                'customer_id':self.id,
                'tel':self.user.user_name}

#Order
class Order(models.Model):
    driver = models.ForeignKey(DriverInfo)
    customer = models.ForeignKey(CustomerInfo)
    male_number = models.IntegerField()
    female_number = models.IntegerField()
    create_date = models.DateTimeField()
    state = models.IntegerField()       #0新订单 1未接 2已接 3已送达
    type = models.IntegerField()        #1打车 2拼车


    from_longitude = models.FloatField()
    from_latitude = models.FloatField()
    from_desc = models.CharField(max_length=30)
    destination_longitude = models.FloatField()
    destination_latitude = models.FloatField()
    to_desc = models.CharField(max_length=30)

    def toDict(self):
        dict = {key:self.__dict__[key] for key in ['id',
                                                   'male_number',
                                                   'female_number',
                                                   'create_date',
                                                   'state',
                                                   'type',
                                                   'from_longitude',
                                                   'from_latitude',
                                                   'destination_longitude',
                                                   'destination_latitude',
                                                   'from_desc',
                                                   'to_desc',]}
        dict['driver'] = self.driver.toDict()
        dict['customer'] = self.customer.toDict()
        return dict