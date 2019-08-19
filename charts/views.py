from django.shortcuts import render
from django.http import JsonResponse
from django.shortcuts import render
from django.views.generic import View
from dateutil import tz
from django.core.cache import cache
import json
import requests
import datetime
from django.conf import settings
from django.http import HttpResponse
from pytz import timezone


auth = {}

def get_access_token():
    try:
        # print("in get_access_token function ....")
        headers = {
            'Content-type': 'application/json',
        }
        data = {"grant_type": "client_credentials", "client_id": settings.CLIENT_ID,"client_secret": settings.CLIENT_SECRET}
        # print(json.dumps(data))
        r = requests.post(settings.API_DOMAIN, headers=headers, data=json.dumps(data))
        return r.json()
    except requests.exceptions.RequestException as e:  
        print("api connection error...")
    return {}


def get_refresh_token(refresh_token):
    try:
        # print("in refresh_token function ....")
        headers = {
            'Content-type': 'application/json',
        }
        data = {"grant_type": "refresh_token","refresh_token": refresh_token, "client_id": settings.CLIENT_ID,"client_secret": settings.CLIENT_SECRET}
        # print(json.dumps(data))
        r = requests.post(settings.API_DOMAIN, headers=headers, data=json.dumps(data))
        # print(r.json())
        return r.json()
    except requests.exceptions.RequestException as e:  
        print("api connection error...")
    return {}



def check_auth_token():
    global auth
    # check cache first
    access_token = cache.get('vea_access_token')
    # print("access token is : ",access_token)
    
    if access_token is None:
        refresh_token = cache.get('vea_refresh_token')
        # print("refresh token is : " , refresh_token)
        if refresh_token is None:
            auth = get_access_token()
        else:
            auth = get_refresh_token(refresh_token)
        
        if 'access_token' in auth.keys():
            access_token = auth['access_token']

        if access_token is not None: 
            # print("refresh token is : ", auth['refresh_token'])
            cache.set('vea_access_token', auth['access_token'], timeout=(int(auth['expires_in']) - 500))
            cache.set('vea_refresh_token', auth['refresh_token'])

    return True

class HomeView(View):
    check_auth_token()
    def get(self, request, *args, **kwargs):
        dv = ''
        if 'view' in request.GET :
            dv = request.GET['view']
        return render(request, 'charts/charts.html', {'detailview':dv})



def get_data(request, *args, **kwargs):
    query = request.GET['q']
    group = request.GET['g']
    f =''
    t =''
    z =''

    if 'z' in request.GET :
        z = request.GET['z']
    
    if query == 'custom':
        f = request.GET['f']
        t = request.GET['t']
    
    apidata = get_apidata(query,group,f,t)

    # print (f,t)
    if group == 'hour': #if today , also graph that has the “outs” subtracted from the “ins”
        outs = {}
        if z == 'ocp':
            outs = get_apidata('today',group,f,t,'outs')

        context = prepare_today(apidata,outs)
    else:
        context = prepare_monthly(apidata)

    return JsonResponse(context)



def prepare_today(ins, outs):
    # print('prepare_today....')
    today = {
        'labels' : [],
        'sumins': [],
    }
    outsflag = bool(outs)
    count = 0
    totalins = 0
    totalouts = 0
    for i in ins["results"]: 
            timestr = i['recordDate_hour_1'] 
            utc = datetime.datetime.strptime(timestr, "%Y-%m-%dT%H:%M:%S.%fZ")
            print(timestr)
            from_zone = tz.tzutc()
            to_zone = timezone('US/Eastern')
            utc = utc.replace(tzinfo=from_zone)
            east = utc.astimezone(to_zone)
            if east.hour >= 7 :
                l = east.strftime("%I%p")  
                today['labels'].append(l)
                totalins += int(i['sumins'])
                if outsflag :
                    o =outs['results'][count]
                    totalouts+=int(o['sumouts'])
                    cur = totalins - totalouts
                    today['sumins'].append(cur)
                else :
                    today['sumins'].append(int(i['sumins']))
            count +=1
    return today


def prepare_monthly(data):
    source = {
        'labels' : [],
        'sumins': [],
    }
    print(data)
    for i in data["results"]: 
            timestr = i['recordDate_day_1'] #only show the first campus info
            utc = datetime.datetime.strptime(timestr, "%Y-%m-%dT%H:%M:%S.%fZ")
            from_zone = tz.tzutc()
            to_zone = timezone('US/Eastern')
            utc = utc.replace(tzinfo=from_zone)
            east = utc.astimezone(to_zone)
            l = east.strftime("%m/%d")  
            source['labels'].append(l)
            source['sumins'].append(int(i['sumins']))
    print(source)
    return source

def get_apidata(relativedDate, dateGrouping, f ='',t ='', metrics='ins'):
    
    check_auth_token()
    headers = {
        'accept': 'application/json',
        'Authorization': auth['token_type'] + ' ' + auth['access_token'],
    }

    params = (
        ('relativeDate', relativedDate),
        ('dateGroupings', dateGrouping),
        ('startDate', f),
        ('endDate', t),
        ('entityType', 'location'),
        ('excludeClosedHours', 'true'),
        ('metrics', metrics),
    )
    print (params)
    response = requests.get('https://vea.sensourceinc.com/api/data/traffic', headers=headers, params=params)
    print(response.status_code)
    print(response.json())
    return response.json()


def timeconvert(timestr):
    # Create datetime objects
    d0 = datetime.datetime.strptime(timestr, "%Y-%m-%dT%H:%M:%S.%fZ")
    d1 = datetime.datetime.now() # Current time

