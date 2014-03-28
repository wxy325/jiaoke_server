#coding=utf-8

import urllib
import urllib2
import json


def getDistanceWithLocation(locationFrom, locationTo, locationPass=()):
    param = {}
    param['origin'] = locationFrom.__unicode__()
    param['destination'] = locationTo.__unicode__()
    param['mode'] = 'driving'
    param['origin_region'] = '上海'
    param['destination_region'] = '上海'
    param['output'] = 'json'
    param['ak'] = 'jeszhojTR7sZSeF0RHwitYiN'

    if len(locationPass):
        paramStr = ''

        i = 0
        for l in locationPass:
            if i != 0:
                paramStr = paramStr + '|'
            paramStr = paramStr + l.__unicode__()

        param['waypoints'] = paramStr

    url_values = urllib.urlencode(param)

    url = 'http://api.map.baidu.com/direction/v1'
    full_url = url + '?' + url_values
    response = urllib2.urlopen(full_url)
    data = response.read()


    jsonDict = json.loads(data)


    try:
        routes = jsonDict['result']['routes'][0]['distance']
    except IndexError:
        routes = 99999999999999
    return routes
