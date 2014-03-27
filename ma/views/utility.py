from django.http import HttpResponse
import json
from ma.beans.Error import Error
from ma.models import UserSession


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
