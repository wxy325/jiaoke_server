__author__ = 'wxy325'
from ma.models import UserEntity
from django.views.decorators.csrf import csrf_exempt
from utility import *
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
            sessionId = request.POST['session_id']
        except KeyError:
            return responseError(1001)

        try:
            session = UserSession.objects.get(id = sessionId)
            session.delete()
        except UserSession.DoesNotExist:
            pass
        return responseSuccess()
    else:
        return responseError(1000)



@csrf_exempt
def userGetInfo(request):
    if request.method == 'POST':
        try:
            user = getUserFromRequest(request)
        except UserSession.DoesNotExist, UserSession.SessionExpireException:
            return responseError(1005)
        except KeyError:
            return responseError(1001)


        userDict = {key:user.__dict__[key] for key in ['user_name','real_name','gender','type_id']}
        return responseJson(userDict)
    else:
        return responseError(1000)

@csrf_exempt
def userUpdateInfo(request):
    if request.method == 'POST':
        try:
            user = getUserFromRequest(request)
        except UserSession.DoesNotExist, UserSession.SessionExpireException:
            return responseError(1005)
        except KeyError:
            return responseError(1001)


        try:
            realName = request.POST['real_name']
            user.real_name = realName
        except KeyError:
            pass

        try:
            gender = request.POST['gender']
            user.gender = gender
        except KeyError:
            pass

        user.save()
        return responseSuccess()
    else:
        return responseError(1000)
