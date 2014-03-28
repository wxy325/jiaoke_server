from django.db import models
import datetime


# Create your models here.

#User
class UserEntity(models.Model):
    user_name = models.CharField(max_length=11)
    password = models.CharField(max_length=30)
    real_name = models.CharField(max_length=30)
    gender = models.IntegerField()
    type_id = models.IntegerField()     #0driver 1customer

    class ShouldBeCustomerException(Exception):
        pass
    class ShouldBeDriverException(Exception):
        pass



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

class DriverInfo(models.Model):
    user = models.ForeignKey(UserEntity)
    car_number = models.CharField(max_length=10)
    state = models.IntegerField()   #0YES NO pingche
    location_info = models.ForeignKey(DriverLocationInfo)

class CustomerInfo(models.Model):
    user = models.ForeignKey(UserEntity)


#Order
class Order(models.Model):
    driver = models.ForeignKey(DriverInfo)
    customer = models.ForeignKey(CustomerInfo)
    number_of_people = models.IntegerField()
    create_date = models.DateTimeField()
    state = models.IntegerField()       #0weiJie 1yiJie 2yiSongDa

    destination_longitude = models.FloatField()
    destination_latitude = models.FloatField()

