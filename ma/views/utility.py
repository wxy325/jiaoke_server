from django.http import HttpResponse
import json
from ma.beans.Error import Error
from ma.models import UserSession
from ma.models import UserEntity
from ma.models import DriverLocationInfo
from ma.models import DriverInfo

from datetime import date
from datetime import datetime
from datetime import timedelta


class CJsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, date):
            return obj.strftime('%Y-%m-%d')
        else:
            return json.JSONEncoder.default(self, obj)

def responseError(errorCode):
    return responseJson(Error.errorWithCode(errorCode).__dict__)

def responseJson(j):
    h = HttpResponse(json.dumps(j,ensure_ascii=True, cls=CJsonEncoder))
    contentType = h['Content-Type'];
    contentType = contentType.replace('text/html','text/javascript')
    h['Content-Type']=contentType
    return h




def responseSuccess():
    return responseJson({"result":True})

def getUserFromRequest(request):

    sessionId = request.POST['session_id']

    session = UserSession.objects.get(id = sessionId)
    if not session.checkSessionValid():
        raise UserSession.SessionExpireException
    else:
        session.updateExpireDate()
    return session.user


def getCustomerFromRequest(request):
    user = getUserFromRequest(request)
    if user.type_id == 0:
        #driver
        raise UserEntity.ShouldBeCustomerException
    else:
        return user.customerinfo_set.get_or_create()[0]

def getDriverFromRequest(request):
    user = getUserFromRequest(request)
    if user.type_id == 1:
        #customer
        raise UserEntity.ShouldBeDriverException
    else:
        return user.driverinfo_set.get_or_create()[0]


def getNearDriver(latitude,longitude, deltaLa, deltaLo):

    locationInfoList = DriverLocationInfo.objects.filter(latitude__range=(latitude - deltaLa,latitude + deltaLa),
                                                         longitude__range=(longitude - deltaLo,longitude + deltaLo))

    #timeFrom = datetime.now() - timedelta(minutes=30)
    #locationInfoList = DriverLocationInfo.objects.filter(longitude__range=(latitude - deltaLa,latitude + deltaLa),
    #                                                     latitude__range=(longitude - deltaLo,longitude + deltaLo),
    #                                                     update_time__gte=timeFrom)

    driverList = []
    for lo in locationInfoList:
        try:
            driver = lo.driverinfo_set.get()
            driverList.append(driver)
        except DriverInfo.DoesNotExist:
            pass
    return driverList

def getNearDriverCircle(latitude, longitude, radius):
    driverList = getNearDriver(latitude, longitude, radius, radius)
    return [driver for driver in driverList
            if ((driver.location_info.latitude - latitude)**2 + (driver.location_info.longitude - longitude)**2) <= radius ** 2]


