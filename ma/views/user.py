from django.shortcuts import render
from django.http import HttpResponse
from ma.beans.Error import Error
from ma.models import UserEntity
from ma.models import UserSession
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from utility import responseError
from utility import responseJson
import random


import json
# Create your views here.

@csrf_exempt
def userRegister(request):
    if request.method == 'POST':
        try:
            userName = request.POST['user_name']
            password = request.POST['password']
            realName = request.POST['real_name']
            gender = request.POST['gender']
            typeId = request.POST['type_id']
        except KeyError:
            return responseError(1001)

        try:
            UserEntity.objects.get(user_name = userName)
            return responseError(1003)
        except UserEntity.DoesNotExist:
            user = UserEntity(user_name=userName, password=password, gender = gender, real_name= realName, type_id=typeId)
            user.save()
            return HttpResponse(json.dumps({'result':True}))
    else:
        return responseError(1000)


@csrf_exempt
def userLogin(request):
    if request.method == 'POST':
        try:
            userName = request.POST['user_name']
            password = request.POST['password']
        except KeyError:
            return responseError(1001)

        try:
            user = UserEntity.objects.get(user_name = userName)
            if user.password == password:

                sessionId = random.randint(1, 65535)

                try:
                    while True:
                        UserSession.objects.get(id = sessionId)
                        sessionId = sessionId + 1
                except UserSession.DoesNotExist:
                    session = UserSession(id = sessionId, user=user)
                    session.updateExpireDate()
                    session.save()
                    return responseJson({"type_id":user.type_id, "session_id":session.id})
                session = UserSession(user=user)
                session.updateExpireDate()
                session.save()
                return responseJson({"type_id":user.type_id, "session_id":session.id})

            else:
                return responseError(1002)

        except UserEntity.DoesNotExist:
            return responseError(1002)
            pass
    else:
        return responseError(1000)


@csrf_exempt
def userLogout(request):
    if request.method == 'POST':
        try:
            sessionId = request['session_id']
        except KeyError:
            return responseError(1001)



    else:
        return responseError(1000)



@csrf_exempt
def userGetInfo(request):

    return HttpResponse("Hello World")
