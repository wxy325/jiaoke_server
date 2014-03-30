#coding=utf-8
from django.db import models
import datetime


# Create your models here.

#User
class UserEntity(models.Model):
    user_name = models.CharField(max_length=11)
    password = models.CharField(max_length=30)
    real_name = models.CharField(max_length=30)
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

    def toDict(self):
        dict = {'driver_id':self.id,
                'car_number':self.car_number,
                'state':self.state,
                #'location_info':self.location_info.toDict(),
                'real_name':self.user.real_name}
        try:
            dict['location_info'] = self.location_info.toDict()
        except DriverLocationInfo.DoesNotExist:
            pass
        return dict

class CustomerInfo(models.Model):
    user = models.ForeignKey(UserEntity)

    def toDict(self):
        return {'real_name':self.user.real_name,}

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
    destination_longitude = models.FloatField()
    destination_latitude = models.FloatField()

    def toDict(self):
        dict = {key:self.__dict__[key] for key in ['male_number',
                                                   'female_number',
                                                   'create_date',
                                                   'state',
                                                   'type',
                                                   'from_longitude',
                                                   'from_latitude',
                                                   'destination_longitude',
                                                   'destination_latitude',]}
        dict['driver'] = self.driver.toDict()
        dict['customer'] = self.customer.toDict()
        return dict