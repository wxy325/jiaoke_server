from django.http import HttpResponse
import json
from ma.beans.Error import Error
from ma.models import UserSession
from ma.models import UserEntity


def responseError(errorCode):
    return HttpResponse(json.dumps(Error.errorWithCode(errorCode).__dict__,ensure_ascii=False))

def responseJson(dict):
    return HttpResponse(json.dumps(dict,ensure_ascii=False))

def responseSuccess():
    return responseJson({"result":True})

def getUserFromRequest(request):

    sessionId = request.POST['session_id']

    session = UserSession.objects.get(id = sessionId)
    if not session.checkSessionValid():
        raise UserSession.SessionExpireException
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