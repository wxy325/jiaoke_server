from django.http import HttpResponse
import json
from ma.beans.Error import Error
from ma.models import UserSession
from ma.models import UserEntity
from datetime import date
from datetime import datetime


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
    h = HttpResponse(json.dumps(j,ensure_ascii=False, cls=CJsonEncoder))
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