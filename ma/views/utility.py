from django.http import HttpResponse
import json
from ma.beans.Error import Error

def responseError(errorCode):
    return HttpResponse(json.dumps(Error.errorWithCode(1001).__dict__,ensure_ascii=False))

def responseJson(dict):
    return HttpResponse(json.dumps(dict,ensure_ascii=False))