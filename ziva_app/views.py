import base64
import json
import re
import math
import random
import string
from django.db.models import Sum, F, ExpressionWrapper, IntegerField

from collections import defaultdict
from django.views.decorators.cache import never_cache
from django.contrib.auth import logout as auth_logout
from datetime import datetime,timedelta
from itertools import groupby
import paytmchecksum
from django.forms import IntegerField, DecimalField
from django.views.decorators.cache import cache_control
from django.db.models import DateTimeField, Sum, F, CharField, Value, OuterRef, Subquery, Case, When, Q, Count, Func
import datetime
import geocoder as geocoder

from django.shortcuts import render, HttpResponse, redirect
from django.urls import reverse
from django.db.models.functions import Cast, Round
import requests
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from ziva_app.models import *
from django.db.models import Sum
from django.contrib.auth import logout


class BytesEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, bytes):
            return obj.decode('utf-8')
        return json.JSONEncoder.default(self, obj)


# Create your views here.

@login_required
def index(request):
    return render(request,'base.html')

@csrf_exempt
def login(request):

    if request.method == 'POST':
        url = "http://13.235.112.1/ziva/mobile-api/login.php"
        payload = json.dumps({
            "username": request.POST.get('Username'),
            "password": request.POST.get('Password'),
            "osversion": "12",
            "udid": "80e15017be845772",
            "tokenid": "test"
        })
        headers = {
        'Content-Type': 'application/json'
        }
        response = requests.request("GET", url, headers=headers, data=payload)
        if response.status_code == 200:
            data = response.json()
            role = data['role']
            name=data['name']
            displayrole = data['displayrole']
            deponame = data['deponame']
            depoid = data['depoid']
            accesskey = data['accesskey']
            username = data['username']
            warehousename = data['warehousename']
            code = data['code']
            regionid = data['regionid']
            region = data['region']
            warehouseid = data['warehouseid']
            request.session['name'] = name
            request.session['displayrole'] = displayrole
            request.session['accesskey'] = accesskey
            request.session['username'] = username
            request.session['role'] = role
            request.session['deponame']=deponame
            request.session['depoid'] = depoid
            request.session['codee'] = code
            request.session['regionid'] = regionid
            request.session['region'] = region
            request.session['warehousename'] = warehousename
            request.session['warehouseid'] = warehouseid

            url = "http://13.235.112.1/ziva/mobile-api/sidemenu-permissions.php"

            payload = json.dumps({

                  "accesskey": accesskey
            })
            headers = {
                'Content-Type': 'application/json'
            }
            response = requests.request("GET", url, headers=headers, data=payload)
            data1 = response.json()
            menuname = data1['mylist']
            request.session['mylist'] = menuname
            context = {'menuname':menuname}
            #sidebar_items = {'submenu':submenu,'weblinks':weblinks}
            messages.success(request,data['message'])
            if role == 'Admin':
                return redirect('/depot_dashboard')
            elif role == "Warehouse":
                return redirect('/zonal_dashboard')
            elif role == 'Bus Station' and displayrole == 'DC CONTROLLER':
                return redirect('/internal_consumption')
            elif displayrole == 'REGIONAL MANAGER':
                return redirect('/intconsump_dashboard')
            elif role == 'Bus Station':
                return redirect('/bust_dashboard')
            elif role ==  "Depo":
                return redirect('/depot_dashboard')
            elif displayrole == "MARKETING EXECUTIVE":
                return redirect('/store_master')
        else:
            try:
                data = response.json()
                messages.error(request, data['message'])
            except:
                messages.error(request,response.text)
            return redirect('/login')
    return render(request, 'login1.html')


@never_cache
def signout(request):
    del request.session['accesskey']
    request.session.flush()
    return redirect('/login')


def location_map(request,id):
    latitude, longitude = map(float, id.split(','))
    return render(request, 'location.html',{'latitude': latitude, 'longitude': longitude})


def store_master(request):
    if 'accesskey' not in request.session:
        return redirect('/login')
    try:
        menuname = request.session['mylist']
        role = request.session['role']
        if role == 'Admin':
            accesskey  = request.session['accesskey']
            url = "http://13.235.112.1/ziva/mobile-api/warehousemaster-list.php"

            payload = json.dumps({"accesskey": accesskey})
            headers = {
                'Content-Type': 'text/plain'
            }
            response = requests.request("GET", url, headers=headers, data=payload)

            data = response.json()
            wh_masterlist = data['warehouselist']

            url = "http://13.235.112.1/ziva/mobile-api/dropdwn-table-list.php"

            payload = json.dumps({"accesskey": accesskey, "name": "Storetype"})
            headers = {
                'Content-Type': 'text/plain'
            }

            response = requests.request("GET", url, headers=headers, data=payload)

            data = response.json()
            storetype_list = data['itemmasterlist']

            if request.method == 'POST':

                url = "http://13.235.112.1/ziva/mobile-api/adminstoremaster-list.php"

                payload = json.dumps({
                    "accesskey": accesskey,
                    "warehouseid": request.POST.get('warehouseid'),
                    "regionid": request.POST.get('regionid'),
                    "depoid": request.POST.get('depoid'),
                    "busstationid": request.POST.get('busstationid')
                })
                headers = {
                    'Content-Type': 'application/json'
                }

                response = requests.request("GET", url, headers=headers, data=payload)
                if response.status_code == 200:
                    data = response.json()
                    store_masterlist = data['adminstoremasterlistdata']
                    return render(request, 'masters/store_master_Sub_list.html', {"list": store_masterlist,'wh_masterlist':wh_masterlist,'storetype_list':storetype_list,'menuname':menuname})
                else:
                    return render(request, 'masters/store_master_Sub_list.html',
                                  {'wh_masterlist': wh_masterlist, 'storetype_list': storetype_list,'menuname':menuname})
            else:

                    url = "http://13.235.112.1/ziva/mobile-api/adminstoremaster-list.php"

                    payload = json.dumps({
                        "accesskey": accesskey,
                        "warehouseid": 'All',
                        "regionid": 'All',
                        "depoid": 'All',
                        "busstationid": 'All'

                    })
                    headers = {
                        'Content-Type': 'application/json'
                    }
                    response = requests.request("GET", url, headers=headers, data=payload)
                    if response.status_code == 200:
                        data = response.json()
                        store_masterlist = data['adminstoremasterlistdata']
                        return render(request, 'masters/store_master_Sub_list.html', {'wh_masterlist': wh_masterlist,'storetype_list':storetype_list,'list':store_masterlist,'menuname':menuname})
                    else:
                        return render(request, 'masters/store_master_Sub_list.html',
                                      {'wh_masterlist': wh_masterlist, 'storetype_list': storetype_list,'menuname':menuname})
        else:
                accesskey = request.session['accesskey']
                url = "http://13.235.112.1/ziva/mobile-api/warehousemaster-list.php"

                payload = json.dumps({"accesskey": accesskey})
                headers = {
                    'Content-Type': 'text/plain'
                }
                response = requests.request("GET", url, headers=headers, data=payload)

                data = response.json()
                wh_masterlist = data['warehouselist']

                url = "http://13.235.112.1/ziva/mobile-api/dropdwn-table-list.php"

                payload = json.dumps({"accesskey": accesskey, "name": "Storetype"})
                headers = {
                    'Content-Type': 'text/plain'
                }

                response = requests.request("GET", url, headers=headers, data=payload)

                data = response.json()
                storetype_list = data['itemmasterlist']

                url = "http://13.235.112.1/ziva/mobile-api/store-master-list.php"

                payload = json.dumps({
                    "accesskey": accesskey
                })
                headers = {
                    'Content-Type': 'application/json'
                }

                response = requests.request("GET", url, headers=headers, data=payload)
                if response.status_code == 200:
                    data = response.json()
                    store_masterlist = data['storemasterlist']
                    return render(request, 'masters/store_master_list.html',
                                  {"list": store_masterlist, 'wh_masterlist': wh_masterlist,
                                   'storetype_list': storetype_list,'menuname':menuname})
                else:
                    return render(request, 'masters/store_master_list.html',
                                  {'wh_masterlist': wh_masterlist, 'storetype_list': storetype_list,'menuname':menuname})
    except:

        return render(request,'login1.html')



def get_store(request):
    if 'accesskey' not in request.session:
        return redirect('/login')
    accesskey = request.session['accesskey']
    id = request.POST.get('id')
    url = "http://13.235.112.1/ziva/mobile-api/store-master-list.php"

    payload = json.dumps({
        "accesskey": accesskey
    })
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    if response.status_code == 200:
        data = response.json()
        store_masterlist = data['storemasterlist']
        for i in store_masterlist:
            if str(i['storecode']) == id:
                data = {"storecode": i["storecode"], "storename": i["storename"], "legal_name": i["legal_name"],
                        "contact_person": i['contact_person'], "mobile_no": i['mobile_no'], "pancard": i['pancard'],
                        "gstnumber": i['gstnumber'], "tradelicenceno": i['tradelicenceno'],"foodlicence": i["foodlicence"],
                        "storeaddress": i["storeaddress"], "pincode": i["pincode"], "remarks": i["remarks"],"storelocation": i["storelocation"],
                        "state": i["state"],"bus_station": i["bus_station"],"busstation_id": i["busstation_id"],"depoid": i["depoid"],"depo": i["depo"],
                        "warehouse": i["warehouse"],"warehouseid": i["warehouseid"],"email":i["email"],"region":i['region'],"regionid":i['regionid'],
                        "alternate_mobileno":i['alternate_mobileno' ],"natureofbusiness":i['natureofbusiness'],'storetype':i['storetype']}

        return JsonResponse({'data': data})
    else:
        try:
            data = response.json()
            messages.error(request,data['message'])
        except:
            messages.error(request,response.text)
        return redirect('/add_store')

def add_store(request):
    if 'accesskey' not in request.session:
        return redirect('/login')
    try:

        menuname = request.session['mylist']
        g = geocoder.ip('me', user_agent='http')
        latlng = g.latlng
        lat = latlng[0]
        lng = latlng[1]
        accesskey = request.session['accesskey']

        url = "http://13.235.112.1/ziva/mobile-api/warehousemaster-list.php"

        payload = json.dumps({"accesskey": accesskey})
        headers = {
            'Content-Type': 'text/plain'
        }
        response = requests.request("GET", url, headers=headers, data=payload)

        data = response.json()
        wh_masterlist = data['warehouselist']

        url = "http://13.235.112.1/ziva/mobile-api/dropdwn-table-list.php"

        payload = json.dumps({"accesskey": accesskey, "name": "Storetype"})
        headers = {
            'Content-Type': 'text/plain'
        }

        response = requests.request("GET", url, headers=headers, data=payload)

        data = response.json()
        storetype_list = data['itemmasterlist']

        if request.method == "POST":
            gstattach = request.FILES.get("gstattach")
            panattach = request.FILES.get("panattach")
            tlattach = request.FILES.get("tlattach")
            storephoto = request.FILES.get("storephoto")

            if gstattach:
                gstattach_data = base64.b64encode(gstattach.read())
                gstattach_name = request.FILES.get("gstattach").name

            else:
                gstattach_data = None
                gstattach_name = None

            if panattach:
                panattach_data = base64.b64encode(panattach.read())
                panattach_name = request.FILES.get("panattach").name
            else:
                panattach_data = None
                panattach_name = None

            if tlattach:
                tlattach_data = base64.b64encode(tlattach.read())
                tlattach_name = request.FILES.get("tlattach").name
            else:
                tlattach_data = None
                tlattach_name= None

            if storephoto:
                storephoto_data = base64.b64encode(storephoto.read())
                storephoto_name = request.FILES.get("storephoto").name
            else:
                storephoto_data = None
                storephoto_name = None

            url = "http://13.235.112.1/ziva/mobile-api/add-storemaster.php"
            payload = {
                'accesskey': accesskey,
                "storename": request.POST.get("storename"),
                'storeattachfilename':storephoto_name,
                "storecodeid":request.POST.get('stallcode'),
                'storephoto': storephoto_data ,
                'legalname': request.POST.get("legalname"),
                "depo":request.POST.get("deponame"),
                "depoid": request.POST.get("depoid"),
                "region": request.POST.get("regionname"),
                "regionid":request.POST.get("regionid"),
                "warehouse":request.POST.get("warehousename"),
                "warehouseid":request.POST.get("warehouseid"),
                "busstationname": request.POST.get("busstationname"),
                "busstationid": request.POST.get("busstationid"),
                'gstnumber': request.POST.get("gstnumber"),
                'gstattachfilename':  gstattach_name,
                'pancard': request.POST.get("pancard"),
                'panattachfilename': panattach_name,
                'tradelicenceno': request.POST.get("tradelicenceno"),
                'tlattachfilename':tlattach_name,
                'storelocation': str(lat)+","+str(lng),
                'emailid': request.POST.get("email"),
                'storeaddress': request.POST.get("storeaddress"),
                'pincode': request.POST.get("pincode"),
                'state': request.POST.get('state'),
                'contactperson': request.POST.get("contactperson"),
                'mobileno': request.POST.get("mobile"),
                'remarks': request.POST.get("remarks"),
                'natureofbusiness':request.POST.get('natofbus'),
                'storetype': request.POST.get('store_type'),
                'alternatemobileno': request.POST.get('altmobileno'),
                'gstattach': gstattach_data,
                'panattach': panattach_data,
                'tlattach': tlattach_data,

            }
            payload = json.dumps(payload, cls=BytesEncoder)
            headers = {
                'Content-Type': 'application/json'
            }
            r = requests.post(url, payload, headers=headers)
            if r.status_code == 200:
                data = r.json()
                messages.success(request, data['message'])
                return redirect('store_master')
            else:
                try:
                    data = r.json()
                    messages.error(request, data['message'])
                    return redirect('store_master')
                except:
                    messages.error(request,response.text)
                    return redirect('store_master')
        else:
            return render(request, 'masters/store_master_add.html', {'warehouse': wh_masterlist,'data':storetype_list,'menuname':menuname})
    except:
        return render(request,'login1.html')

def store_edit(request):
    if 'accesskey' not in request.session:
        return redirect('/login')
    accesskey = request.session['accesskey']
    if request.method == "POST":
                url = "http://13.235.112.1/ziva/mobile-api/edit-storemaster.php"
                payload =json.dumps( {
                    "storecode": request.POST.get("stcode"),
                    'accesskey':accesskey,
                    "storename": request.POST.get("storename"),
                    'legalname': request.POST.get("legalname"),
                    'gstnumber': request.POST.get("gstnumber"),
                    'pancard': request.POST.get("pancard"),
                    "depo": request.POST.get("deponame1"),
                    "regionid":request.POST.get("regionid1"),
                    "region": request.POST.get("regionname1"),
                    "depoid":request.POST.get("depoid1"),
                    "warehouse": request.POST.get("warehousename1"),
                    "warehouseid": request.POST.get("warehouseid1"),
                    "busstationname":request.POST.get("busstationname1"),
                    "busstationid":request.POST.get("busstationid1"),
                    'foodlicence': request.POST.get("foodlicence"),
                    'tradelicenceno': request.POST.get("tradelicenceno"),
                    'storelocation': request.POST.get("storelocation"),
                    'emailid': request.POST.get("email"),
                    'storeaddress': request.POST.get("storeaddress"),
                    'pincode': request.POST.get("pincode"),
                    'state': request.POST.get('state'),
                    'contactperson': request.POST.get("contactperson"),
                    'mobileno': request.POST.get("mobileno"),
                    'remarks': request.POST.get("remarks"),
                    'natureofbusiness':request.POST.get('natofbus1'),
                    'storetype': request.POST.get('store_type1'),
                    'alternatemobileno': request.POST.get('mobileno2'),


                })
                headers = {
                    'Content-Type': 'application/json'
                }
                r = requests.post(url, payload, headers=headers)
                if r.status_code == 200:
                    data = r.json()
                    messages.success(request, data['message'])
                    return redirect('/store_master')
                elif response.status_code == 400:
                    data = response.json()
                    if data['message'] == 'Sorry! some details are missing':
                        messages.error(request, data['message'])
                        return redirect('/store_master')
                    else:
                        messages.error(request, data['message'])
                        return redirect('/login')
                else:
                    try:
                        r = response.json()
                        messages.error(request, r['message'])
                    except:
                        messages.error(request, response.text)
                    return redirect('/store_master')
    return redirect('/store_master')

def store_status_active(request):
    if 'accesskey' not in request.session:
        return redirect('/login')
    accesskey = request.session['accesskey']
    url = "http://13.235.112.1/ziva/mobile-api/status-change.php"

    payload = json.dumps({
        "accesskey": accesskey,
        "sno": request.POST.get('id'),
        "type": "Storemaster",
        "status": "Inactive"
    })
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    if response.status_code == 200:
        data = response.json()
        messages.success(request, data['message'])
        return redirect('store_master')
    else:
        try:
            data = response.json()
            messages.error(request, data['message'])
            return redirect('store_master')
        except:
            messages.error(request,response.text)
        return redirect('store_master')



def store_status_inactive(request, id):
    if 'accesskey' not in request.session:
        return redirect('/login')
    accesskey = request.session['accesskey']
    url = "http://13.235.112.1/ziva/mobile-api/status-change.php"

    payload = json.dumps({
        "accesskey": accesskey,
        "sno": id,
        "type": "Storemaster",
        "status": "Active"
    })
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    data = response.json()
    if response.status_code == 200:
        messages.success(request, data['message'])
        return redirect('store_master')
    else:
        messages.error(request, data['message'])
        return redirect('store_master')

def item_add(request):
    if 'accesskey' not in request.session:
        return redirect('/login')
    try:
        menuname = request.session['mylist']
        accesskey = request.session['accesskey']
        url = "http://13.235.112.1/ziva/mobile-api/dropdwn-table-list.php"
        payload=json.dumps({
            "accesskey":accesskey,
            "name":"UOM"
        })
        headers = {
            'Content-Type': 'application/json'
        }

        response = requests.request("GET", url, headers=headers, data=payload)
        if response.status_code == 200:
            response = response.json()
            uom = response['itemmasterlist']

        url = "http://13.235.112.1/ziva/mobile-api/dropdwn-table-list.php"
        payload = json.dumps({
            "accesskey": accesskey,
            "name": "CATEGORY"
        })
        headers = {
            'Content-Type': 'text/plain'
        }

        response1 = requests.request("GET", url, headers=headers, data=payload)
        response1 = response1.json()
        category = response1['itemmasterlist']


        if request.method == "POST":
            image = request.FILES.get("imagefile")
            if image:
                image_data = base64.b64encode(image.read())
            else:
                image_data = None

            url = "http://13.235.112.1/ziva/mobile-api/add-item-master.php"
            payload = {

                "accesskey":accesskey ,
                "itemname": request.POST.get('name'),
                "hsncode": request.POST.get('hsncode'),
                "lpp": "",
                "gst": request.POST.get("gst"),
                "category": request.POST.get('category'),
                "mrp": request.POST.get('mrp'),
                "manufacturername": request.POST.get('manufacture'),
                "uom": request.POST.get('uom'),
                "item_code":request.POST.get('code'),
                "image": image_data,
            }
            payload = json.dumps(payload, cls=BytesEncoder)
            headers = {
                'Content-Type': 'application/json'
            }
            r = requests.post(url, payload, headers=headers)
            if r.status_code == 200:
                data = r.json()
                messages.success(request, data['message'])
                return redirect('item_master')
            else:
                try:
                    data = r.json()
                    messages.error(request, data['message'])
                except:
                    messages.error(request,response.text)
                return redirect('item_master')

        else:

            return render(request, 'Item_master/item_add.html', {'uom_data': uom, 'cat_data': category,'menuname':menuname})
    except:
        if response.status_code == 400:
            messages.error(request,data['message'])
            return redirect('/login')
    return render(request, 'Item_master/item_add.html')
def storetype_list(request):
    if 'accesskey' not in request.session:
        return redirect('/login')
    menuname = request.session['mylist']
    accesskey = request.session['accesskey']
    url = "http://13.235.112.1/ziva/mobile-api/dropdwn-table-list.php"

    payload = json.dumps({"accesskey": accesskey, "name": "Storetype"})
    headers = {
        'Content-Type': 'text/plain'
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    if response.status_code == 200:
        data = response.json()
        storetype_list = data['itemmasterlist']
        return render(request, 'category_master/storetype_list.html', {"all_data": storetype_list,'menuname':menuname})
    else:
        try:
            data = response.json()
            return render(request, 'category_master/storetype_list.html',{'menuname':menuname})
        except:
            messages.error(request, response.text)
        return render(request, 'category_master/storetype_list.html',{'menuname':menuname})
def item_list(request):
    if 'accesskey' not in request.session:
        return redirect('/login')
    try:
        menuname = request.session['mylist']
        accesskey = request.session['accesskey']

        url = "http://13.235.112.1/ziva/mobile-api/dropdwn-table-list.php"
        payload = json.dumps({
            "accesskey": accesskey,
            "name": "UOM"
        })
        headers = {
            'Content-Type': 'application/json'
        }

        response = requests.request("GET", url, headers=headers, data=payload)
        data = response.json()
        uom = data['itemmasterlist']

        url = "http://13.235.112.1/ziva/mobile-api/dropdwn-table-list.php"
        payload = json.dumps({
            "accesskey": accesskey,
            "name": "CATEGORY"
        })
        headers = {
            'Content-Type': 'text/plain'
        }

        response1 = requests.request("GET", url, headers=headers, data=payload)
        response1 = response1.json()
        category = response1['itemmasterlist']

        url = "http://13.235.112.1/ziva/mobile-api/itemmaster-list.php"

        payload = json.dumps({"accesskey":accesskey})
        headers = {
            'Content-Type': 'application/json'
        }
        response = requests.request("GET", url, headers=headers, data=payload)
        if response.status_code == 200:
            data = response.json()
            item_masterlist = data['itemmasterlist']
            return render(request, 'Item_master/item_list.html', {'all_data': item_masterlist,'category':category,'uom':uom,'menuname':menuname})
        else:
            return render(request, 'Item_master/item_list.html',{'menuname':menuname})
    except:
        if response.status_code == 400:
            messages.error(request,data['message'])
            return render(request,'login1.html')
    return render(request, 'Item_master/item_list.html',{'menuname':menuname})

def item_status_active(request):
    if 'accesskey' not in request.session:
        return redirect('/login')
    try:
        accesskey = request.session['accesskey']
        url = "http://13.235.112.1/ziva/mobile-api/status-change.php"

        payload = json.dumps({
            "accesskey": accesskey,
            "sno":request.POST.get('id'),
            "type": "Itemmaster",
            "status": "Inactive"
        })
        headers = {
            'Content-Type': 'application/json'
        }

        response = requests.request("POST", url, headers=headers, data=payload)

        if response.status_code == 200:
            data = response.json()
            messages.success(request, data['message'])
            return redirect('item_master')
        else:
            try:
                data = response.json()
                messages.error(request, data['message'])
                return redirect('item_master')
            except:
                messages.error(request,response.text)
            return redirect('item_master')
    except:
        if response.status_code == 400:
            data = response.json()
            messages.error(request, data['message'])
            return redirect('/login')
    return redirect('item_master')


def item_status_inactive(request):
    if 'accesskey' not in request.session:
        return redirect('/login')
    accesskey = request.session['accesskey']
    url = "http://13.235.112.1/ziva/mobile-api/status-change.php"

    payload = json.dumps({
        "accesskey":accesskey,
        "sno": request.POST.get('id'),
        "type": "Itemmaster",
        "status": "Active"
    })
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    if response.status_code == 200:
        data = response.json()
        messages.success(request, data['message'])
        return redirect('item_master')
    elif response.status_code == 400:
        data = response.json()
        messages.error(request, data['message'])
        return redirect('/login')
    else:
        try:
            data = response.json()
            messages.error(request, data['message'])
            return redirect('item_master')
        except:
            messages.error(request, data['message'])
        return redirect('item_master')




def des_add(request):
    if 'accesskey' not in request.session:
        return redirect('/login')
    try:
        menuname = request.session['mylist']
        accesskey = request.session['accesskey']

        payload = json.dumps({"accesskey": accesskey})
        headers = {
            'Content-Type': 'application/json'
        }
        url = "http://13.235.112.1/ziva/mobile-api/region-list.php"
        response = requests.request("POST", url, headers=headers, data=payload)
        #if response.status_code == 200:
        data = response.json()
        regionlist = data['regionlist']

        url = "http://13.235.112.1/ziva/mobile-api/itemmaster-list.php"

        payload = json.dumps({"accesskey": accesskey})
        headers = {
            'Content-Type': 'application/json'
        }
        response = requests.request("GET", url, headers=headers, data=payload)

        data = response.json()
        item_masterlist = data['itemmasterlist']

        if request.method == 'POST':

            url = "http://13.235.112.1/ziva/mobile-api/addpricemaster.php"

            payload = {
                "accesskey":accesskey,
                "regionname":  request.POST.get('regionnmae'),
                "regioncode":  request.POST.get('regionid'),
                "itemcode":  request.POST.get('itemid'),
                "itemname":  request.POST.get('itemname'),
                "mrp":  request.POST.get('amount'),
            }
            headers = {
                'Content-Type': 'text/plain'
            }
            payload = json.dumps(payload, cls=BytesEncoder)
            response = requests.request("POST", url, data=payload, headers=headers)
            if response.status_code == 200:
                r = response.json()
                messages.success(request, r['message'])
                return redirect('des_list')
            else:
                try:
                    r = response.json()
                    messages.error(request, r['message'])
                except:
                    messages.error(request, response.text)
            return render(request, 'masters/pricemaster.html',{'regionlist':regionlist,'item_masterlist':item_masterlist,'menuname':menuname})
        return render(request, 'masters/pricemaster.html',{'regionlist':regionlist,'item_masterlist':item_masterlist,'menuname':menuname})
    except:
        if response.status_code == 400:
            messages.error(request,data['message'])
            return render(request,'login1.html')
    messages.error(request,response.text)
    return render(request,'masters/pricemaster.html',{'menuname':menuname})



def role(request):
    if 'accesskey' not in request.session:
        return redirect('/login')
    menuname = request.session['mylist']
    accesskey = request.session['accesskey']
    if request.method == 'POST':

        url = "http://13.235.112.1/ziva/mobile-api/addmasterdata.php"

        payload = json.dumps({
            "accesskey": accesskey,
            "type": "ROLE",
            "value": request.POST.get('role'),
        })
        headers = {
            'Content-Type': 'text/plain'
        }
        response = requests.request("POST", url, data=payload, headers=headers)
        if response.status_code == 200:
            r = response.json()
            messages.success(request, r['message'])
            return redirect('role_list')
        else:
            try:

                r = response.json()
                messages.error(request, r['message'])
                return render(request, 'category_master/df.html', {"role": "active","menuname":menuname})
            except:
                messages.error(request,response.text)
            return render(request, 'category_master/df.html', {"role": "active","menuname":menuname})
    return render(request, 'category_master/df.html', {"role": "active","menuname":menuname})


def level(request):
    if 'accesskey' not in request.session:
        return redirect('/login')
    accesskey = request.session['accesskey']
    menuname = request.session['mylist']
    if request.method == 'POST':

        url = "http://13.235.112.1/ziva/mobile-api/addmasterdata.php"

        payload = {
            "accesskey": accesskey,
            "type": "LEVEL",
            "value": request.POST.get('level'),
        }
        headers = {
            'Content-Type': 'text/plain'
        }
        payload = json.dumps(payload, cls=BytesEncoder)
        response = requests.request("POST", url, data=payload, headers=headers)


        if response.status_code == 200:
            r = response.json()
            messages.success(request, r['message'])
            return redirect('level_list')
        elif response.status_code == 400:
            data = response.json()
            if data['message'] == 'Sorry! some details are missing':
                messages.error(request, data['message'])
                return render(request, 'category_master/df.html', {"level": "active", "menuname": menuname})
            else:
                messages.error(request, data['message'])
                return redirect('/login')
        else:
            try:
                r = response.json()
                messages.error(request, r['message'])
            except:
                messages.error(request,response.text)
            return render(request, 'category_master/df.html',{"level": "active","menuname":menuname})
    return render(request, 'category_master/df.html',{"level": "active","menuname":menuname})


def city(request):
    if 'accesskey' not in request.session:
        return redirect('/login')
    menuname = request.session['mylist']
    accesskey = request.session['accesskey']
    if request.method == 'POST':

        url = "http://13.235.112.1/ziva/mobile-api/addmasterdata.php"

        payload = {
            "accesskey": accesskey,
            "type": "CITY",
            "value": request.POST.get('city'),
        }
        headers = {
            'Content-Type': 'text/plain'
        }
        payload = json.dumps(payload, cls=BytesEncoder)
        response = requests.request("POST", url, data=payload, headers=headers)
        if response.status_code == 200:
            r = response.json()
            messages.success(request, r['message'])
            return redirect('city_list')
        else:
            try:
                r = response.json()
                messages.error(request, r['message'])
                return render(request, 'category_master/df.html', {"city": "active","menuname":menuname})
            except:
                    messages.error(request,response.text)
            return render(request, 'category_master/df.html', {"city": "active","menuname":menuname})
    return render(request, 'category_master/df.html', {"city": "active","menuname":menuname})

def state(request):
    if 'accesskey' not in request.session:
        return redirect('/login')
    menuname = request.session['mylist']
    accesskey = request.session['accesskey']
    if request.method == 'POST':
        url = "http://13.235.112.1/ziva/mobile-api/addmasterdata.php"

        payload = {
            "accesskey":accesskey,
            "type": "STATE",
            "value": request.POST.get('state'),
        }
        headers = {
            'Content-Type': 'text/plain'
        }
        payload = json.dumps(payload, cls=BytesEncoder)
        response = requests.request("POST", url, data=payload, headers=headers)

        if response.status_code == 200:
            r = response.json()
            messages.success(request, r['message'])
            return redirect('state_list')
        else:
            try:
                r = response.json()
                messages.error(request, r['message'])
                return render(request, 'category_master/df.html', {"state": "active",'menuname':menuname})
            except:
                messages.error(request,response.text)
        return render(request, 'category_master/df.html', {"state": "active",'menuname':menuname})
    return render(request, 'category_master/df.html', {"state": "active",'menuname':menuname})


def uom(request):
    if 'accesskey' not in request.session:
        return redirect('/login')
    menuname = request.session['mylist']
    accesskey = request.session['accesskey']
    if request.method == 'POST':

        url = "http://13.235.112.1/ziva/mobile-api/addmasterdata.php"

        payload = {
            "accesskey": accesskey,
            "type": "UOM",
            "value": request.POST.get('uom'),
        }
        headers = {
            'Content-Type': 'text/plain'
        }
        payload = json.dumps(payload, cls=BytesEncoder)
        response = requests.request("POST", url, data=payload, headers=headers)
        if response.status_code == 200:
            r = response.json()
            messages.success(request, r['message'])
            return redirect('uom_list')
        else:
            try:
                r = response.json()
                messages.error(request, r['message'])
            except:
                messages.error(request,response.text)
        return render(request, 'category_master/df.html', {"uom": "active",'menuname':menuname})
    return render(request, 'category_master/df.html', {"uom": "active",'menuname':menuname})


def storetype(request):
    if 'accesskey' not in request.session:
        return redirect('/login')
    menuname = request.session['mylist']
    accesskey = request.session['accesskey']
    if request.method == 'POST':

        url = "http://13.235.112.1/ziva/mobile-api/addmasterdata.php"

        payload = {
            "accesskey": accesskey,
            "type": "Storetype",
            "value": request.POST.get('stotetype'),
        }
        headers = {
            'Content-Type': 'text/plain'
        }
        payload = json.dumps(payload, cls=BytesEncoder)
        response = requests.request("POST", url, data=payload, headers=headers)
        if response.status_code == 200:
            r = response.json()
            messages.success(request, r['message'])
            return redirect('storetype_list')
        else:
            try:
                r = response.json()
                messages.error(request, r['message'])
                return render(request, 'category_master/df.html', {"storetype": "active",'menuname':menuname})
            except:
                messages.error(request,response.text)
            return render(request, 'category_master/df.html', {"storetype": "active",'menuname':menuname})
    else:
        return render(request, 'category_master/df.html', {"storetype": "active",'menuname':menuname})



def gst(request):
    if 'accesskey' not in request.session:
        return redirect('/login')
    menuname = request.session['mylist']
    accesskey = request.session['accesskey']
    if request.method == 'POST':

        url = "http://13.235.112.1/ziva/mobile-api/addmasterdata.php"

        payload = {
            "accesskey": accesskey,
            "type": "GST",
            "value": request.POST.get('gst'),
        }
        headers = {
            'Content-Type': 'text/plain'
        }
        payload = json.dumps(payload, cls=BytesEncoder)
        response = requests.request("POST", url, data=payload, headers=headers)
        if response.status_code == 200:
            r = response.json()
            messages.success(request, r['message'])
            return redirect('gst_list')
        else:
            try:
                r = response.json()
                messages.error(request, r['message'])
            except:
                messages.error(request, response.text)
            return render(request, 'category_master/df.html', {"gst": "active",'menuname':menuname})
    return render(request, 'category_master/df.html', {"gst": "active",'menuname':menuname})


def category(request):
    if 'accesskey' not in request.session:
        return redirect('/login')
    menuname = request.session['mylist']
    accesskey = request.session['accesskey']
    if request.method == 'POST':

        url = "http://13.235.112.1/ziva/mobile-api/addmasterdata.php"

        payload = json.dumps({
            "accesskey":   accesskey,
            "type": "CATEGORY",
            "value": request.POST.get('category'),
        })
        headers = {
            'Content-Type': 'text/plain'
        }
        response = requests.request("POST", url, data=payload, headers=headers)
        if response.status_code == 200:
            r = response.json()
            messages.success(request, r['message'])
            return redirect('category_list')
        else:
            try:
                r = response.json()
                messages.error(request, r['message'])
            except:
                messages.error(request, response.text)
            return render(request, 'category_master/df.html', {"category": "active",'menuname':menuname})
    return render(request, 'category_master/df.html', {"category": "active",'menuname':menuname})


def role_list(request):
    if 'accesskey' not in request.session:
        return redirect('/login')
    menuname = request.session['mylist']
    accesskey = request.session['accesskey']
    url = "http://13.235.112.1/ziva/mobile-api/dropdwn-table-list.php"

    payload = json.dumps({"accesskey":accesskey,"name":"ROLE"})
    headers = {
        'Content-Type': 'text/plain'
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    if response.status_code == 200:
        data = response.json()
        role_list = data['itemmasterlist']
        return render(request, 'category_master/role_list.html', {"all_data": role_list,'menuname':menuname})
    elif response.status_code == 400:
        data = response.json()
        messages.error(request, data['message'])
        return render(request, 'login1.html')
    else:
        try:
            data = response.json()
            return render(request, 'category_master/role_list.html',{'menuname':menuname})
        except:
            messages.error(request, response.text)
        return render(request, 'category_master/role_list.html',{'menuname':menuname})


def level_list(request):
    if 'accesskey' not in request.session:
        return redirect('/login')
    menuname = request.session['mylist']
    accesskey = request.session['accesskey']
    url = "http://13.235.112.1/ziva/mobile-api/dropdwn-table-list.php"

    payload = json.dumps({"accesskey":accesskey,"name":"LEVEL"})
    headers = {
        'Content-Type': 'text/plain'
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    if response.status_code == 200:
        data = response.json()
        level_list = data['itemmasterlist']
        return render(request, 'category_master/level_list.html', {"all_data": level_list,'menuname':menuname})
    elif response.status_code == 400:
        data = response.json()
        if data['message'] == 'Sorry! some details are missing':
            messages.error(request, data['message'])
            return render(request, 'category_master/level_list.html', {'menuname': menuname})
        else:
            messages.error(request, data['message'])
            return redirect('/login')
    else:
        try:
            data = response.json()
            messages.error(request, data['message'])
            return render(request, 'category_master/level_list.html',{'menuname':menuname})
        except:
            messages.error(request, response.text)
        return render(request, 'category_master/level_list.html',{'menuname':menuname})

def city_list(request):
    if 'accesskey' not in request.session:
        return redirect('/login')
    menuname = request.session['mylist']
    accesskey = request.session['accesskey']
    url = "http://13.235.112.1/ziva/mobile-api/dropdwn-table-list.php"

    payload = json.dumps({"accesskey":accesskey,"name":"CITY"})
    headers = {
        'Content-Type': 'text/plain'
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    if response.status_code == 200:
        data = response.json()
        city_list = data['itemmasterlist']
        return render(request, 'category_master/city_list.html', {"all_data": city_list,'menuname':menuname})
    else:
        try:
            data = response.json()
            return render(request, 'category_master/city_list.html',{'menuname':menuname})
        except:
            messages.error(request, response.text)
        return render(request, 'category_master/city_list.html',{'menuname':menuname})


def state_list(request):
    if 'accesskey' not in request.session:
        return redirect('/login')
    menuname = request.session['mylist']
    accesskey = request.session['accesskey']
    url = "http://13.235.112.1/ziva/mobile-api/dropdwn-table-list.php"

    payload = json.dumps({"accesskey": accesskey,  "name":"STATE"})
    headers = {
        'Content-Type': 'text/plain'
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    if response.status_code == 200:
        data = response.json()
        state_list = data['itemmasterlist']
        return render(request, 'category_master/state_list.html', {"all_data": state_list,'menuname':menuname})
    else:
        try:
            data = response.json()
            return render(request, 'category_master/state_list.html',{'menuname':menuname})
        except:
            messages.error(request, response.text)
        return render(request, 'category_master/state_list.html',{'menuname':menuname})

def uom_list(request):
    if 'accesskey' not in request.session:
        return redirect('/login')
    menuname = request.session['mylist']
    accesskey = request.session['accesskey']
    url = "http://13.235.112.1/ziva/mobile-api/dropdwn-table-list.php"

    payload = json.dumps({"accesskey":accesskey, "name":"UOM"})
    headers = {
        'Content-Type': 'text/plain'
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    if response.status_code == 200:
        data = response.json()
        uom_list = data['itemmasterlist']
        return render(request, 'category_master/uom_list.html', {"all_data": uom_list,'menuname':menuname})
    else:
        try:
            data = response.json()
            return render(request, 'category_master/uom_list.html',{'menuname':menuname})
        except:
            messages.error(request, response.text)
        return render(request, 'category_master/uom_list.html',{'menuname':menuname})


def gst_list(request):
    if 'accesskey' not in request.session:
        return redirect('/login')
    menuname = request.session['mylist']
    accesskey = request.session['accesskey']
    url = "http://13.235.112.1/ziva/mobile-api/dropdwn-table-list.php"

    payload = json.dumps({"accesskey":accesskey,    "name":"GST"})
    headers = {
        'Content-Type': 'text/plain'
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    if response.status_code == 200:
        data = response.json()
        gst_list = data['itemmasterlist']
        return render(request, 'category_master/gst_list.html', {"all_data": gst_list,'menuname':menuname})
    else:
        try:
            data = response.json()
            return render(request, 'category_master/gst_list.html',{'menuname':menuname})
        except:
            messages.error(request,response.text)
        return render(request, 'category_master/gst_list.html',{'menuname':menuname})



def category_list(request):
    if 'accesskey' not in request.session:
        return redirect('/login')
    menuname = request.session['mylist']
    accesskey = request.session['accesskey']
    url = "http://13.235.112.1/ziva/mobile-api/dropdwn-table-list.php"

    payload = json.dumps({"accesskey":accesskey,    "name":"CATEGORY"})
    headers = {
        'Content-Type': 'text/plain'
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    if response.status_code == 200:
        data = response.json()
        category_list = data['itemmasterlist']
        return render(request, 'category_master/category_list.html', {'menuname':menuname,"all_data": category_list})
    else:
        try:
            data = response.json()
            return render(request, 'category_master/category_list.html',{'menuname':menuname})
        except:
            messages.error(request, response.text)
        return render(request, 'category_master/category_list.html',{'menuname':menuname})


def des_list(request):
    if 'accesskey' not in request.session:
        return redirect('/login')
    menuname = request.session['mylist']
    accesskey = request.session['accesskey']
    url = "http://13.235.112.1/ziva/mobile-api/price-list.php"

    payload = json.dumps({"accesskey":accesskey})
    headers = {
        'Content-Type': 'text/plain'
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    if response.status_code == 200:
        data = response.json()
        des_list = data['pricelist']
        return render(request, 'category_master/des_list.html', {"all_data": des_list,'menuname':menuname})
    elif response.status_code == 400:
        data = response.json()
        messages.error(request, data['message'])
        return render(request, 'login1.html')
    else:
        try:
            data = response.json()
            return render(request, 'category_master/des_list.html',{'menuname':menuname})
        except:
            messages.error(request,response.text)
        return render(request, 'category_master/des_list.html',{'menuname':menuname})


def store_status_inactive(request):
    if 'accesskey' not in request.session:
        return redirect('/login')
    accesskey = request.session['accesskey']

    url = "http://13.235.112.1/ziva/mobile-api/status-change.php"

    payload = json.dumps({
        "accesskey": accesskey,
        "sno": request.POST.get('id'),
        "type": "Dropdownmaster",
        "status": request.POST.get('status')
    })
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    if response.status_code == 200:
        data = response.json()
        messages.success(request, data['message'])
        return redirect('/storetype_list')
    else:
        try:
            data = response.json()
            messages.error(request, data['message'])
            return redirect('storetype_list')
        except:
            messages.error(request, response.text)
        return redirect('/storetype_list')
def des_status_inactive(request):
    if 'accesskey' not in request.session:
        return redirect('/login')
    accesskey = request.session['accesskey']

    url = "http://13.235.112.1/ziva/mobile-api/status-change.php"

    payload = json.dumps({
        "accesskey":accesskey,
        "sno": request.POST.get('id'),
        "type": "Pricemaster",
        "status": request.POST.get('status')
    })
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    if response.status_code == 200:
        data = response.json()
        messages.success(request, data['message'])
        return redirect('/des_list')
    else:
        try:
            data = response.json()
            messages.error(request, data['message'])
            return redirect('/des_list')
        except:
            messages.error(request,response.text)
        return redirect('/des_list')

def gst_status_inactive(request):
    if 'accesskey' not in request.session:
        return redirect('/login')
    accesskey = request.session['accesskey']

    url = "http://13.235.112.1/ziva/mobile-api/status-change.php"

    payload = json.dumps({
            "accesskey": accesskey,
            "sno": request.POST.get('id'),
            "type": "Dropdownmaster",
            "status": request.POST.get('status')
    })
    headers = {
            'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    if response.status_code == 200:
        data = response.json()
        messages.success(request, data['message'])
        return redirect('/gst_list')
    elif response.status_code == 400:
        data = response.json()
        if data['message'] == 'Sorry! some details are missing':
            messages.error(request, data['message'])
            return redirect('/gst_list')
        else:
            messages.error(request, data['message'])
            return redirect('/login')
    else:
        try:
            data = response.json()
            messages.error(request, data['message'])
            return redirect('/gst_list')
        except:
            messages.error(request, response.text)
        return redirect('/gst_list')


def uom_status_inactive(request):
    if 'accesskey' not in request.session:
        return redirect('/login')
    accesskey = request.session['accesskey']

    url = "http://13.235.112.1/ziva/mobile-api/status-change.php"

    payload = json.dumps({
        "accesskey": accesskey,
        "sno": request.POST.get('id'),
        "type": "Dropdownmaster",
        "status": request.POST.get('status')
    })
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    if response.status_code == 200:
        data = response.json()
        messages.success(request, data['message'])
        return redirect('/uom_list')
    else:
        try:
            data = response.json()
            messages.error(request, data['message'])
            return redirect('/uom_list')
        except:
            messages.error(request, response.text)
        return redirect('/uom_list')

def get_price(request):
    if 'accesskey' not in request.session:
        return redirect('/login')
    accesskey = request.session['accesskey']

    url = "http://13.235.112.1/ziva/mobile-api/price-list.php"

    payload = json.dumps({
        "accesskey": accesskey,
    })
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    data = response.json()
    return JsonResponse({'data':data})

def role_status_inactive(request):
    if 'accesskey' not in request.session:
        return redirect('/login')
    accesskey = request.session['accesskey']

    url = "http://13.235.112.1/ziva/mobile-api/status-change.php"

    payload = json.dumps({
        "accesskey": accesskey,
        "sno": request.POST.get('id'),
        "type": "Dropdownmaster",
        "status": request.POST.get('status')
    })
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    if response.status_code == 200:
        data = response.json()
        messages.success(request, data['message'])
        return redirect('/role_list')
    else:
        try:
            data = response.json()
            messages.error(request, data['message'])
            return redirect('/role_list')
        except:
            messages.error(request, response.text)
        return redirect('/role_list')

def level_status_inactive(request):
    if 'accesskey' not in request.session:
        return redirect('/login')
    accesskey = request.session['accesskey']

    url = "http://13.235.112.1/ziva/mobile-api/status-change.php"

    payload = json.dumps({
        "accesskey": accesskey,
        "sno": request.POST.get('id'),
        "type": "Dropdownmaster",
        "status": request.POST.get('status')
    })
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    if response.status_code == 200:
        data = response.json()
        messages.success(request, data['message'])
        return redirect('/level_list')
    else:
        try:
            data = response.json()
            messages.error(request, data['message'])
            return redirect('/level_list')
        except:
            messages.error(request, response.text)
        return redirect('/level_list')

def state_status_inactive(request):
    if 'accesskey' not in request.session:
        return redirect('/login')
    accesskey = request.session['accesskey']

    url = "http://13.235.112.1/ziva/mobile-api/status-change.php"

    payload = json.dumps({
        "accesskey": accesskey,
        "sno": request.POST.get('id'),
        "type": "Dropdownmaster",
        "status": request.POST.get('status')
    })
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    if response.status_code == 200:
        data = response.json()
        messages.success(request, data['message'])
        return redirect('/state_list')
    else:
        try:
            data = response.json()
            messages.error(request, data['message'])
            return redirect('/state_list')
        except:
            messages.error(request, response.text)
        return redirect('/state_list')

def category_status_inactive(request):
    if 'accesskey' not in request.session:
        return redirect('/login')
    accesskey = request.session['accesskey']

    url = "http://13.235.112.1/ziva/mobile-api/status-change.php"

    payload = json.dumps({
        "accesskey": accesskey,
        "sno": request.POST.get('id'),
        "type": "Dropdownmaster",
        "status": request.POST.get('status')
    })
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    if response.status_code == 200:
        data = response.json()
        messages.success(request, data['message'])
        return redirect('/category_list')
    else:
        try:
            data = response.json()
            messages.error(request, data['message'])
            return redirect('/category_list')
        except:
            messages.error(request, response.text)
        return redirect('/category_list')
def city_status_inactive(request):
    if 'accesskey' not in request.session:
        return redirect('/login')

    accesskey = request.session['accesskey']

    url = "http://13.235.112.1/ziva/mobile-api/status-change.php"

    payload = json.dumps({
            "accesskey": accesskey,
            "sno": request.POST.get('id'),
            "type": "Dropdownmaster",
            "status": request.POST.get('status')
        })
    headers = {
            'Content-Type': 'application/json'
        }

    response = requests.request("POST", url, headers=headers, data=payload)
    if response.status_code == 200:
        data = response.json()
        messages.success(request, data['message'])
        return redirect('/city_list')
    elif response.status_code == 400:
        data = response.json()
        if data['message'] == 'Sorry! some details are missing':
            messages.error(request, data['message'])
            return redirect('/add_bussupply')
        else:
            messages.error(request, data['message'])
            return redirect('/login')
    else:
        try:
            data = response.json()
            messages.error(request, data['message'])
            return redirect('/city_list')
        except:
            messages.error(request, response.text)
        return redirect('/city_list')

def depo_add(request):
    if 'accesskey' not in request.session:
        return redirect('/login')
    try:

        menuname = request.session['mylist']
        g = geocoder.ip('me', user_agent='http')
        latlng = g.latlng
        lat = latlng[0]
        lng = latlng[1]
        accesskey = request.session['accesskey']
        payload = json.dumps({"accesskey": accesskey})
        headers = {
            'Content-Type': 'application/json'
        }
        url = "http://13.235.112.1/ziva/mobile-api/region-list.php"
        response = requests.request("POST", url, headers=headers, data=payload)
        if response.status_code == 200:
            data = response.json()
            regionlist = data['regionlist']
        else:
            try:
                data = response.json()
                messages.error(request,response.text)
                return render(request, 'depo/depo_add.html')
            except:
                messages.error(request,response.text)
            return render(request, 'depo/depo_add.html')

        if request.method == "POST":
            gstattach = request.FILES.get("gstattach")
            depofile = request.FILES.get("depofile")
            licattach = request.FILES.get("licattach")
            if licattach:
                gstattach = base64.b64encode(gstattach.read())
                gst_name = request.FILES.get("gstattach").name

            else:
                gstattach = None
                gst_name = None
            if licattach:
                licenceattach_data = base64.b64encode(licattach.read())
                licenceattach_name = request.FILES.get("licattach").name

            else:
                licenceattach_data = None
                licenceattach_name = None
            if depofile:
                depofile_data = base64.b64encode(depofile.read())
                depofile_name = request.FILES.get("depofile").name

            else:
                depofile_data = None
                depofile_name = None

            id=request.POST.get("regionid")

            for i in regionlist:
                if i['region_id'] == id:
                    whid=i['warehouseid']
                    whname=i['warehousename']
                    regionname = i['regionname']

            url = "http://13.235.112.1/ziva/mobile-api/add-depomaster.php"

            payload = {
                        "accesskey": accesskey,
                         "depo_code":request.POST.get("depocode"),
                        "deponame": request.POST.get("deponame"),
                        "gstnumber": request.POST.get("gstnumber"),
                        "address": request.POST.get("address"),
                        "depo_manager": request.POST.get("depomanager"),
                        "location":  str(lat)+","+str(lng),
                        "depo_contact_no": request.POST.get('mobileno'),
                        "gstattach": gstattach,
                        "gstattachfilename": gst_name,
                        "licence":request.POST.get("license"),
                        "licenceattach":licenceattach_data,
                        "licencefilename": licenceattach_name,
                        "depoattach":  depofile_name,
                        "depoattachfilename":depofile_data,
                        "warehouseid": whid,
                        "warehouse": whname,
                        "regionid": request.POST.get('regionid'),
                        "regionname": regionname
                    }
            payload = json.dumps(payload, cls=BytesEncoder)
            headers = {
                    'Content-Type': 'application/json'
                    }
            r = requests.post(url, payload, headers=headers)
            if r.status_code == 200:
                r1 = r.json()
                messages.success(request, r1['message'])
                return redirect('/depo_list')
            else:
                    r1 = r.json()
                    messages.error(request, r1['message'])
                    return redirect('/depo_list')
        else:
            return render(request, 'depo/depo_add.html', {'data': regionlist,'menuname':menuname})

    except Exception as e:
        messages.error(request, str(e))
        return render(request, 'depo/depo_add.html', {"menuname": menuname})


def depo_list(request):
    if 'accesskey' not in request.session:
        return redirect('/login')
    try:
        accesskey = request.session['accesskey']
        menuname = request.session['mylist']
        payload = json.dumps({"accesskey": accesskey})
        headers = {
            'Content-Type': 'application/json'
        }
        url = "http://13.235.112.1/ziva/mobile-api/region-list.php"
        response = requests.request("POST", url, headers=headers, data=payload)

        data = response.json()
        regionlist = data['regionlist']

        url = "http://13.235.112.1/ziva/mobile-api/warehousemaster-list.php"

        payload = json.dumps({"accesskey": accesskey})
        headers = {
            'Content-Type': 'text/plain'
        }
        response = requests.request("GET", url, headers=headers, data=payload)

        data = response.json()
        wh_masterlist = data['warehouselist']
        if request.method == 'POST':
            url = "http://13.235.112.1/ziva/mobile-api/depo-list-new.php"

            payload = json.dumps({"accesskey":accesskey,
                                  "warehouseid":request.POST.get('warehouseid'),
                                  "regionid":request.POST.get('regionid')})

            headers = {
                'Content-Type': 'text/plain'
            }
            response = requests.request("GET", url, headers=headers, data=payload)
            if response.status_code == 200:
                data = response.json()
                depolist = data['depolist']
                return render(request, 'depo/depo_list.html', {'all_data': depolist,'data':regionlist,'menuname':menuname,'wh_masterlist':wh_masterlist})
            else:
                return render(request, 'depo/depo_list.html',{'data':regionlist,'menuname':menuname,'wh_masterlist':wh_masterlist})
        else:
            url = "http://13.235.112.1/ziva/mobile-api/depo-list.php"

            payload = json.dumps({"accesskey": accesskey})
            headers = {
                'Content-Type': 'text/plain'
            }
            response = requests.request("GET", url, headers=headers, data=payload)
            if response.status_code == 200:
                data = response.json()
                depolist = data['depolist']
                return render(request, 'depo/depo_list.html',
                              {'all_data': depolist, 'data': regionlist, 'menuname': menuname,
                               'wh_masterlist': wh_masterlist})
            else:
                return render(request, 'depo/depo_list.html',
                              {'data': regionlist, 'menuname': menuname, 'wh_masterlist': wh_masterlist})
    except:
        if response.status_code == 400:
            messages.error(request, data['message'])
            return render(request, 'login1.html')
    return render(request, 'depo/depo_list.html',{'menuname':menuname})



def depo_status_active(request):
    if 'accesskey' not in request.session:
        return redirect('/login')
    accesskey = request.session['accesskey']
    url = "http://13.235.112.1/ziva/mobile-api/status-change.php"

    payload = json.dumps({
        "accesskey": accesskey,
        "sno": request.POST.get('id'),
        "type": "Depomaster",
        "status": "Inactive"
    })
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    if response.status_code == 200:
        data = response.json()
        messages.success(request, data['message'])
        return redirect('depo_list')
    else:
        try:
            data = response.json()
            messages.error(request, data['message'])
            return redirect('depo_list')
        except:
            messages.error(request,response.text)
        return redirect('depo_list')

def depo_status_inactive(request):
    if 'accesskey' not in request.session:
        return redirect('/login')
    accesskey = request.session['accesskey']
    url = "http://13.235.112.1/ziva/mobile-api/status-change.php"

    payload = json.dumps({
        "accesskey": accesskey,
        "sno": request.POST.get('id'),
        "type": "Depomaster",
        "status": "Active"
    })
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    if response.status_code == 200:
        data = response.json()
        messages.success(request, data['message'])
        return redirect('/depo_list')
    else:
        try:
            data = response.json()
            messages.error(request, data['message'])
            return redirect('/depo_list')
        except:
            messages.error(request, response.text)
        return redirect('/depo_list')
def bus_status_active(request):
    if 'accesskey' not in request.session:
        return redirect('/login')
    accesskey = request.session['accesskey']
    url = "http://13.235.112.1/ziva/mobile-api/status-change.php"

    payload = json.dumps({
        "accesskey": accesskey,
        "sno": request.POST.get('id'),
        "type": "Busstation",
        "status": "Inactive"
    })
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    if response.status_code == 200:
        data = response.json()
        messages.success(request, data['message'])
        return redirect('bus_list')
    else:
        try:
            data = response.json()
            messages.error(request, data['message'])
            return redirect('bus_list')
        except:
            messages.error(request, response.text)
        return redirect('bus_list')

def bus_status_inactive(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    accesskey = request.session['accesskey']
    url = "http://13.235.112.1/ziva/mobile-api/status-change.php"

    payload = json.dumps({
        "accesskey": accesskey,
        "sno": request.POST.get('id'),
        "type": "Depomaster",
        "status": "Active"
    })
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    if response.status_code == 200:
        data = response.json()
        messages.success(request, data['message'])
        return redirect('bus_list')
    else:
        try:
            data = response.json()
            messages.error(request, data['message'])
            return redirect('bus_list')
        except:
            messages.error(request,response.text)
        return redirect('bus_list')
def region_list(request):
  if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')

  try:
        menuname = request.session['mylist']
        accesskey = request.session['accesskey']

        url = "http://13.235.112.1/ziva/mobile-api/warehousemaster-list.php"

        payload = json.dumps({"accesskey":accesskey})
        headers = {
            'Content-Type': 'text/plain'
        }
        response = requests.request("GET", url, headers=headers, data=payload)

        data = response.json()
        wh_masterlist = data['warehouselist']

        payload = json.dumps({"accesskey":accesskey})
        headers = {
            'Content-Type': 'application/json'
        }
        url = "http://13.235.112.1/ziva/mobile-api/region-list.php"
        response = requests.request("POST", url, headers=headers, data=payload)
        if response.status_code == 200:
            data = response.json()
            regionlist = data['regionlist']
            return render(request, 'region/region-list.html', {'all_data': regionlist,'data':wh_masterlist,'menuname':menuname})
        else:
            return render(request, 'region/region-list.html',{'data':wh_masterlist,'menuname':menuname})
  except:
      if response.status_code == 400:
          data = response.json()
          messages.error(request, data['message'])
          return render(request, 'login1.html')
  return render(request, 'region/region-list.html', {'menuname': menuname})

def region_add(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    menuname = request.session['mylist']
    accesskey = request.session['accesskey']
    url = "http://13.235.112.1/ziva/mobile-api/warehousemaster-list.php"

    payload = json.dumps({"accesskey":accesskey})
    headers = {
        'Content-Type': 'text/plain'
    }
    response = requests.request("GET", url, headers=headers, data=payload)
    data = response.json()
    wh_masterlist = data['warehouselist']
    if request.method == 'POST':
        accesskey = request.session['accesskey']
        payload = json.dumps({"accesskey": accesskey,
                              "regionname": request.POST.get('regionname'),
                              "warehouseid":request.POST.get('whid'),
                              "region_code":request.POST.get('region_code'),
                              "warehousename":  request.POST.get('warehousename'),
                              "region_contact_no":  request.POST.get('mobileno'),
                              "region_manager":  request.POST.get('regionmanager')
                              })
        headers = {
            'Content-Type': 'application/json'
        }
        url = "http://13.235.112.1/ziva/mobile-api/create-region.php"
        response = requests.request("POST", url, headers=headers, data=payload)
        if response.status_code == 200:
            data = response.json()
            messages.success(request, data['message'])
            return redirect('/region_list')
        else:
            data = response.json()
            messages.error(request,data['message'])
            return redirect('/region_list')
    else:
        return render(request,'region/region-add.html',{'data':wh_masterlist,'menuname':menuname})


def get_region(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    accesskey = request.session['accesskey']
    url = "http://13.235.112.1/ziva/mobile-api/region-search.php"

    payload = json.dumps({
        "accesskey": accesskey,
        "regionid": request.POST.get('id')
    })

    headers = {
        'Content-Type': 'application/json'
    }
    data = requests.request("POST", url, headers=headers, data=payload)
    data2 = data.json()
    return JsonResponse({'data': data2})


def region_edit(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    accesskey = request.session['accesskey']
    if request.method == 'POST':
        url = "http://13.235.112.1/ziva/mobile-api/edit-regionmaster.php"

        payload = json.dumps({
            "accesskey": accesskey,
            "region_code":request.POST.get('regioncode'),
            "regionid":  request.POST.get('region_id1'),
            "regionname": request.POST.get('regionname1'),
            "region_manager": request.POST.get('regionmanager1'),
            "region_contact_no": request.POST.get('mobileno1'),
            "warehouseid": request.POST.get('whid1'),
            "warehousename": request.POST.get('warehousename1'),
        })
        headers = {
            'Content-Type': 'application/json'
        }

        response = requests.request("POST", url, headers=headers, data=payload)

        if response.status_code == 200:
            data = response.json()
            messages.success(request, data['message'])
            return redirect('/region_list')
        elif response.status_code == 400:
            data = response.json()
            text = data['message']
            if 'some details are missing' in text:
                messages.error(request, data['message'])
                return redirect('/region_list')
            else:
                messages.error(request, data['message'])
                return redirect('/login')
        else:
            try:
                r = response.json()
                messages.error(request, r['message'])
            except:
                messages.error(request, response.text)
            return redirect('/region_list')
    return redirect('/region_list')

def stk_warehouse_list(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    accesskey = request.session['accesskey']
    url = "http://13.235.112.1/ziva/mobile-api/warehousemaster-list.php"

    payload = json.dumps({"accesskey": accesskey})
    headers = {
        'Content-Type': 'text/plain'
    }
    response = requests.request("GET", url, headers=headers, data=payload)
    if response.status_code == 200:
        data2 = response.json()
        return JsonResponse({'data': data2})
    elif response.status_code == 400:
        data = response.json()
        if data['message'] == 'Sorry! some details are missing':
            return JsonResponse({'data': data})
        else:
            messages.error(request, data['message'])
            return redirect('/login')
    elif response.status_code == 503:
        data = response.json()
        return JsonResponse({'data': data})
    elif response.status_code == 500:
        data = {'error': 'true', 'message': 'Internal server error'}
        return JsonResponse({'data': data})
    else:
        data = {'error': 'true', 'message': 'something went wrong'}
        return JsonResponse({'data': data})


def stk_depot_list(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    accesskey = request.session['accesskey']
    url = "http://13.235.112.1/ziva/mobile-api/depo-list.php"

    payload = json.dumps({"accesskey": accesskey})
    headers = {
        'Content-Type': 'text/plain'
    }
    response = requests.request("GET", url, headers=headers, data=payload)
    if response.status_code == 200:
        data2 = response.json()
        return JsonResponse({'data': data2})
    elif response.status_code == 400:
        data = response.json()
        if data['message'] == 'Sorry! some details are missing':
            return JsonResponse({'data': data})
        else:
            messages.error(request, data['message'])
            return redirect('/login')
    elif response.status_code == 503:
        data = response.json()
        return JsonResponse({'data': data})
    elif response.status_code == 500:
        data = {'error': 'true', 'message': 'Internal server error'}
        return JsonResponse({'data': data})
    else:
        data = {'error': 'true', 'message': 'something went wrong'}
        return JsonResponse({'data': data})


def warehouseinventory_search(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    wh_code = request.session['wh_code']
    accesskey = request.session['accesskey']
    url = "http://13.235.112.1/ziva/mobile-api/warehouseinventory-search-new-admin.php"
    payload = json.dumps({
        "accesskey": accesskey,
        "id": wh_code,
        "type": "Warehouse"
    })
    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.request("GET", url, headers=headers, data=payload)
    if response.status_code == 200:
        data = response.json()
        return JsonResponse({'data': data})
    elif response.status_code == 400:
        data = response.json()
        if data['message'] == 'Sorry! some details are missing':
            messages.error(request, data['message'])
            return JsonResponse({'data': data})
        else:
            messages.error(request, data['message'])
            return redirect('/login')
    else:
        return JsonResponse({'data': "Some thing went wrong"})


def depotinventory_search(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    fromid =   request.session['fromid']
    accesskey = request.session['accesskey']
    url = "http://13.235.112.1/ziva/mobile-api/warehouseinventory-search-new-admin.php"
    payload = json.dumps({
        "accesskey": accesskey,
        "id": fromid,
        "type": "Depo"
    })
    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.request("GET", url, headers=headers, data=payload)
    if response.status_code == 200:
        data = response.json()
        return JsonResponse({'data': data})
    elif response.status_code == 400:
        data = response.json()
        if data['message'] == 'Sorry! some details are missing':
            messages.error(request, data['message'])
            return JsonResponse({'data': data})
        else:
            messages.error(request, data['message'])
            return redirect('/login')
    else:
        return JsonResponse({'data': "Some thing went wrong"})



def businventory_search(request):
        if 'accesskey' not in request.session:
            messages.error(request, 'Access denied!')
            return redirect('/login')
        busid1 = request.session['busid1']
        accesskey = request.session['accesskey']
        url = "http://13.235.112.1/ziva/mobile-api/warehouseinventory-search-new-admin.php"
        payload = json.dumps({
            "accesskey": accesskey,
            "id": busid1,
            "type": "Bus Station"
        })
        headers = {
            'Content-Type': 'application/json'
        }
        response = requests.request("GET", url, headers=headers, data=payload)
        if response.status_code == 200:
            data = response.json()
            return JsonResponse({'data': data})
        elif response.status_code == 400:
            data = response.json()
            if data['message'] == 'Sorry! some details are missing':
                messages.error(request, data['message'])
                return JsonResponse({'data': data})
            else:
                messages.error(request, data['message'])
                return redirect('/login')
        else:
            return JsonResponse({'data': "Some thing went wrong"})


def stk_region_list(request):
            if 'accesskey' not in request.session:
                messages.error(request, 'Access denied!')
                return redirect('/login')
            accesskey = request.session['accesskey']
            url = "http://13.235.112.1/ziva/mobile-api/region-list.php"
            payload = json.dumps({
                "accesskey": accesskey
            })
            headers = {
                'Content-Type': 'application/json'
            }

            response = requests.request("GET", url, headers=headers, data=payload)
            if response.status_code == 200:
                data = response.json()
                return JsonResponse({'data': data})
            elif response.status_code == 400:
                data = response.json()
                if data['message'] == 'Sorry! some details are missing':
                    messages.error(request, data['message'])
                    return JsonResponse({'data': data})
                else:
                    messages.error(request, data['message'])
                    return redirect('/login')
            else:
                return JsonResponse({'data': "Some thing went wrong"})


def stk_busstation_list(request):
            if 'accesskey' not in request.session:
                messages.error(request, 'Access denied!')
                return redirect('/login')
            accesskey = request.session['accesskey']
            url = "http://13.235.112.1/ziva/mobile-api/bus-list.php"
            payload = json.dumps({
                "accesskey": accesskey
            })
            headers = {
                'Content-Type': 'application/json'
            }

            response = requests.request("GET", url, headers=headers, data=payload)
            if response.status_code == 200:
                data2 = response.json()
                return JsonResponse({'data': data2})
            elif response.status_code == 400:
                data = response.json()
                if data['message'] == 'Sorry! some details are missing':
                    return JsonResponse({'data': data})
                else:
                    messages.error(request, data['message'])
                    return redirect('/login')
            elif response.status_code == 503:
                data = response.json()
                return JsonResponse({'data': data})
            elif response.status_code == 500:
                data = {'error': 'true', 'message': 'Internal server error'}
                return JsonResponse({'data': data})
            else:
                data = {'error': 'true', 'message': 'something went wrong'}
                return JsonResponse({'data': data})


def warehouse_list(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    try:
        menuname = request.session['mylist']
        accesskey = request.session['accesskey']
        url = "http://13.235.112.1/ziva/mobile-api/warehousemaster-list.php"

        payload = json.dumps({"accesskey":accesskey})
        headers = {
            'Content-Type': 'text/plain'
        }
        response = requests.request("GET", url, headers=headers, data=payload)
        if response.status_code == 200:
            data = response.json()
            wh_masterlist = data['warehouselist']
            return render(request, 'warehouse/warehouse_list.html', {'all_data': wh_masterlist,'menuname':menuname})
        if response.status_code == 400:
            data = response.json()
            messages.error(request, data['message'])
            return redirect('/login')
        else:
            return render(request, 'warehouse/warehouse_list.html',{'menuname':menuname})
    except:
        messages.error(request, data.text)
    return render(request, 'category_master/storetype_list.html', {'menuname': menuname})

def warehouse_add(request):
    try:
        if 'accesskey' not in request.session:
            messages.error(request, 'Access denied!')
            return redirect('/login')
        menuname = request.session['mylist']
        accesskey = request.session['accesskey']
        url = "http://13.235.112.1/ziva/mobile-api/region-list.php"
        payload = json.dumps({
            "accesskey": accesskey,
            "regionid": ""
        })
        headers = {
            'Content-Type': 'application/json'
        }

        response = requests.request("GET", url, headers=headers, data=payload)
        data = response.json()
        region = data['regionlist']


        if request.method == "POST":
            gstattach = request.FILES.get("gstattach")
            panattach = request.FILES.get("panattach")
            licattach = request.FILES.get("licattach")
            warehouse = request.FILES.get("warehousefile")
            if gstattach:
                gstattach = base64.b64encode(gstattach.read())
                gst_name = request.FILES.get("gstattach").name

            else:
                gstattach = None
                gst_name = None
            if panattach:
                panattach_data = base64.b64encode(panattach.read())
                panattach_name = request.FILES.get("panattach").name

            else:
                panattach_data = None
                panattach_name = None
            if licattach:
                licattach_data = base64.b64encode(licattach.read())
                licattach_name = request.FILES.get("licattach").name

            else:
                licattach_data = None
                licattach_name = None
            if warehouse:
                warehouse_data = base64.b64encode(warehouse.read())
                warehouse_name = request.FILES.get("warehousefile").name

            else:
                warehouse_data = None
                warehouse_name = None

            url = "http://13.235.112.1/ziva/mobile-api/add-warehousemaster.php"
            payload = {
                "accesskey": accesskey,
                "regionid": request.POST.get('depo'),
                ""
                "warehousename": request.POST.get('warehousename'),
                "gstnumber": " ",
                "licenseno": " ",
                "panno": " ",
                "address": request.POST.get('storeaddress'),
                "wh_manager": request.POST.get('warehousemamager'),
                "location": request.POST.get('location'),
                "wh_contact_no": request.POST.get('mobileno'),
                "gstattachfilename": gst_name,
                "panattachfilekename": panattach_name,
                "licencefilename": licattach_name,
                "warehouseattachfilename": warehouse_name,
                "panattach": panattach_data,
                "warehouseattach": warehouse_data,
                "gstattach": gstattach,
                "licence": licattach_data,
                "warehouse_code":request.POST.get('warehouse_code')
            }
            payload = json.dumps(payload, cls=BytesEncoder)

            headers = {
                'Content-Type': 'application/json'
            }
            r = requests.post(url, payload, headers=headers)
            if r.status_code == 200:
                r1 = r.json()
                messages.success(request, r1['message'])
                return redirect('warehouse_list')
            else:
                try:
                    r1 = r.json()
                    messages.error(request,r1['message'])
                except:
                    r1 = r.json()
                    messages.error(request, response.text)
                return render(request, 'warehouse/warehouse_add.html', {'data': region,'menuname':menuname})

        return render(request, 'warehouse/warehouse_add.html', {'data': region,'menuname':menuname})
    except:
     if  response.status_code  == 400:
         messages.error(request, data['message'])
         return redirect('/login')
    return render(request, 'warehouse/warehouse_add.html', {'menuname': menuname})
def warehouse_status_active(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    accesskey = request.session['accesskey']
    url = "http://13.235.112.1/ziva/mobile-api/status-change.php"

    payload = json.dumps({
        "accesskey": accesskey,
        "sno": request.POST.get('id'),
        "type": "Warehousemaster",
        "status": "Inactive"
    })
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    if response.status_code == 200:
        data = response.json()
        messages.success(request, data['message'])
        return redirect('warehouse_list')
    else:
        try:
            data = response.json()
            messages.error(request, data['message'])
            return redirect('warehouse_list')
        except:
            messages.error(request,response.text)
        return redirect('warehouse_list')



def warehouse_status_inactive(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    accesskey = request.session['accesskey']
    url = "http://13.235.112.1/ziva/mobile-api/status-change.php"

    payload = json.dumps({
        "accesskey": accesskey,
        "sno": request.POST.get('id'),
        "type": "Warehousemaster",
        "status": "Active"
    })
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    if response.status_code == 200:
        data = response.json()
        messages.success(request, data['message'])
        return redirect('warehouse_list')
    else:
        try:
            data = response.json()
            messages.error(request, data['message'])
            return redirect('warehouse_list')
        except:
            messages.error(request,response.text)
        return redirect('warehouse_list')


def vendor_add(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    menuname = request.session['mylist']
    accesskey = request.session['accesskey']
    url = "http://13.235.112.1/ziva/mobile-api/warehousemaster-list.php"

    payload = json.dumps({"accesskey": accesskey})
    headers = {
        'Content-Type': 'text/plain'
    }
    response = requests.request("GET", url, headers=headers, data=payload)

    data = response.json()
    wh_masterlist = data['warehouselist']

    url = "http://13.235.112.1/ziva/mobile-api/statelist.php"

    payload = json.dumps({
        "accesskey": accesskey,
        "category": "Indian"
    })
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    if response.status_code == 200:
        res_state = response.json()
        state_list = res_state['statelist']
    else:
        try:
            res_state = response.json()
            messages.error(request,res_state)
            return render(request, 'vendor/vendor_add.html')
        except:
            messages.error(request, response.text)
        return render(request, 'vendor/vendor_add.html')

    if request.method == "POST":
        gstattach = request.FILES.get("gstattach")
        panattach = request.FILES.get("panattach")

        if gstattach:
            gstattach_data = base64.b64encode(gstattach.read())
            gstattach_name =  request.FILES.get("gstattach").name

        else:
            gstattach_data = None
            gstattach_name = None

        if panattach:
            panattach_data = base64.b64encode(panattach.read())
            panattach_data_name = request.FILES.get("gstattach").name


        else:
            panattach_data = None
            panattach_data_name = None

        url = "http://13.235.112.1/ziva/mobile-api/add-vendormaster.php"

        payload = {
            "accesskey": accesskey,
            "vendorname": request.POST.get('vendorname'),
            "gstno": request.POST.get('gstnumber'),
            "panno": request.POST.get('pancard'),
            "contactperson": request.POST.get('contactperson'),
            "mobile": request.POST.get('mobile'),
            "emailid": request.POST.get('email'),
            "address": request.POST.get('storeaddress'),
            "pincode": request.POST.get('pincode'),
            "state": request.POST.get('state'),
            "fssai":request.POST.get('fssai'),
            "city": request.POST.get('city'),
            "panattach": panattach_data,
            "gstattach": gstattach_data,
            "region": "",
            "depo": "",
            "warehouse": "",
            "regionid": "",
            "depoid": "",
            "warehouseid": "",
            "busstationid": "",
            "busstationname": "",
            "panattachfilename":panattach_data_name,
            "gstattachfilename":gstattach_name

        }
        payload = json.dumps(payload, cls=BytesEncoder)
        headers = {
            'Content-Type': 'application/json'
        }
        r = requests.post(url, payload, headers=headers)

        if r.status_code == 200:
            data = r.json()
            messages.success(request, data['message'])
            return redirect('vendor_list')
        else:
            try:
                data = r.json()
                messages.error(request, data['message'])
                return redirect('vendor_list')
            except:
                messages.error(request, data['message'])
            return redirect('vendor_list')

    return render(request, 'vendor/vendor_add.html', {'data': state_list,'data1':wh_masterlist,'menuname':menuname})


def vendor_list(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    try:
        menuname = request.session['mylist']
        accesskey = request.session['accesskey']
        url = "http://13.235.112.1/ziva/mobile-api/vendormasterlist.php"

        payload = json.dumps({"accesskey":accesskey})
        headers = {
            'Content-Type': 'application/json'
        }

        response = requests.request("GET", url, headers=headers, data=payload)
        if response.status_code == 200:
            data = response.json()
            vendor_masterlist = data['vendormasterlist']
            return render(request, 'vendor/vendor_list.html', {'all_data': vendor_masterlist,'menuname':menuname})
        elif response.status_code == 400:
            data = response.json()
            messages.error(request,data['message'])
            return render(request,'login1.html')
        else:
            try:
                data = response.json()
                return render(request, 'vendor/vendor_list.html',{'menuname':menuname})
            except:
                messages.error(request,response.text)
            return render(request, 'vendor/vendor_list.html',{'menuname':menuname})
    except:
        messages.error(request,data['message'])
    return render(request,'login1.html')

def vendor_status_active(request, id):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    accesskey = request.session['accesskey']
    url = "http://13.235.112.1/ziva/mobile-api/status-change.php"

    payload = json.dumps({
        "accesskey": accesskey,
        "sno": id,
        "type": "Vendormaster",
        "status": "Inactive"
    })
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)


    if response.status_code == 200:
        data = response.json()
        messages.success(request, data['message'])
        return redirect('vendor_list')
    else:
        data = response.json()
        messages.error(request, data['message'])
        return redirect('vendor_list')


def vendor_status_inactive(request, id):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    accesskey = request.session['accesskey']
    url = "http://13.235.112.1/ziva/mobile-api/status-change.php"

    payload = json.dumps({
        "accesskey":accesskey,
        "sno": id,
        "type": "Vendormaster",
        "status": "Active"
    })
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    data = response.json()
    if response.status_code == 200:
        messages.success(request, data['message'])
        return redirect('vendor_list')
    else:
        messages.error(request, data['message'])
        return redirect('vendor_list')

def get_storeregion(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    menuname = request.session['mylist']
    accesskey = request.session['accesskey']
    warehouse = request.POST.get('warehouse')
    if warehouse:
        warehouse = warehouse
    else:
        warehouse = 'All'
    url = "http://13.235.112.1/ziva/mobile-api/dropdownlist-storemaster-all.php"

    payload = json.dumps({"accesskey": accesskey, "type":"Region",
                    "warehousename":warehouse,
                    "regionid":"",
                    "depoid":""})
    headers = {
        'Content-Type': 'text/plain'
    }
    response = requests.request("GET", url, headers=headers, data=payload)
    if response.status_code == 200:
        data = response.json()
        return JsonResponse({'data': data})
    elif response.status_code == 400:
        data = response.json()
        return JsonResponse({'data': data})
    elif response.status_code == 503:
        data = response.json()
        return JsonResponse({'data': data})
    else:
        data = {'error':'true','messsage':'something went wrong'}
        return JsonResponse({'data': data})


def get_storebus(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    try:
            accesskey = request.session['accesskey']
            warehouse = request.POST.get('warehouse')
            region = request.POST.get('region')
            depo=request.POST.get('depo')
            if depo:
                depo=depo
            else:
                depo='All'
            if warehouse:
                warehouse = warehouse
            else:
                warehouse='All'
            if region:
                region=region
            else:
                region='All'
            url = "http://13.235.112.1/ziva/mobile-api/dropdownlist-storemaster-all.php"

            payload = json.dumps({"accesskey": accesskey, "type": "Bus Station",
                                  "warehousename": warehouse,
                                  "regionid": region,
                                  "depoid":depo})
            headers = {
                'Content-Type': 'text/plain'
            }
            response = requests.request("GET", url, headers=headers, data=payload)
            if response.status_code == 200:
                data2 = response.json()
                return JsonResponse({'data': data2})
            elif response.status_code == 400:
                data = response.json()
                if data['message'] == 'Sorry! some details are missing':
                    return JsonResponse({'data': data})
                else:
                    messages.error(request, data['message'])
                    return redirect('/login')
            elif response.status_code == 503:
                data = response.json()
                return JsonResponse({'data': data})
            elif response.status_code == 500:
                data = {'error': 'true', 'message': 'Internal server error'}
                return JsonResponse({'data': data})
            else:
                data = {'error': 'true', 'message': 'something went wrong'}
                return JsonResponse({'data': data})
    except Exception as e:
                messages.error(request, str(e))
                return JsonResponse({'data': str(e)})


def get_proformabus(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    role = request.session['role']
    if role == 'Admin':
        accesskey = request.session['accesskey']

        url = "http://13.235.112.1/ziva/mobile-api/dropdownlist-storemaster.php"

        payload = json.dumps({"accesskey": accesskey, "type": "Bus Station",
                              "warehousename": 'All',
                              "regionid": 'All',
                              "depoid": request.POST.get('depo')})
        headers = {
            'Content-Type': 'text/plain'
        }
        response = requests.request("GET", url, headers=headers, data=payload)
        if response.status_code == 200:
            data2 = response.json()
            return JsonResponse({'data': data2})
        elif response.status_code == 400:
            data = response.json()
            if data['message'] == 'Sorry! some details are missing':
                return JsonResponse({'data': data})
            else:
                messages.error(request, data['message'])
                return redirect('/login')
        elif response.status_code == 503:
            data = response.json()
            return JsonResponse({'data': data})
        elif response.status_code == 500:
            data = {'error': 'true', 'message': 'Internal server error'}
            return JsonResponse({'data': data})
        else:
            data = {'error': 'true', 'message': 'something went wrong'}
            return JsonResponse({'data': data})

    else:
        accesskey = request.session['accesskey']
        regionid = request.session['regionid']
        warehousename = request.session['warehousename']

        url = "http://13.235.112.1/ziva/mobile-api/dropdownlist-storemaster.php"

        payload = json.dumps({"accesskey": accesskey, "type": "Bus Station",
                              "warehousename": warehousename,
                              "regionid": regionid,
                              "depoid":request.POST.get('depo')})
        headers = {
            'Content-Type': 'text/plain'
        }
        response = requests.request("GET", url, headers=headers, data=payload)
        if response.status_code == 200:
            data2 = response.json()
            return JsonResponse({'data': data2})
        elif response.status_code == 400:
            data = response.json()
            if data['message'] == 'Sorry! some details are missing':
                return JsonResponse({'data': data})
            else:
                messages.error(request, data['message'])
                return redirect('/login')
        elif response.status_code == 503:
            data = response.json()
            return JsonResponse({'data': data})
        elif response.status_code == 500:
            data = {'error': 'true', 'message': 'Internal server error'}
            return JsonResponse({'data': data})
        else:
            data = {'error': 'true', 'message': 'something went wrong'}
            return JsonResponse({'data': data})


def get_proformastore(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    accesskey = request.session['accesskey']
    regionid = request.session['regionid']
    warehouseid =  request.session['warehouseid']
    depoid =  request.session['depoid']
    role = request.session['role']
    if role == 'Admin':
        url = "http://13.235.112.1/ziva/mobile-api/adminstoremaster-list.php"

        payload = json.dumps({
            "accesskey": accesskey,
            "warehouseid": 'All',
            "regionid": 'All',
            "depoid": 'All',
            "busstationid": request.POST.get('busid')

        })
        headers = {
            'Content-Type': 'application/json'
        }


        response = requests.request("GET", url, headers=headers, data=payload)
        if response.status_code == 200:
            data2 = response.json()
            return JsonResponse({'data': data2})
        elif response.status_code == 400:
            data = response.json()
            if data['message'] == 'Sorry! some details are missing':
                return JsonResponse({'data': data})
            else:
                messages.error(request, data['message'])
                return redirect('/login')
        elif response.status_code == 503:
            data = response.json()
            return JsonResponse({'data': data})
        elif response.status_code == 500:
            data = {'error': 'true', 'message': 'Internal server error'}
            return JsonResponse({'data': data})
        else:
            data = {'error': 'true', 'message': 'something went wrong'}
            return JsonResponse({'data': data})
    else:
        url = "http://13.235.112.1/ziva/mobile-api/adminstoremaster-list.php"

        payload = json.dumps({
            "accesskey": accesskey,
            "warehouseid": warehouseid,
            "regionid": regionid,
            "depoid": request.POST.get('depo'),
            "busstationid": request.POST.get('busid')

        })
        headers = {
            'Content-Type': 'application/json'
        }

        response = requests.request("GET", url, headers=headers, data=payload)
        if response.status_code == 200:
            data2 = response.json()
            return JsonResponse({'data': data2})
        elif response.status_code == 400:
            data = response.json()
            if data['message'] == 'Sorry! some details are missing':
                return JsonResponse({'data': data})
            else:
                messages.error(request, data['message'])
                return redirect('/login')
        elif response.status_code == 503:
            data = response.json()
            return JsonResponse({'data': data})
        elif response.status_code == 500:
            data = {'error': 'true', 'message': 'Internal server error'}
            return JsonResponse({'data': data})
        else:
            data = {'error': 'true', 'message': 'something went wrong'}
            return JsonResponse({'data': data})

def get_storedepo(request):
     if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
     accesskey = request.session['accesskey']
     warehouse = request.POST.get('warehouse')
     region = request.POST.get('region')
     if region:
         region=region
     else:
         region = "All"

     if warehouse:
        warehouse = warehouse
     else:
        warehouse = 'All'

     url = "http://13.235.112.1/ziva/mobile-api/dropdownlist-storemaster-all.php"

     payload = json.dumps({"accesskey": accesskey, "type": "Depo",
                           "warehousename": warehouse,
                           "regionid": region,
                           "depoid": ""})
     headers = {
         'Content-Type': 'text/plain'
     }
     response = requests.request("GET", url, headers=headers, data=payload)
     if response.status_code == 200:
         data2 = response.json()
         return JsonResponse({'data': data2})
     elif response.status_code == 400:
         data = response.json()
         if data['message'] == 'Sorry! some details are missing':
             return JsonResponse({'data': data})
         else:
             messages.error(request, data['message'])
             return redirect('/login')
     elif response.status_code == 503:
         data = response.json()
         return JsonResponse({'data': data})
     elif response.status_code == 500:
         data = {'error': 'true', 'message': 'Internal server error'}
         return JsonResponse({'data': data})
     else:
         data = {'error': 'true', 'message': 'something went wrong'}
         return JsonResponse({'data': data})



def get_depregion(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    accesskey = request.session['accesskey']
    warehouse = request.POST.get('warehouse')
    url = "http://13.235.112.1/ziva/mobile-api/dependent-region-list.php"

    payload = json.dumps({"accesskey": accesskey, "warehousename": warehouse})
    headers = {
        'Content-Type': 'text/plain'
    }
    response = requests.request("GET", url, headers=headers, data=payload)
    if response.status_code == 200:
        data2 = response.json()
        return JsonResponse({'data': data2})
    elif response.status_code == 400:
        data = response.json()
        if data['message'] == 'Sorry! some details are missing':
            return JsonResponse({'data': data})
        else:
            messages.error(request, data['message'])
            return redirect('/login')
    elif response.status_code == 503:
        data = response.json()
        return JsonResponse({'data': data})
    elif response.status_code == 500:
        data = {'error': 'true', 'message': 'Internal server error'}
        return JsonResponse({'data': data})
    else:
        data = {'error': 'true', 'message': 'something went wrong'}
        return JsonResponse({'data': data})

def get_dependent_depo(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    accesskey = request.session['accesskey']
    url = "http://13.235.112.1/ziva/mobile-api/dropdownlist.php"

    payload = json.dumps({"accesskey": accesskey,
                          "warehousename": request.POST.get('warehouse'),
                          "role": request.POST.get('role'),
                          "type": "Depo",
                          "regionid": request.POST.get('region'),
                          "depoid": ""
                          })
    headers = {
        'Content-Type': 'text/plain'
    }
    response = requests.request("GET", url, headers=headers, data=payload)
    if response.status_code == 200:
        data2 = response.json()
        return JsonResponse({'data': data2})
    elif response.status_code == 400:
        data = response.json()
        if data['message'] == 'Sorry! some details are missing':
            return JsonResponse({'data': data})
        else:
            messages.error(request, data['message'])
            return redirect('/login')
    elif response.status_code == 503:
        data = response.json()
        return JsonResponse({'data': data})
    elif response.status_code == 500:
        data = {'error': 'true', 'message': 'Internal server error'}
        return JsonResponse({'data': data})
    else:
        data = {'error': 'true', 'message': 'something went wrong'}
        return JsonResponse({'data': data})

def get_dependent_bus(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    accesskey = request.session['accesskey']
    url = "http://13.235.112.1/ziva/mobile-api/dropdownlist.php"

    payload = json.dumps({"accesskey": accesskey,
                          "warehousename": request.POST.get('warehouse'),
                          "role": request.POST.get('role'),
                          "type": "busstation",
                          "regionid": request.POST.get('region'),
                          "depoid": request.POST.get('depo')
                          })
    headers = {
        'Content-Type': 'text/plain'
    }
    response = requests.request("GET", url, headers=headers, data=payload)
    if response.status_code == 200:
        data2 = response.json()
        return JsonResponse({'data': data2})
    elif response.status_code == 400:
        data = response.json()
        if data['message'] == 'Sorry! some details are missing':
            return JsonResponse({'data': data})
        else:
            messages.error(request, data['message'])
            return redirect('/login')
    elif response.status_code == 503:
        data = response.json()
        return JsonResponse({'data': data})
    elif response.status_code == 500:
        data = {'error': 'true', 'message': 'Internal server error'}
        return JsonResponse({'data': data})
    else:
        data = {'error': 'true', 'message': 'something went wrong'}
        return JsonResponse({'data': data})

def user_add(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    try:
        menuname = request.session['mylist']
        accesskey = request.session['accesskey']

        url = "http://13.235.112.1/ziva/mobile-api/warehousemaster-list.php"

        payload = json.dumps({
            "accesskey": accesskey
        })
        headers = {
            'Content-Type': 'text/plain'
        }
        response = requests.request("GET", url, headers=headers, data=payload)
        data = response.json()
        wh_masterlist = data['warehouselist']
        url = "http://13.235.112.1/ziva/mobile-api/dropdwn-table-list.php"

        payload = json.dumps({
            "accesskey": accesskey,
            "name": "DESIGNATION"
        })
        headers = {
            'Content-Type': 'application/json'
        }

        response1 = requests.request("GET", url, headers=headers, data=payload)
        data = response1.json()
        des_list = data['itemmasterlist']


        url = "http://13.235.112.1/ziva/mobile-api/role-dropdownlist.php"

        payload = json.dumps({"accesskey": accesskey})
        headers = {
            'Content-Type': 'text/plain'
        }

        response3 = requests.request("GET", url, headers=headers, data=payload)
        data2 = response3.json()
        role_list = data2['roledropdownlist']



        url = "http://13.235.112.1/ziva/mobile-api/dropdwn-table-list.php"

        payload = json.dumps({"accesskey": accesskey,  "name":"LEVEL"})
        headers = {
            'Content-Type': 'text/plain'
        }
        response4 = requests.request("GET", url, headers=headers, data=payload)
        data3 = response4.json()
        level_list = data3['itemmasterlist']

        if request.method == "POST":
            image = request.FILES.get("image")
            if image:
                image_data = base64.b64encode(image.read())
                image_name = request.FILES.get("image").name

            else:
                image_data = None
                image_name = None

            url = "http://13.235.112.1/ziva/mobile-api/create-user-new.php"

            payload = {
                "accesskey": accesskey,
                "username": request.POST.get('username'),
                "mobile": request.POST.get('mobile'),
                "userid": request.POST.get('uid'),
                "emailid": request.POST.get('email'),
                "region": request.POST.get('regionname'),
                "regionid": request.POST.get('region'),
                "warehouseid" : request.POST.get('warehouse'),
                "warehousename": request.POST.get('warehousename'),
                "depo": request.POST.get('depo'),
                "level": request.POST.get('level'),
                 "role": request.POST.get('role'),
                 "userattachfilename":image_name,
                 "designation": "",
                 "deponame":request.POST.get('deponame'),
                 "depoid": request.POST.get('depo'),
                 "busstationname":request.POST.get('busstationname'),
                 "busstationid": request.POST.get('busstation'),
                "userimage": image_data
            }
            headers = {
                'Content-Type': 'application/json'
            }
            payload = json.dumps(payload, cls=BytesEncoder)
            response = requests.request("GET", url, headers=headers, data=payload)

            if response.status_code == 200:
                r = response.json()
                messages.success(request, r['message'])
                return redirect('user_list')
            elif response.status_code == 400:
                data = response.json()
                text = data['message']
                if "some details are missing" in text:
                    messages.error(request, data['message'])
                    return redirect('user_add')
                else:
                    messages.error(request, data['message'])
                    return redirect('/login')
            else:
                try:
                    r = response.json()
                    messages.error(request, r['message'])
                except:
                    messages.error(request, response.text)
            return redirect('user_add')
        return render(request, 'user/user_add.html',
                      {'all_data': des_list,'all_data2': role_list, 'all_data3': level_list,'data':wh_masterlist,'menuname':menuname})
    except:

        if response.status_code == 400:
            messages.error(request, data['message'])
            return redirect('/login')
    messages.error(request,response.text)
    return render(request, 'user/user_add.html')

def user_edit(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    if request.method == "POST":
        accesskey = request.session['accesskey']
        url = "http://13.235.112.1/ziva/mobile-api/edit-user.php"
        payload = json.dumps({
            "accesskey": accesskey,
            "username": request.POST.get('username'),
            "mobile": request.POST.get('mobile'),
            "userid": request.POST.get('uid'),
            "emailid": request.POST.get('email'),
            "region": request.POST.get('regionname'),
            "regionid": request.POST.get('regionid'),
            "warehouseid": request.POST.get('warehouseid'),
            "warehousename": request.POST.get('warehousename'),
            "level": request.POST.get('levelname'),
            "role": request.POST.get('role'),
            "userattachfilename": "",
            "designation": "",
            "deponame": request.POST.get('deponame'),
            "depoid": request.POST.get('depoid'),
            "busstationname": request.POST.get('busstationname'),
            "busstationid": request.POST.get('busstationid'),
            "userimage": ""
        })
        headers = {
            'Content-Type': 'application/json'
        }

        response = requests.request("GET", url, headers=headers, data=payload)



        if response.status_code == 200:
            data = response.json()
            messages.success(request, data['message'])
            return redirect('user_list')
        elif response.status_code == 400:
            data = response.json()
            text = data['message']
            if 'some details are missing' in text:
                messages.error(request, data['message'])
                return redirect('/user_list')
            else:
                messages.error(request, data['message'])
                return redirect('/login')
        else:
            try:
                r = response.json()
                messages.error(request, r['message'])
            except:
                messages.error(request, response.text)
            return redirect('/user_list')
    return redirect('/user_list')


def user_list(request):
    try:
            if 'accesskey' not in request.session:
                messages.error(request, 'Access denied!')
                return redirect('/login')
            menuname = request.session['mylist']
            accesskey = request.session['accesskey']
            url = "http://13.235.112.1/ziva/mobile-api/role-dropdownlist.php"

            payload = json.dumps({"accesskey": accesskey})
            headers = {
                'Content-Type': 'text/plain'
            }

            response = requests.request("GET", url, headers=headers, data=payload)
            data2 = response.json()
            role_list = data2['roledropdownlist']
            url = "http://13.235.112.1/ziva/mobile-api/dropdwn-table-list.php"

            payload = json.dumps({"accesskey": accesskey, "name": "LEVEL"})
            headers = {
                'Content-Type': 'text/plain'
            }
            response = requests.request("GET", url, headers=headers, data=payload)
            data3 = response.json()
            level_list = data3['itemmasterlist']
            url = "http://13.235.112.1/ziva/mobile-api/user-list.php"

            payload = json.dumps({
                    "accesskey": accesskey
                })
            headers = {
                    'Content-Type': 'application/json'
                }

            response = requests.request("GET", url, headers=headers, data=payload)
            if response.status_code == 200:
                    data = response.json()
                    user_list = data['userlist']
                    return render(request, 'user/user_list.html', {"list": user_list,'menuname':menuname,'role_list':role_list,'level_list':level_list})
            if response.status_code == 400:
                    data = response.json()
                    messages.error(request,data['message'])
                    return redirect('/login')
            else:
                    return render(request, 'user/user_list.html',{'menuname':menuname,'role_list':role_list,'level_list':level_list})
    except Exception as e:
        if response.status_code == '400':
            data = response.json()
            messages.error(request, data['message'])
            return redirect('/login')
    messages.error(request,response.text)
    return render(request, 'user/user_list.html', {"menuname": menuname})

def user_status_active(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    accesskey = request.session['accesskey']
    url = "http://13.235.112.1/ziva/mobile-api/status-change.php"

    payload = json.dumps({
        "accesskey": accesskey,
        "sno": request.POST.get('id'),
        "type": "Logins",
        "status": "Inactive"
    })
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    if response.status_code == 200:
        data = response.json()
        messages.success(request, data['message'])
        return redirect('user_list')
    else:
        try:
            data = response.json()
            messages.error(request, data['message'])
            return redirect('user_list')
        except:
            messages.error(request, data['message'])
        return redirect('user_list')


def user_status_inactive(request, id):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    url = "http://13.235.112.1/ziva/mobile-api/status-change.php"

    payload = json.dumps({
        "accesskey": "LTIwMjIxMjE5MjIyMzcy",
        "sno": id,
        "type": "Logins",
        "status": "Active"
    })
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)


    if response.status_code == 200:
        data = response.json()
        messages.success(request, data['message'])
        return redirect('user_list')
    else:
        data = response.json()
        messages.error(request, data['message'])
        return redirect('user_list')


def add_grn(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    try:
        accesskey = request.session['accesskey']
        whname = request.session['warehousename']
        menuname = request.session['mylist']
        warehouseid = request.session['warehouseid']
        role = request.session['role']
        url = "http://13.235.112.1/ziva/mobile-api/vendormasterlist.php"

        payload = json.dumps({"accesskey":accesskey})
        headers = {
            'Content-Type': 'text/plain'
        }
        response = requests.request("GET", url, headers=headers, data=payload)
        data = response.json()
        vendor_masterlist = data['vendormasterlist']

        url = "http://13.235.112.1/ziva/mobile-api/warehousemaster-list.php"
        payload = json.dumps({"accesskey": accesskey})
        headers = {
            'Content-Type': 'text/plain'
        }
        response = requests.request("GET", url, headers=headers, data=payload)
        data = response.json()
        wh_masterlist = data['warehouselist']
        if role == 'Admin':
            if request.method == "POST":
                invoiceattach = request.FILES.get("invoiceimage")
                if invoiceattach:
                    invoiceimage_data = base64.b64encode(invoiceattach.read())
                    invoiceimage_name = request.FILES.get("invoiceimage").name

                else:
                    invoiceimage_data = None
                    invoiceimage_name = None

                url = "http://13.235.112.1/ziva/mobile-api/create-grn-admin.php"
                payload = {
                    "accesskey": accesskey,
                    "vendorname": request.POST.get('vname'),
                    "invoiceno": request.POST.get('invno'),
                    "invoicedate": request.POST.get('invoicedate'),
                    "invoiceamount": request.POST.get('invoiceamount'),
                    "vendorid": request.POST.get('vid'),
                    "invoicephoto":invoiceimage_data,
                    "invoiceattachfilename":invoiceimage_name,
                    "whcode": request.POST.get('whid')
                }
                payload = json.dumps(payload, cls=BytesEncoder)
                headers = {
                    'Content-Type': 'application/json'
                }

                r = requests.post(url, payload, headers=headers)

                if r.status_code == 200:
                    data2 = r.json()
                    grn = data2['grnnumber']
                    messages.success(request, data2['message'])
                    url = reverse('add_grnitem', args=[grn])
                    return redirect(url)
                else:
                    data2 = r.json()
                    messages.error(request, data2['message'])
                    return redirect('add_grn')
            else:
                return render(request, 'grn/add_grn.html',
                              {'all_data': vendor_masterlist, 'whname': whname, 'menuname': menuname,'all_data1':wh_masterlist})
        else:

                    if request.method == "POST":
                        invoiceimage = request.FILES.get("invoiceimage")

                        if invoiceimage:
                            invoiceattach_data = base64.b64encode(invoiceimage.read())
                            invoiceattach_name = request.FILES.get("invoiceimage").name

                        else:
                            invoiceattach_data = None
                            invoiceattach_name = None
                        url = "http://13.235.112.1/ziva/mobile-api/create-grn.php"
                        payload ={
                            "accesskey": accesskey,
                            "vendorname": request.POST.get('vname'),
                            "invoiceno": request.POST.get('invno'),
                            "invoicedate": request.POST.get('invoicedate'),
                            "invoiceamount": request.POST.get('invoiceamount'),
                            "vendorid": request.POST.get('vid'),
                            "invoicephoto": invoiceattach_data,
                            "invoiceattachfilename": invoiceattach_name,
                            "whcode": request.POST.get('wh_id'),
                        }
                        payload = json.dumps(payload, cls=BytesEncoder)
                        headers = {
                            'Content-Type': 'application/json'
                        }

                        r = requests.post(url, payload, headers=headers)

                        if r.status_code == 200:
                            data2 = r.json()
                            grn = data2['grnnumber']
                            messages.success(request, data2['message'])
                            url = reverse('add_grnitem', args=[grn])
                            return redirect(url)
                        else:
                            data2 = r.json()
                            messages.error(request, data2['message'])
                            return redirect('add_grn')
                    else:
                        return render(request, 'grn/add_grn.html', {'all_data': vendor_masterlist, 'whname': whname,'menuname':menuname,'all_data1':wh_masterlist})
    except Exception as e:
        messages.error(request, str(e))
        return render(request, 'grn/add_grn.html', {'menuname': menuname})


def delete_grn_item(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    accesskey = request.session['accesskey']
    url = "http://13.235.112.1/ziva/mobile-api/delete-grnitem.php"
    id = request.POST.get('deletesono')
    payload = json.dumps({
        "accesskey": accesskey,
        "sno": request.POST.get('deleteid'),
        "grn": id,
    })
    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.request("GET", url, headers=headers, data=payload)
    if response.status_code == 200:
        data = response.json()
        messages.success(request, data['message'])
        url = reverse('add_grnitem', args=[id])
        return redirect(url)
    elif response.status_code == 400:
        data = response.json()
        if data['message'] == 'Sorry! some details are missing':
            messages.error(request, data['message'])
            url = reverse('add_grnitem', args=[id])
            return redirect(url)
        else:
            messages.error(request, data['message'])
            return redirect('/login')
    else:
        try:
            data = response.json()
            messages.error(request, data['message'])
        except:
            messages.error(request, response.text)
        url = reverse('add_grnitem', args=[id])
        return redirect(url)


def indent_item_update(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    accesskey = request.session['accesskey']
    if request.method == "POST":
        id = request.POST.get('indentno')
        url = "http://13.235.112.1/ziva/mobile-api/edit-indentitem-admin.php"

        payload = json.dumps({

            "accesskey": accesskey,
            "indent_no":request.POST.get('indentno'),
            "sno":request.POST.get('indsno'),
            "item_code":request.POST.get('itemcode'),
            "item_name":request.POST.get('itemname'),
            "qty":request.POST.get('qty'),
            "mrp":request.POST.get('price')
        })
        headers = {
            'Content-Type': 'application/json'
        }

        response = requests.request("GET", url, headers=headers, data=payload)

        data = response.json()

        if response.status_code == 200:
            messages.success(request, data['message'])
            url = reverse('indent_item_list', args=[id])
            return redirect(url)
        elif response.status_code == 400:
            data = response.json()
            if data['message'] == 'Sorry! some details are missing':
                messages.error(request, data['message'])
                url = reverse('indent_item_list', args=[id])
                return redirect(url)
            else:
                messages.error(request, data['message'])
                return redirect('/login')

    else:

        url = reverse('indent_item_list', args=[id])
        return redirect(url)



def edit_grn(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    accesskey = request.session['accesskey']
    if request.method == "POST":
        url = "http://13.235.112.1/ziva/mobile-api/edit-grn-admin.php"

        payload = json.dumps({

            "accesskey": accesskey,
            "grn":request.POST.get('grn'),
            "vendorname": request.POST.get('vname'),
            "invoice_id": request.POST.get('invno'),
            "invoice_date": request.POST.get('invoicedate'),
            "invoice_amount": request.POST.get('invoiceamount'),
            "vendorid": request.POST.get('vid'),
            "warehouse_id":request.POST.get('whid')
        })
        headers = {
            'Content-Type': 'application/json'
        }

        response = requests.request("GET", url, headers=headers, data=payload)

        data = response.json()

        if response.status_code == 200:
            messages.success(request, data['message'])
            return redirect('grn_list1')
        elif response.status_code == 400:
            data = response.json()
            if data['message'] == 'Sorry! some details are missing':
                messages.error(request, data['message'])
                return redirect('/grn_list1')
            else:
                messages.error(request, data['message'])
                return redirect('grn_list1')

    else:
            return redirect('grn_list1')
    return redirect('grn_list1')

def edit_grn_item(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    accesskey = request.session['accesskey']

    if request.method == "POST":
        id = request.POST.get('grn')
        url = "http://13.235.112.1/ziva/mobile-api/edit-grnitem-admin.php"

        payload = json.dumps({
            "accesskey": accesskey,
            "grn": request.POST.get('grn'),
            "sno":request.POST.get('id'),
            "item_name": request.POST.get('itemname1'),
            "item_code": request.POST.get('itemcode'),
            "quantity": request.POST.get('quantity'),
            "batch_no": request.POST.get('batchno'),
            "expiry_date": request.POST.get('result'),
            "purchase_price": request.POST.get('latestpurchase'),
            "mrp": request.POST.get('mrp'),
            "uom": request.POST.get('uom'),

        })
        headers = {
            'Content-Type': 'application/json'
        }

        response = requests.request("GET", url, headers=headers, data=payload)

        data = response.json()

        if response.status_code == 200:
            messages.success(request, data['message'])
            url = reverse('add_grnitem', args=[id])
            return redirect(url)

        elif response.status_code == 400:
            data = response.json()
            text = data['message']
            if 'some details are missing' in text:
                messages.error(request, data['message'])
                url = reverse('add_grnitem', args=[id])
                return redirect(url)
            else:
                messages.error(request, data['message'])
                return redirect('/login')
        else:
            try:
                data = response.json()
                messages.error(request, data['message'])
            except:
                messages.error(request, response.text)
            url = reverse('add_grnitem', args=[id])
            return redirect(url)

    else:
        url = reverse('add_grnitem', args=[id])
        return redirect(url)


def grn_search(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    accesskey = request.session['accesskey']
    url = "http://13.235.112.1/ziva/mobile-api/grn-searchlist.php"

    payload = json.dumps({
        "accesskey": accesskey,
        "status":request.POST.get('status'),
        "searchterm": request.POST.get('id')
    })

    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    if response.status_code == 200:
        data2 = response.json()
        return JsonResponse({'data': data2})
    elif response.status_code == 400:
        data = response.json()
        if data['message'] == 'Sorry! some details are missing':
            messages.error(request, data['message'])
            return redirect('/grn_list1')
        else:
            messages.error(request, data['message'])
            return redirect('/login')
    else:
        return redirect('/grn_list1')


def add_grnitem(request,id):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    try:
        accesskey = request.session['accesskey']
        menuname = request.session['mylist']
        url = "http://13.235.112.1/ziva/mobile-api/itemmaster-list.php"

        payload = json.dumps({"accesskey":accesskey})
        headers = {
            'Content-Type': 'application/json'
        }
        response = requests.request("GET", url, headers=headers, data=payload)
        data = response.json()
        item_masterlist = data['itemmasterlist']

        role = request.session['role']


        if role == 'Admin':
            if request.method == "POST":
                url = "http://13.235.112.1/ziva/mobile-api/grn-item-admin.php"
                payload = {
                    "accesskey": accesskey,
                    "grnnumber": id,
                    "itemname": request.POST.get('txtItemName'),
                    "itemcode": request.POST.get('itemname'),
                    "hsncode": "",
                    "qty": request.POST.get('quantity'),
                    "batchno": request.POST.get('batchno'),
                    "expdate": request.POST.get('result'),
                    "purchaseprice": request.POST.get('latestpurchase'),
                    "mrp": request.POST.get('mrp'),
                    "freeqty": "",
                    "gst": " ",
                    "uom": request.POST.get('uom'),
                    "manufacturer": request.POST.get('manufacture'),
                    "itemsno": request.POST.get('itemsno')
                }
                payload = json.dumps(payload, cls=BytesEncoder)
                headers = {
                    'Content-Type': 'application/json'
                }
                r = requests.post(url, payload, headers=headers)

                if r.status_code == 200:
                    r1 = r.json()
                    messages.success(request, r1['message'])
                    url = "http://13.235.112.1/ziva/mobile-api/grn-item-list.php"

                    payload = json.dumps({
                        "accesskey": accesskey,
                        "grnno": id
                    })
                    headers = {
                        'Content-Type': 'text/plain'
                    }

                    response = requests.request("GET", url, headers=headers, data=payload)
                    if response.status_code == 200:
                        data = response.json()
                        grn_item_list = data['grnitemlist']

                        return render(request, 'grn/add_grnitem.html',
                                      {'all_data': grn_item_list, 'data': item_masterlist, 'menuname': menuname, 'id': id,'response':200})
                    elif response.status_code == 503:
                        try:
                            data = response.json()
                            grn_item_list = data['grnitemlist']
                            messages.success(request, r1['message'])
                            return render(request, 'grn/add_grnitem.html',
                                          {'all_data': grn_item_list, 'data': item_masterlist, 'menuname': menuname, 'id': id,'response':200})
                        except:
                            return render(request, 'grn/add_grnitem.html',
                                          {'data': item_masterlist, 'menuname': menuname,
                                           'id': id, 'response': 200})
                    else:
                        return render(request, 'grn/add_grnitem.html',
                                      {'data': item_masterlist, 'menuname': menuname,
                                       'id': id, 'response': 200})
                elif r.status_code == 400:
                    r1 = r.json()
                    if r1['message'] == 'Sorry! some details are missing':
                        messages.error(request, data['message'])
                        url = "http://13.235.112.1/ziva/mobile-api/grn-item-list.php"

                        payload = json.dumps({
                            "accesskey": accesskey,
                            "grnno": id
                        })
                        headers = {
                            'Content-Type': 'text/plain'
                        }

                        response = requests.request("GET", url, headers=headers, data=payload)
                        if response.status_code == '200':
                            data = response.json()
                            grn_item_list = data['grnitemlist']
                            return render(request, 'grn/add_grnitem.html',
                                          {'all_data': grn_item_list, 'data': item_masterlist, 'menuname': menuname,
                                           'id': id,
                                           'response': 200})

                        elif response.status_code == 503:
                            try:
                                data = response.json()
                                grn_item_list = data['grnitemlist']
                                return render(request, 'grn/add_grnitem.html',
                                              {'all_data': grn_item_list, 'data': item_masterlist, 'menuname': menuname,
                                               'id': id,
                                               'response': 200})
                            except:
                                return render(request, 'grn/add_grnitem.html',
                                              {'data': item_masterlist, 'menuname': menuname,
                                               'id': id,
                                               'response': 200})
                        else:
                            return render(request, 'grn/add_grnitem.html',
                                          { 'data': item_masterlist, 'menuname': menuname,
                                           'id': id,
                                           'response': 200})
                    else:
                        messages.error(request, data['message'])
                        return redirect('/login')
                else:
                    try:
                        r1 = r.json()
                        messages.error(request, r1['message'])
                        url = "http://13.235.112.1/ziva/mobile-api/grn-item-list.php"

                        payload = json.dumps({
                            "accesskey": accesskey,
                            "grnno": id
                        })
                        headers = {
                            'Content-Type': 'text/plain'
                        }

                        response = requests.request("GET", url, headers=headers, data=payload)
                        if response.status_code == 200:
                            data = response.json()
                            grn_item_list = data['grnitemlist']

                            return render(request, 'grn/add_grnitem.html',
                                          {'all_data':grn_item_list,'data': item_masterlist, 'menuname': menuname,'id':id,'response':400})
                        elif response.status_code == 503:
                            try:
                                data = response.json()
                                grn_item_list = data['grnitemlist']
                                return render(request, 'grn/add_grnitem.html',
                                              {'all_data': grn_item_list, 'data': item_masterlist, 'menuname': menuname,
                                               'id': id,
                                               'response': 400})
                            except:
                                return render(request, 'grn/add_grnitem.html',
                                              {'data': item_masterlist, 'menuname': menuname,
                                               'id': id, 'response': 400})
                    except:
                        messages.error(request,"some thing went wrong !")
                        return render(request, 'grn/add_grnitem.html',
                                      {'data': item_masterlist, 'menuname': menuname,
                                       'id': id, 'response': 400})
            else:
                url = "http://13.235.112.1/ziva/mobile-api/grn-item-list.php"

                payload = json.dumps({
                    "accesskey": accesskey,
                    "grnno": id
                })
                headers = {
                    'Content-Type': 'text/plain'
                }

                response = requests.request("GET", url, headers=headers, data=payload)
                if response.status_code == 200:
                    data = response.json()
                    grn_item_list = data['grnitemlist']
                    return render(request, 'grn/add_grnitem.html',
                                  {'all_data': grn_item_list, 'data': item_masterlist, 'menuname': menuname, 'id': id,
                                   'response': 400})
                elif response.status_code == 503:
                    try:
                        data = response.json()
                        grn_item_list = data['grnitemlist']
                        return render(request, 'grn/add_grnitem.html',
                                      {'all_data': grn_item_list, 'data': item_masterlist, 'menuname': menuname, 'id': id,
                                       'response': 400})
                    except:
                        return render(request, 'grn/add_grnitem.html',
                                      {'data': item_masterlist, 'menuname': menuname,
                                       'id': id, 'response': 400})
                else:
                    return render(request, 'grn/add_grnitem.html',
                                          {'data': item_masterlist, 'menuname': menuname,
                                           'id': id, 'response': 400})


        else:
            if request.method == 'POST':
                url = "http://13.235.112.1/ziva/mobile-api/grn-item.php"
                payload = {
                        "accesskey": accesskey,
                        "grnnumber": id,
                        "itemname": request.POST.get('txtItemName'),
                        "itemcode": request.POST.get('itemname'),
                        "hsncode":"",
                        "qty": request.POST.get('quantity'),
                        "batchno": request.POST.get('batchno'),
                        "expdate": request.POST.get('result'),
                        "purchaseprice": request.POST.get('latestpurchase'),
                        "mrp":request.POST.get('mrp'),
                        "freeqty": "",
                        "gst": " ",
                        "uom": request.POST.get('uom'),
                        "manufacturer": request.POST.get('manufacture'),
                        "itemsno": request.POST.get('itemsno')
                    }
                payload = json.dumps(payload, cls=BytesEncoder)
                headers = {
                        'Content-Type': 'application/json'
                    }
                r = requests.post(url, payload, headers=headers)

                if r.status_code == 200:
                        r1 = r.json()
                        messages.success(request, r1['message'])
                        url = "http://13.235.112.1/ziva/mobile-api/grn-item-list.php"

                        payload = json.dumps({
                            "accesskey": accesskey,
                            "grnno": id
                        })
                        headers = {
                            'Content-Type': 'text/plain'
                        }

                        response = requests.request("GET", url, headers=headers, data=payload)
                        if response.status_code == 200:
                            data = response.json()
                            grn_item_list = data['grnitemlist']
                            return render(request, 'grn/add_grnitem.html', {'all_data': grn_item_list,'data': item_masterlist,'menuname':menuname,'id':id,'response':200})
                        elif response.status_code == 503:
                            data = response.json()
                            grn_item_list = data['grnitemlist']
                            return render(request, 'grn/add_grnitem.html',
                                          {'all_data': grn_item_list, 'data': item_masterlist, 'menuname': menuname,
                                           'id': id, 'response': 200})
                        else:
                            return render(request, 'grn/add_grnitem.html',
                                          { 'data': item_masterlist, 'menuname': menuname,
                                           'id': id,  'response': 200})
                elif r.status_code == 400:
                        r1 = r.json()
                        if r1['message'] == 'Sorry! some details are missing':
                            messages.error(request, r1['message'])
                            url = "http://13.235.112.1/ziva/mobile-api/grn-item-list.php"

                            payload = json.dumps({
                                "accesskey": accesskey,
                                "grnno": id
                            })
                            headers = {
                                'Content-Type': 'text/plain'
                            }

                            response = requests.request("GET", url, headers=headers, data=payload)
                            if response.status_code == 200:
                                data = response.json()
                                grn_item_list = data['grnitemlist']
                                return render(request, 'grn/add_grnitem.html',
                                              {'all_data': grn_item_list, 'data': item_masterlist, 'menuname': menuname, 'id': id,
                                              'response': 200})
                            elif response.status_code == 503:
                                data = response.json()
                                grn_item_list = data['grnitemlist']
                                return render(request, 'grn/add_grnitem.html',
                                              {'all_data': grn_item_list, 'data': item_masterlist, 'menuname': menuname,
                                               'id': id,
                                               'response': 200})
                            else:
                                return render(request, 'grn/add_grnitem.html',
                                              {'data': item_masterlist, 'menuname': menuname,'id': id,'response': 200})
                        else:
                            messages.error(request, r1['message'])
                            return redirect('/login')

                else:
                    try:
                        r1 = r.json()
                        messages.success(request, r1['message'])
                        url = "http://13.235.112.1/ziva/mobile-api/grn-item-list.php"

                        payload = json.dumps({
                            "accesskey": accesskey,
                            "grnno": id
                        })
                        headers = {
                            'Content-Type': 'text/plain'
                        }

                        response = requests.request("GET", url, headers=headers, data=payload)
                        if response.status_code == 200:
                            data = response.json()
                            grn_item_list = data['grnitemlist']
                            return render(request, 'grn/add_grnitem.html',
                                          {'all_data': grn_item_list, 'data': item_masterlist, 'menuname': menuname,
                                           'id': id, 'response': 400})
                        elif response.status_code == 503:
                            try:
                                data = response.json()
                                grn_item_list = data['grnitemlist']
                                return render(request, 'grn/add_grnitem.html',
                                              {'all_data': grn_item_list, 'data': item_masterlist, 'menuname': menuname,
                                               'id': id, 'response': 400})
                            except:
                               pass
                            return render(request, 'grn/add_grnitem.html',
                                          {'data': item_masterlist, 'menuname': menuname,
                                           'id': id, 'response': 400})
                        else:
                            return render(request, 'grn/add_grnitem.html',
                                          {'data': item_masterlist, 'menuname': menuname, 'id': id, 'response': 400})
                    except:
                        messages.error(request,"something went wrong")
                        return render(request, 'grn/add_grnitem.html',
                                      {'data': item_masterlist, 'menuname': menuname, 'id': id, 'response': 400})
            else:
                url = "http://13.235.112.1/ziva/mobile-api/grn-item-list.php"

                payload = json.dumps({
                    "accesskey": accesskey,
                    "grnno": id
                })
                headers = {
                    'Content-Type': 'text/plain'
                }

                response = requests.request("GET", url, headers=headers, data=payload)
                if response.status_code == 200:
                    data = response.json()
                    grn_item_list = data['grnitemlist']
                    return render(request, 'grn/add_grnitem.html',
                                  {'all_data': grn_item_list, 'data': item_masterlist, 'menuname': menuname, 'id': id,
                                   'response': 400})
                elif response.status_code == 503:
                    try:
                        data = response.json()
                        grn_item_list = data['grnitemlist']
                        return render(request, 'grn/add_grnitem.html',
                                      {'all_data': grn_item_list, 'data': item_masterlist, 'menuname': menuname,
                                       'id': id,
                                       'response': 400})
                    except:
                        return render(request, 'grn/add_grnitem.html',
                                      {'data': item_masterlist, 'menuname': menuname,
                                       'id': id, 'response': 400})
                else:
                    return render(request, 'grn/add_grnitem.html',
                                  {'data': item_masterlist, 'menuname': menuname,
                                   'id': id, 'response': 400})
    except:
        if response.status_code == 400:
            data = response.json()
            messages.error(request,data['message'])
            return redirect('/login')
    messages.error(request, response.text)
    return render(request, 'grn/add_grnitem.html',{'menuname':menuname,'data': item_masterlist})

def add_grnitem_list(request,id):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    try:
        menuname = request.session['mylist']
        accesskey = request.session['accesskey']

        url = "http://13.235.112.1/ziva/mobile-api/itemmaster-list-new.php"

        payload = json.dumps({"accesskey": accesskey})
        headers = {
            'Content-Type': 'application/json'
        }
        response = requests.request("GET", url, headers=headers, data=payload)
        data = response.json()
        item_masterlist = data['itemmasterlist']

        url = "http://13.235.112.1/ziva/mobile-api/grn-item-list.php"

        payload = json.dumps({
            "accesskey": accesskey,
            "grnno": id
        })
        headers = {
            'Content-Type': 'text/plain'
        }

        response = requests.request("GET", url, headers=headers, data=payload)
        if response.status_code == 200:
            data = response.json()
            grn_item_list = data['grnitemlist']
            return render(request, 'grn/add_grnitem_list.html', {'all_data': grn_item_list,'menuname':menuname,'id':id,'item_masterlist':item_masterlist})
        elif response.status_code == 400:
            data = response.json()
            if data['message'] == 'Sorry! some details are missing':
                messages.error(request, data['message'])
                return render(request, 'grn/add_grnitem_list.html',{'menuname':menuname,'id':id,'item_masterlist':item_masterlist})
            else:
                messages.error(request, data['message'])
                return redirect('/login')
        else:
            return render(request, 'grn/add_grnitem_list.html',{'menuname':menuname,'id':id,'item_masterlist':item_masterlist})
    except:
        if response.status_code == 400:
            data = response.json()
            messages.error(request, data['message'])
            return redirect('/login')
    return render(request, 'grn/add_grnitem_list.html', {'menuname': menuname})


def add_grnitem_list1(request,id):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    menuname = request.session['mylist']
    accesskey = request.session['accesskey']

    url = "http://13.235.112.1/ziva/mobile-api/itemmaster-list.php"

    payload = json.dumps({"accesskey": accesskey})
    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.request("GET", url, headers=headers, data=payload)
    data = response.json()
    item_masterlist = data['itemmasterlist']

    url = "http://13.235.112.1/ziva/mobile-api/grn-item-list.php"

    payload = json.dumps({
        "accesskey": accesskey,
        "grnno": id
    })
    headers = {
        'Content-Type': 'text/plain'
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    if response.status_code == 200:
        data = response.json()
        grn_item_list = data['grnitemlist']
        return render(request, 'grn/add_grnitem_list1.html', {'all_data': grn_item_list,'menuname':menuname,'id':id,'item_masterlist':item_masterlist})
    elif response.status_code == 400:
        data = response.json()
        messages.error(request, data['message'])
        return redirect('/login')
    else:
        return render(request, 'grn/add_grnitem_list1.html',{'menuname':menuname,'id':id,'item_masterlist':item_masterlist})

def grn_reject(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    accesskey = request.session['accesskey']
    url = "http://13.235.112.1/ziva/mobile-api/grn-reject.php"
    #sno=request.POST.get('txtHdnId1')
    payload = json.dumps({
        "accesskey": accesskey,
        "grn_no": request.POST.get('txtHdnId1'),
        "comments":""
    })
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    if response.status_code == 200:
        data = response.json()
        messages.success(request, data['message'])
        #url = reverse('add_grnitem_list', args=[sno])
        return redirect('/grn_pending_status')
    else:
        data = response.json()
        messages.error(request, data['message'])
        #url = reverse('add_grnitem_list', args=[sno])
        return redirect('/grn_pending_status')

def add_grn_inventory(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    accesskey = request.session['accesskey']
    sno = request.POST.get('sno')
    url = "http://13.235.112.1/ziva/mobile-api/grn-add-inventoryitem.php"

    payload = json.dumps({
        "accesskey": accesskey,
        "sno": request.POST.get('txtHdnId'),
        "qty": request.POST.get('qty')
    })
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    if response.status_code == 200:
        data = response.json()
        messages.success(request,data['message'])
        url=reverse('add_grnitem_list',args=[sno])
        return  redirect(url)
    else:
        data = response.json()
        messages.error(request,data['message'])
        url = reverse('add_grnitem_list', args=[sno])
        return redirect(url)
def add_pending_grn_inventory(request):
        if 'accesskey' not in request.session:
            messages.error(request, 'Access denied!')
            return redirect('/login')

        accesskey = request.session['accesskey']
        url = "http://13.235.112.1/ziva/mobile-api/grn-add-inventory.php"

        payload = json.dumps({
            "accesskey": accesskey,
            "grn_no": request.POST.get('txtHdnId'),
            "comments": request.POST.get('comment')
        })
        headers = {
            'Content-Type': 'application/json'
        }

        response = requests.request("GET", url, headers=headers, data=payload)
        if response.status_code == 200:
            data = response.json()
            messages.success(request, data['message'])
            return redirect('grn_pending_status')
        elif response.status_code == 400:
            data = response.json()
            if data['message'] == 'Sorry! some details are missing':
                messages.error(request, data['message'])
                return redirect('grn_pending_status')
            else:
                messages.error(request, data['message'])
                return redirect('/login')
        elif response.status_code == 503:
            data = response.json()
            messages.error(request, data['message'])
            return redirect('grn_pending_status')
        elif response.status_code == 503:
            data = response.json()
            messages.error(request, data['message'])
            return redirect('grn_pending_status')
        elif response.status_code == 500:
            messages.error(request, "Internal server error")
            return redirect('grn_pending_status')

        else:
            messages.error(request,"something went wrong")
            return redirect('grn_pending_status')


def add_apending_grn_inventory1(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    accesskey = request.session['accesskey']
    url = "http://13.235.112.1/ziva/mobile-api/grn-add-inventory.php"

    payload = json.dumps({
        "accesskey": accesskey,
        "grn_no": request.POST.get('txtHdnId'),
        "comments": request.POST.get('comment')
    })
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("GET", url, headers=headers, data=payload)

    data = response.json()

    if response.status_code == 200:
        messages.success(request, data['message'])
        return redirect('grn_list')
    else:
        messages.error(request, data['message'])
        return redirect('grn_list')




def grn_list(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    menuname = request.session['mylist']
    accesskey = request.session['accesskey']

    url = "http://13.235.112.1/ziva/mobile-api/grn-list.php"

    payload = json.dumps({"accesskey":accesskey,"status":"All"})
    headers = {
        'Content-Type': 'text/plain'
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    if response.status_code == 200:
        data = response.json()
        grn_list = data['grnlist']
        return render(request, 'grn/grn_list_all.html', {'all_data': grn_list,'menuname':menuname})
    else:
        return render(request, 'grn/grn_list_all.html',{'menuname':menuname})


def grn_list1(request):
    try:

        if 'accesskey' not in request.session:
            messages.error(request, 'Access denied!')
            return redirect('/login')

        menuname = request.session['mylist']
        accesskey = request.session['accesskey']
        url = "http://13.235.112.1/ziva/mobile-api/vendormasterlist.php"

        payload = json.dumps({"accesskey": accesskey})
        headers = {
            'Content-Type': 'text/plain'
        }
        response = requests.request("GET", url, headers=headers, data=payload)
        data = response.json()
        vendor_masterlist = data['vendormasterlist']

        url = "http://13.235.112.1/ziva/mobile-api/warehousemaster-list.php"
        payload = json.dumps({"accesskey": accesskey})
        headers = {
            'Content-Type': 'text/plain'
        }
        response = requests.request("GET", url, headers=headers, data=payload)
        data = response.json()
        wh_masterlist = data['warehouselist']
        role = request.session['role']
        if role == 'Admin':
            url = "http://13.235.112.1/ziva/mobile-api/grn-list-admin.php"

            payload = json.dumps({"accesskey":accesskey,"status":"All"})
            headers = {
                'Content-Type': 'text/plain'
            }

            response = requests.request("GET", url, headers=headers, data=payload)
            if response.status_code == 200:
                data = response.json()
                grn_list = data['grnlist']
                return render(request, 'grn/grn_list1.html', {'all_data': grn_list,'menuname':menuname,'vendor_masterlist':vendor_masterlist,'wh_masterlist':wh_masterlist})
            elif response.status_code == 400:
                data = response.json()
                if data['message'] == 'Sorry! some details are missing':
                    messages.error(request, data['message'])
                    return redirect('/internal_consumption')
                else:
                    messages.error(request, data['message'])
                    return redirect('/login')
            else:
                return render(request, 'grn/grn_list1.html',{'menuname':menuname})
        else:
            url = "http://13.235.112.1/ziva/mobile-api/grn-list.php"

            payload = json.dumps({"accesskey": accesskey, "status": "All"})
            headers = {
                'Content-Type': 'text/plain'
            }

            response = requests.request("GET", url, headers=headers, data=payload)
            if response.status_code == 200:
                data = response.json()
                grn_list = data['grnlist']
                return render(request, 'grn/grn_list1.html',
                              {'all_data': grn_list, 'menuname': menuname, 'vendor_masterlist': vendor_masterlist,
                               'wh_masterlist': wh_masterlist})
            elif response.status_code == 400:
                data = response.json()
                if data['message'] == 'Sorry! some details are missing':
                    messages.error(request, data['message'])
                    return redirect('/internal_consumption')
                else:
                    messages.error(request, data['message'])
                    return redirect('/login')
            else:
                return render(request, 'grn/grn_list1.html', {'menuname': menuname})
    except:
        if response.status_code == 400:
            data = response.json()
            messages.error(request, data['message'])
            return render(request, 'login1.html')
    return render(request, 'grn/grn_list1.html', {'menuname': menuname})


def grn_new_verified_status(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    menuname = request.session['mylist']
    accesskey = request.session['accesskey']
    url = "http://13.235.112.1/ziva/mobile-api/grn-list.php"

    payload = json.dumps({"accesskey": accesskey, "status": "verified"})
    headers = {
        'Content-Type': 'text/plain'
    }
    response = requests.request("GET", url, headers=headers, data=payload)
    if response.status_code == 200:
        data = response.json()
        grn_list = data['grnlist']
        return render(request, 'grn/grn_new_verified_status.html', {'all_data': grn_list,'menuname':menuname})
    elif response.status_code == 400:
        data = response.json()
        messages.error(request,data['message'])
        return render(request, 'login1.html')
    else:
        return render(request, 'grn/grn_new_verified_status.html',{'menuname':menuname})


def grn_verified_status(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    menuname = request.session['mylist']
    accesskey = request.session['accesskey']
    url = "http://13.235.112.1/ziva/mobile-api/grn-list.php"

    payload = json.dumps({"accesskey": accesskey, "status": "verified"})
    headers = {
        'Content-Type': 'text/plain'
    }
    response = requests.request("GET", url, headers=headers, data=payload)
    if response.status_code == 200:
        data = response.json()
        grn_list = data['grnlist']
        return render(request, 'grn/grn_list_verified.html', {'all_data': grn_list,'menuname':menuname})
    elif response.status_code == 400:
        data = response.json()
        messages.error(request,data['message'])
        return render(request, 'login1.html')
    else:
        return render(request, 'grn/grn_list_verified.html',{'menuname':menuname})


def grn_new_pending_status(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    menuname = request.session['mylist']
    accesskey = request.session['accesskey']

    url = "http://13.235.112.1/ziva/mobile-api/grn-list.php"

    payload = json.dumps({"accesskey": accesskey, "status": "pending"})
    headers = {
        'Content-Type': 'text/plain'
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    if response.status_code == 200:
        data = response.json()
        grn_list = data['grnlist']
        return render(request, 'grn/grn_new.html', {'all_data': grn_list, 'menuname': menuname})
    elif response.status_code == 400:
        data = response.json()
        messages.error(request, data['message'])
        return render(request, 'login1.html')
    else:
        return render(request, 'grn/grn_new.html', {'menuname': menuname})


def grn_pending_status(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    menuname = request.session['mylist']
    accesskey = request.session['accesskey']

    url = "http://13.235.112.1/ziva/mobile-api/grn-list.php"

    payload = json.dumps({"accesskey":accesskey ,"status":"pending"})
    headers = {
        'Content-Type': 'text/plain'
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    if response.status_code == 200:
        data = response.json()
        grn_list = data['grnlist']
        return render(request, 'grn/grn_list_pending.html', {'all_data': grn_list,'menuname':menuname})
    elif response.status_code == 400:
        data = response.json()
        messages.error(request, data['message'])
        return render(request, 'login1.html')
    else:
        return render(request, 'grn/grn_list_pending.html',{'menuname':menuname})



def sale_item_list(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    role = request.session['role']
    accesskey = request.session['accesskey']
    menuname = request.session['mylist']
    busdeponame = request.session['deponame']
    busdepoid = request.session['depoid']
    menuname = request.session['mylist']
    stid = request.session['stid']
    stname = request.session['storename']
    medepoid = request.session['medepoid']
    deponame = request.session['deponame']
    bustation = request.session['bustname']
    accesskey = request.session['accesskey']
    tax_inv = request.session['taxinvoice']
    depoid = request.session['depoid']
    if role == 'Admin':
        depolist = request.session['depolist']
        url = "http://13.235.112.1/ziva/mobile-api/timingstypelist.php"
        payload = json.dumps({

            "accesskey": accesskey
        })
        headers = {
            'Content-Type': 'application/json'
        }
        response = requests.request("GET", url, headers=headers, data=payload)
        if response.status_code == 200:
            data = response.json()
            spell = data['timingslist']

        url = "http://13.235.112.1/ziva/mobile-api/itemmaster-list.php"
        payload = json.dumps({
            "accesskey": accesskey,
        })
        headers = {
            'Content-Type': 'application/json'
        }
        response = requests.request("GET", url, headers=headers, data=payload)
        if response.status_code == 200:
            data = response.json()
            data2 = data['itemmasterlist']

        url = "http://13.235.112.1/ziva/mobile-api/generate-salebill-number.php"

        payload = {
            "accesskey": accesskey,
            "storeid": stid,
            "storename": stname,
            "depoid": depoid,
            "deponame": deponame

        }
        headers = {
            'Content-Type': 'text/plain'
        }
        payload = json.dumps(payload, cls=BytesEncoder)
        response = requests.request("POST", url, headers=headers, data=payload)
        if response.status_code == 200:
            data = response.json()
            netvalue = data['netvalue']
            taxinvoice = data['taxinvoice']

        url = "http://13.235.112.1/ziva/mobile-api/sale-item-list.php"

        payload = json.dumps({
            "accesskey": accesskey,
            "sonumber": taxinvoice
        })
        headers = {
            'Content-Type': 'text/plain'
        }

        response = requests.request("GET", url, headers=headers, data=payload)

        if response.status_code == 200:
            data = response.json()
            sale_item_list = data['saleitemlist']
            return render(request, 'sales/sales_new.html',
                          {'status':'ok','response':'sale200','depolist': depolist,
                           "all_data": sale_item_list,
                           'data': sale_item_list[0],
                           'spell': spell,
                           'netvalue': netvalue,'busdeponame':busdeponame,'busdepoid':busdepoid, 'deponame': medepoid,'bustation':bustation,
                      'stname':stname,'stid':stid,'data2':data2,'data3':data2[0],'taxinvoice':taxinvoice,'menuname':menuname})
        elif response.status_code == 400:
            data = response.json()
            if data['message'] == 'Sorry! some details are missing':
                return render(request, 'sales/sales_new.html',
                              {'depolist': depolist, 'busdeponame': busdeponame, 'busdepoid': busdepoid,
                               'deponame': medepoid, 'bustation': bustation, 'stname': stname, 'data2': data2,
                               'data3': data2[0], 'spell': spell, 'menuname': menuname})
            else:
                messages.error(request, data['message'])
                return redirect('/login')
        else:
            try:
                r = response.json()
            except:
                messages.error(request, response.text)
            return render(request, 'sales/sales_new.html',
                          {'response':'sale200','depolist': depolist,'busdeponame':busdeponame,'busdepoid':busdepoid,'deponame': medepoid,'bustation':bustation,'stname':stname,'data2':data2,'data3':data2[0],'spell':spell,'menuname':menuname})

    else:
            data1 = request.session['daat1']
            busdeponame = request.session['deponame']
            busdepoid = request.session['depoid']
            stid = request.session['stid']
            stname = request.session['storename']
            medepoid = request.session['medepoid']
            deponame = request.session['deponame']
            bustation = request.session['bustname']

            tax_inv = request.session['taxinvoice']
            depoid = request.session['depoid']



            url = "http://13.235.112.1/ziva/mobile-api/timingstypelist.php"
            payload = json.dumps({

                "accesskey": accesskey
            })
            headers = {
                'Content-Type': 'application/json'
            }
            response = requests.request("GET", url, headers=headers, data=payload)
            if response.status_code == 200:
                data = response.json()
                spell = data['timingslist']

            url = "http://13.235.112.1/ziva/mobile-api/itemmaster-list.php"
            payload = json.dumps({
                "accesskey": accesskey,
            })
            headers = {
                'Content-Type': 'application/json'
            }
            response = requests.request("GET", url, headers=headers, data=payload)
            if response.status_code == 200:
                data = response.json()
                data2 = data['itemmasterlist']



            url = "http://13.235.112.1/ziva/mobile-api/generate-salebill-number.php"

            payload = {
                "accesskey": accesskey,
                "storeid": stid,
                "storename": stname,
                "depoid": depoid,
                "deponame": deponame

            }
            headers = {
                'Content-Type': 'text/plain'
            }
            payload = json.dumps(payload, cls=BytesEncoder)
            response = requests.request("POST", url, headers=headers, data=payload)
            if response.status_code == 200:
                data = response.json()
                netvalue = data['netvalue']
                #netvalue = "{:.1f}".format(float(netvalue))
                taxinvoice = data['taxinvoice']

            url = "http://13.235.112.1/ziva/mobile-api/sale-item-list.php"

            payload = json.dumps({
                "accesskey": accesskey,
                "sonumber": tax_inv
            })
            headers = {
                'Content-Type': 'text/plain'
            }

            response = requests.request("GET", url, headers=headers, data=payload)

            if response.status_code == 200:
                data = response.json()
                sale_item_list = data['saleitemlist']
                return render(request, 'sales/sales_new.html',
                              {'status':'ok','response':'sale200','depolist':data1,'busdeponame':busdeponame,'busdepoid':busdepoid,"all_data": sale_item_list, 'deponame': medepoid,'bustation':bustation, 'data': sale_item_list[0],
                              'stname':stname,'stid':stid,'data2':data2,'data3':data2[0],'spell':spell,'netvalue':netvalue,'taxinvoice':taxinvoice,'menuname':menuname})
            elif response.status_code == 400:
                data = response.json()
                if data['message'] == 'Sorry! some details are missing':
                    messages.error(request, data['message'])
                    return render(request, 'sales/sales_new.html',
                                  {'status': 'ok', 'response': 'sale200', 'depolist': data1, 'busdeponame': busdeponame,
                                   'busdepoid': busdepoid, 'deponame': medepoid,
                                   'bustation': bustation,
                                   'stname': stname, 'stid': stid, 'data2': data2, 'data3': data2[0], 'spell': spell,
                                  'menuname': menuname})
                else:
                    return redirect('/login')
            else:
                try:
                    r = response.json()
                    messages.error(request, r['message'])
                except:
                    messages.error(request, response.text)
                return render(request, 'sales/sales_new.html',
                              {'depolist': data1, 'busdeponame': busdeponame, 'busdepoid': busdepoid,
                               'deponame': medepoid, 'bustation': bustation, 'stname': stname, 'data2': data2,
                               'data3': data2[0], 'spell': spell, 'menuname': menuname,'response': 'sale200'})

def sales_item_list_pending(request,id1,id2):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    menuname = request.session['mylist']
    accesskey = request.session['accesskey']

    url = "http://13.235.112.1/ziva/mobile-api/sale-item-list.php"

    payload = json.dumps({
        "accesskey": accesskey,
        "sonumber": id1
    })
    headers = {
        'Content-Type': 'text/plain'
    }

    response = requests.request("GET", url, headers=headers, data=payload)

    if response.status_code == 200:
        data = response.json()
        sale_item_list = data['saleitemlist']
        return render(request, 'sales/sale_item_list.html',{'approve':'pending',"all_data": sale_item_list,'menuname':menuname,"id":id1,'status':id2})
    elif response.status_code == 400:
        data = response.json()
        text = data['message']
        if text in 'some details are missing':
            messages.error(request, data['message'])
            return render(request, 'sales/sale_item_list.html', {'menuname': menuname, "id": id1,'status':id2})
        else:
            messages.error(request, data['message'])
            return render(request, 'login1.html')
    else:
        try:
            data = response.json()
            messages.error(request,data['message'])
        except:
            messages.error(request,response.text)
        return render(request, 'sales/sale_item_list.html',{'menuname':menuname,"id":id1,'status':id2})


def sale_item_list_approve(request, id):
        if 'accesskey' not in request.session:
            messages.error(request, 'Access denied!')
            return redirect('/login')
        menuname = request.session['mylist']
        accesskey = request.session['accesskey']

        url = "http://13.235.112.1/ziva/mobile-api/sale-item-list.php"

        payload = json.dumps({
            "accesskey": accesskey,
            "sonumber": id
        })
        headers = {
            'Content-Type': 'text/plain'
        }

        response = requests.request("GET", url, headers=headers, data=payload)

        if response.status_code == 200:
            data = response.json()
            sale_item_list = data['saleitemlist']
            return render(request, 'sales/sale_item_list_approve.html',
                          {'approve': 'pending', "all_data": sale_item_list, 'menuname': menuname, "id": id})
        elif response.status_code == 400:
            data = response.json()
            messages.error(request, data['message'])
            return render(request, 'login1.html')
        else:
            data = response.json()
            messages.error(request, data['message'])
            return render(request, 'sales/sale_item_list_approve.html', {'menuname': menuname, "id": id})

def proformainvoice(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    try:
        regionid = request.session['regionid']
        warehousename = request.session['warehousename']
        menuname = request.session['mylist']
        accesskey = request.session['accesskey']
        role = request.session['role']
        busdeponame = request.session['deponame']
        busdepoid = request.session['depoid']
        if role == 'Admin':
            url = "http://13.235.112.1/ziva/mobile-api/dropdownlist-storemaster.php"
            payload = json.dumps({
                "accesskey": accesskey,
                "type": "Depo",
                "warehousename": "All",
                "regionid": "All",
                "depoid": ""

            })
            headers = {
                'Content-Type': 'text/plain'
            }
            response = requests.request("POST", url, headers=headers, data=payload)
            if response.status_code == 200:
                data = response.json()
                depolist = data['dropdownlist']
                request.session['depolist'] = depolist

            if request.method == 'POST':

                stname = request.POST.get('stname')
                stid = request.POST.get('stid')
                request.session['stid'] = stid
                request.session['storename'] = stname
                medeponame = request.POST.get('deponame')
                medepoid = request.POST.get('depoid')
                request.session['medepoid'] = medepoid
                request.session['medeponame'] = medeponame
                bustname = request.POST.get('busstationname')
                request.session['bustname'] = bustname

                url = "http://13.235.112.1/ziva/mobile-api/itemmaster-list.php"
                payload = json.dumps({
                    "accesskey": accesskey,
                })
                headers = {
                    'Content-Type': 'application/json'
                }
                response = requests.request("GET", url, headers=headers, data=payload)
                # if response.status_code == 200:
                data = response.json()
                data2 = data['itemmasterlist']

                url = "http://13.235.112.1/ziva/mobile-api/generate-salebill-number-admin.php"

                payload = {
                    "accesskey": accesskey,
                    "storeid": stid,
                    "storename": stname,
                    "depoid":  request.POST.get('depoid'),
                    "deponame": request.POST.get('deponame')
                }
                headers = {
                    'Content-Type': 'text/plain'
                }
                payload = json.dumps(payload, cls=BytesEncoder)
                response = requests.request("POST", url, headers=headers, data=payload)
                if response.status_code == 200:
                    data = response.json()
                    tax_inv = data['taxinvoice']
                    cus_name = data['customer_name']
                    cus_mobile = data['customer_mobile']
                    request.session['taxinvoice'] = tax_inv
                    request.session['customer_name'] = cus_name
                    request.session['customer_mobile'] = cus_mobile
                    messages.success(request, data['message'])
                    return render(request, 'sales/sales_new.html',
                                  {'menuname': menuname,
                                   'depolist': depolist,'busdeponame':busdeponame,'busdepoid':busdepoid,'data2':data2,'stname': stname,'stid':stid,'deponame': medepoid, 'bustation': bustname,'response':'sale200'
                                  })
                elif response.status_code == 400:
                    data = response.json()
                    if data['message'] == 'Sorry! some details are missing':
                        messages.error(request, data['message'])
                        return render(request, 'sales/sales_new.html',
                                      {'menuname': menuname, 'depolist': depolist, 'stname': stname, 'stid': stid,
                                       'deponame': medepoid, 'bustation': bustname})
                    else:
                        messages.error(request, data['message'])
                        return redirect('/login')
                else:
                    try:
                        data = response.json()
                        messages.error(request, data['message'])
                    except:
                        messages.error(request, response.text)
                    return render(request, 'sales/sales_new.html',
                                  {'menuname': menuname, 'depolist': depolist,'stname': stname,'stid':stid,'deponame':medepoid, 'bustation': bustname})
            return render(request, 'sales/sales_new.html',
                          {'depolist': depolist, 'menuname': menuname})

        else:
            url = "http://13.235.112.1/ziva/mobile-api/dropdownlist-storemaster.php"
            payload = json.dumps({
                "accesskey": accesskey,
                "type": "Depo",
                "warehousename": warehousename,
                "regionid": regionid,
                "depoid": ""

            })
            headers = {
                'Content-Type': 'text/plain'
            }
            response = requests.request("POST", url, headers=headers, data=payload)
            if response.status_code == 200:
                data = response.json()
                data1 = data['dropdownlist']
                request.session['daat1'] = data1
                if request.method == 'POST':

                        stname = request.POST.get('stname')
                        stid = request.POST.get('stid')
                        request.session['stid'] = stid
                        request.session['storename']=stname
                        medeponame =  request.POST.get('deponame')
                        medepoid = request.POST.get('depoid')
                        request.session['medepoid'] = medepoid
                        request.session['medeponame']=medeponame
                        bustname = request.POST.get('busstationname')
                        request.session['bustname'] = bustname
                        url = "http://13.235.112.1/ziva/mobile-api/itemmaster-list.php"
                        payload = json.dumps({
                            "accesskey": accesskey,
                        })
                        headers = {
                            'Content-Type': 'application/json'
                        }
                        response = requests.request("GET", url, headers=headers, data=payload)
                        # if response.status_code == 200:
                        data = response.json()
                        data2 = data['itemmasterlist']
                        url = "http://13.235.112.1/ziva/mobile-api/generate-salebill-number.php"

                        payload = {
                            "accesskey": accesskey,
                            "storeid": request.POST.get('stid'),
                            "storename":request.POST.get('stname'),
                            "depoid": busdepoid,
                            "deponame":busdeponame

                        }
                        headers = {
                            'Content-Type': 'text/plain'
                        }
                        payload = json.dumps(payload, cls=BytesEncoder)
                        response = requests.request("POST", url, headers=headers, data=payload)
                        if response.status_code == 200:
                            data = response.json()
                            tax_inv = data['taxinvoice']
                            cus_name = data['customer_name']
                            cus_mobile = data['customer_mobile']
                            request.session['taxinvoice'] = tax_inv
                            request.session['customer_name'] = cus_name
                            request.session['customer_mobile'] = cus_mobile
                            messages.success(request, data['message'])
                            return render(request, 'sales/sales_new.html',
                                          {'response':'sale200','busdeponame':busdeponame,'busdepoid':busdepoid,'menuname':menuname,'depolist': data1, 'data2':data2,'stname': stname,'stid':stid,'deponame': medepoid, 'bustation': bustname})
                        elif response.status_code == 400:
                            data = response.json()
                            if data['message'] == 'Sorry! some details are missing':
                                messages.error(request, data['message'])
                                return render(request, 'sales/sales_new.html', {'busdeponame':busdeponame,'menuname':menuname,'depolist':data1,'stname':stname,'deponame': medepoid,'bustation':bustname})
                            else:
                                messages.error(request, data['message'])
                                return redirect('/login')
                        else:
                            try:
                                data = response.json()
                                messages.error(request,data['message'])
                            except:
                                messages.error(request,response.text)
                            return render(request, 'sales/sales_new.html', {'busdeponame':busdeponame,'menuname':menuname,'depolist':data1,'stname':stname,'deponame': medepoid,'bustation':bustname})
                return render(request, 'sales/sales_new.html', {'depolist':data1,'menuname':menuname,'busdepoid':busdepoid,'busdeponame':busdeponame})

    except:
        if response.status_code == 400:
            data = response.json()
            messages.error(request, data['message'])
            return render(request, 'login1.html')
    return render(request,'sales/sales_new.html')


def sales_item_add(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    try:
        menuname = request.session['mylist']
        tdate = datetime.date.today()
        tdate = tdate.strftime("%d-%m-%Y")
        accesskey = request.session['accesskey']
        regionid = request.session['regionid']
        warehousename = request.session['warehousename']
        stid = request.session['stid']
        stname = request.session['storename']
        deponame = request.session['deponame']
        bustation = request.session['bustname']
        role  = request.session['role']
        if role == 'Admin':
            url = "http://13.235.112.1/ziva/mobile-api/dropdownlist-storemaster.php"
            payload = json.dumps({
                "accesskey": accesskey,
                "type": "Depo",
                "warehousename": "All",
                "regionid": "All",
                "depoid": ""

            })
            headers = {
                'Content-Type': 'text/plain'
            }
            response = requests.request("POST", url, headers=headers, data=payload)
            if response.status_code == 200:
                data = response.json()
                depolist = data['dropdownlist']
            if request.method == 'POST':

                tax_inv = request.session['taxinvoice']
                cus_name = request.session['customer_name']
                cus_mobile = request.session['customer_mobile']

                url = "http://13.235.112.1/ziva/mobile-api/add-saleitem-admin.php"
                payload = json.dumps({

                    "accesskey": accesskey,
                    "quantity": request.POST.get('quantity'),
                    "taxinvoice": tax_inv,
                    "item_code": request.POST.get('itemname'),
                    "date": request.POST.get('date'),
                })

                headers = {
                    'Content-Type': 'application/json'
                }
                r = requests.post(url, data=payload, headers=headers)
                if r.status_code == 200:
                    data = r.json()
                    messages.success(request, data['message'])
                    return redirect('sale_item_list')
                elif response.status_code == 400:
                    data = response.json()
                    text = data['message']
                    if text  in 'some details are missing':
                        messages.error(request, data['message'])
                        return redirect('sale_item_list')
                    else:
                        messages.error(request, data['message'])
                        return redirect('/login')
                else:
                    try:
                        data = r.json()
                        messages.error(request, data['message'])
                    except:
                        messages.error(request, r.text)
                    return redirect('sale_item_list')
            return render(request, 'sales/sales_new.html',
                          {'response':'sale200','menuname': menuname, 'depolist': depolist, 'deponame': deponame, 'bustation': bustation,
                           'stname': stname, 'stid': stid, 'tdate': tdate})
        else:

                url = "http://13.235.112.1/ziva/mobile-api/dropdownlist-storemaster.php"
                payload = json.dumps({
                    "accesskey": accesskey,
                    "type": "Depo",
                    "warehousename": warehousename,
                    "regionid": regionid,
                    "depoid": ""

                })
                headers = {
                    'Content-Type': 'text/plain'
                }
                response = requests.request("POST", url, headers=headers, data=payload)
                if response.status_code == 200:
                    data = response.json()
                    data1 = data['dropdownlist']
                if request.method == 'POST':

                    tax_inv = request.session['taxinvoice']
                    cus_name = request.session['customer_name']
                    cus_mobile = request.session['customer_mobile']


                    url = "http://13.235.112.1/ziva/mobile-api/add-saleitem.php"
                    payload = json.dumps({

                            "accesskey": accesskey,
                            "quantity": request.POST.get('quantity'),
                            "taxinvoice": tax_inv,
                            "item_code": request.POST.get('itemname'),
                            "date": request.POST.get('date'),
                    })

                    headers = {
                        'Content-Type': 'application/json'
                    }
                    r = requests.post(url, data=payload, headers=headers)
                    if r.status_code == 200:
                        data = r.json()
                        messages.success(request,data['message'])
                        return redirect('sale_item_list')
                    else:
                        try:
                            data = r.json()
                            messages.error(request, data['message'])
                        except:
                            messages.error(request,r.text)
                        return redirect('sale_item_list')
                return render(request, 'sales/sales_new.html', {'response':'sale200','menuname':menuname,'depolist':data1,'deponame': deponame,'bustation':bustation, 'stname':stname,'stid':stid,'tdate':tdate})


    except:
        if response.status_code == 400:
            data = response.json()
            messages.error(request, data['message'])
            return render(request, 'login1.html')
    return render(request, 'sales/sales_new.html', {'menuname': menuname})


def complete_sale(request):
        if 'accesskey' not in request.session:
            messages.error(request, 'Access denied!')
            return redirect('/login')
        try:
            accesskey = request.session['accesskey']
            role = request.session['role']
            paymentmode = request.POST.get('paymenttype')
            if   paymentmode:
                paymentmode = request.POST.get('paymenttype')
            else:
                paymentmode = request.POST.get('paymenttype1')
            if role == 'Admin':
                if request.method == 'POST':
                    url = "http://13.235.112.1/ziva/mobile-api/dc-pending-admin.php"

                    if paymentmode == 'CASH':
                        payload = json.dumps({
                            "accesskey": accesskey,
                            "sonumber": request.POST.get('txtHdnId'),
                            "paymentmode":paymentmode,
                            "remarks": request.POST.get('remarks'),
                            "date": request.POST.get('date'),
                            "spelloftheday": request.POST.get('spell1'),
                            "transaction_status": "success",
                            "transaction_id": "",
                        })
                    if paymentmode == 'SCANNER':
                        payload = json.dumps({
                            "accesskey": accesskey,
                            "sonumber": request.POST.get('txtHdnId'),
                            "paymentmode": paymentmode,
                            "remarks": request.POST.get('remarks'),
                            "date": request.POST.get('date'),
                            "spelloftheday": request.POST.get('spell1'),
                            "transaction_status": "success",
                            "transaction_id": request.POST.get('txnid')
                        })
                    if paymentmode == 'DUE':
                        payload = json.dumps({
                            "accesskey": accesskey,
                            "sonumber": request.POST.get('txtHdnId'),
                            "paymentmode": paymentmode,
                            "remarks": request.POST.get('remarks'),
                            "date": request.POST.get('date'),
                            "spelloftheday": request.POST.get('spell1'),
                            "transaction_status": "due",
                            "transaction_id": "",
                        })
                    headers = {
                        'Content-Type': 'application/json'
                    }
                    response = requests.request("POST", url, headers=headers, data=payload)

                    if response.status_code == 200:
                        data = response.json()
                        messages.success(request, data['message'])
                        return redirect('proformainvoice')
                    elif response.status_code == 400:
                        data = response.json()
                        messages.error(request, data['message'])
                        return redirect('proformainvoice')

                    else:
                        try:
                            data = response.json()
                            messages.error(request, data['message'])
                            return redirect('proformainvoice')
                        except:
                            messages.error(request, response.text)
                            return redirect('proformainvoice')
            else:
                    if  request.method == 'POST':
                            url = "http://13.235.112.1/ziva/mobile-api/dc-pending.php"

                            if paymentmode == 'CASH':
                                payload = json.dumps({
                                    "accesskey": accesskey,
                                    "sonumber": request.POST.get('txtHdnId'),
                                    "paymentmode": paymentmode,
                                    "remarks": request.POST.get('remarks'),
                                    "date": request.POST.get('date'),
                                    "spelloftheday":request.POST.get('spell1'),
                                    "transaction_status":"success",
                                    "transaction_id":"",
                                })
                            if paymentmode == 'SCANNER':
                                payload = json.dumps({
                                    "accesskey": accesskey,
                                    "sonumber": request.POST.get('txtHdnId'),
                                    "paymentmode":paymentmode,
                                    "remarks": request.POST.get('remarks'),
                                    "date": request.POST.get('date'),
                                    "spelloftheday": request.POST.get('spell1'),
                                    "transaction_status": "success",
                                    "transaction_id": request.POST.get('txnid')
                                })
                            if paymentmode == 'DUE':
                                payload = json.dumps({
                                    "accesskey": accesskey,
                                    "sonumber": request.POST.get('txtHdnId'),
                                    "paymentmode": paymentmode,
                                    "remarks": request.POST.get('remarks'),
                                    "date": request.POST.get('date'),
                                    "spelloftheday": request.POST.get('spell1'),
                                    "transaction_status": "due",
                                    "transaction_id": "",
                                })
                            headers = {
                                'Content-Type': 'application/json'
                            }
                            response = requests.request("POST", url, headers=headers, data=payload)

                            if response.status_code == 200:
                                data = response.json()
                                messages.success(request, data['message'])
                                return redirect('proformainvoice')
                            elif response.status_code == 400:
                                data = response.json()
                                messages.error(request, data['message'])
                                return redirect('proformainvoice')

                            else:
                                try:
                                    data = response.json()
                                    messages.error(request, data['message'])
                                    return redirect('proformainvoice')
                                except:
                                    messages.error(request,response.text)
                                    return redirect('proformainvoice')
        except:
            messages.error(request,"something went wrong")
            return redirect('sale_item_list')
def delete_deliverchallanitem(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    tax_inv = request.session['taxinvoice']
    accesskey = request.session['accesskey']
    url = "http://13.235.112.1/ziva/mobile-api/delete-saleitem-approved.php"

    payload = json.dumps({
        "accesskey": accesskey,
        "sno": id,
        "sonumber": tax_inv
    })
    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.request("GET", url, headers=headers, data=payload)
    if response.status_code == 200:
        data = response.json()
        messages.success(request, data['message'])
        return redirect('sale_item_list')
    elif response.status_code == 400:
        data = response.json()
        messages.error(request, data['message'])
        return redirect('/login')
    else:
        try:
            data = response.json()
            messages.error(request, data['message'])
        except:
            messages.error(request, response.text)
        return redirect('sale_item_list')


def delete_salesitem(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    accesskey = request.session['accesskey']
    url = "http://13.235.112.1/ziva/mobile-api/delete-sale-item.php"
    id1=request.POST.get('deletesono')
    id2=request.POST.get('status')
    payload = json.dumps({
        "accesskey": accesskey,
        "sno": request.POST.get('deleteid'),
        "sonumber": id1,
    })
    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.request("GET", url, headers=headers, data=payload)
    if response.status_code == 200:
        data = response.json()
        messages.success(request, data['message'])
        url = reverse('sales_item_list_pending', args=[id1,id2])
        return redirect(url)
    elif response.status_code == 400:
        data = response.json()
        text = data['message']
        if text in 'some details are missing':
            messages.error(request, data['message'])
            url = reverse('sales_item_list_pending', args=[id1,id2])
            return redirect(url)
        else:
            messages.error(request, data['message'])
            return redirect('/login')
    else:
        try:
            data = response.json()
            messages.error(request, data['message'])
        except:
            messages.error(request, response.text)
        url = reverse('sales_item_list_pending', args=[id1,id2])
        return redirect(url)



def delete_sale_item(request,id):
        if 'accesskey' not in request.session:
            messages.error(request, 'Access denied!')
            return redirect('/login')
        tax_inv = request.session['taxinvoice']
        accesskey = request.session['accesskey']
        url = "http://13.235.112.1/ziva/mobile-api/delete-saleitem.php"

        payload = json.dumps({
            "accesskey": accesskey,
            "sno":id,
            "sonumber":tax_inv
        })
        headers = {
            'Content-Type': 'application/json'
        }
        response = requests.request("GET", url, headers=headers, data=payload)
        if response.status_code == 200:
            data = response.json()
            messages.success(request, data['message'])
            return redirect('sale_item_list')
        elif response.status_code == 400:
            data = response.json()
            messages.error(request, data['message'])
            return redirect('/login')
        else:
            try:
                data = response.json()
                messages.error(request, data['message'])
            except:
                messages.error(request,response.text)
            return redirect('sale_item_list')



def deletetax_admin(request,id):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    accesskey = request.session['accesskey']
    url = "http://13.235.112.1/ziva/mobile-api/delete-taxinvoice.php"

    payload = json.dumps({
        "accesskey": accesskey,
        "sonumber": id
    })
    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.request("GET", url, headers=headers, data=payload)
    if response.status_code == 200:
        data = response.json()
        messages.success(request, data['message'])
        return redirect('taxinvoice_list_admin')
    elif response.status_code == 400:
        data = response.json()
        messages.error(request, data['message'])
        return redirect('/login')
    else:
        try:
            data = response.json()
            messages.error(request, data['message'])
        except:
            messages.error(request, response.text)
        return redirect('taxinvoice_list_admin')

def get_sale_item(request):

    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    accesskey = request.session['accesskey']

    url = "http://13.235.112.1/ziva/mobile-api/sale-item-list.php"
    itemcode =  request.POST.get('itemcode')
    payload = json.dumps({
        "accesskey": accesskey,
        "sonumber": request.POST.get('id'),
    })
    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.request("GET", url, headers=headers, data=payload)
    if response.status_code == 200:
        data = response.json()
        list = data['saleitemlist']
        for i in list:
            if str(i['item_code']) == itemcode:
                data = {"item_name": i["item_name"], "item_code": i["item_code"], "uom": i["uom"], "noofbottles": i['noofbottles'],
                        "total": i['total'],  "mrp": i['mrp'],"id":i['id'],
                        "expiry_date": i['expiry_date'], "todate1": i['createdon'],"quantity":i['quantity'],"so_number":i['so_number']
                        }
        return JsonResponse({'data': data})
    elif response.status_code == 400:
        data = response.json()
        if data['message'] == 'Sorry! some details are missing':
            return JsonResponse({'data': data})
        else:
            messages.error(request, data['message'])
            return redirect('/login')
    elif response.status_code == 503:
        data = response.json()
        return JsonResponse({'data': data})
    elif response.status_code == 500:
        data = {'error': 'true', 'message': 'Internal server error'}
        return JsonResponse({'data': data})
    else:
        data = {'error': 'true', 'message': 'something went wrong'}
        return JsonResponse({'data': data})

def edit_sale_item(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    tax_inv = request.session['taxinvoice']
    accesskey = request.session['accesskey']
    url = "http://13.235.112.1/ziva/mobile-api/edit-saleitem.php"

    payload = json.dumps({
        "accesskey": accesskey,
        "sno": request.POST.get('txtHdnId1'),
        "sonumber": tax_inv,
        "qty": request.POST.get('quantity1')
    })
    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.request("GET", url, headers=headers, data=payload)
    if response.status_code == 200:
        data = response.json()
        messages.success(request, data['message'])
        return redirect('sale_item_list')
    elif response.status_code == 400:
        data = response.json()
        text = data['message']
        if text in 'some details are missing':
            messages.error(request, data['message'])
            return redirect('sale_item_list')
        else:
            messages.error(request, data['message'])
            return redirect('/login')
    else:
        try:
            data = response.json()
            messages.error(request, data['message'])
        except:
            messages.error(request, response.text)
        return redirect('sale_item_list')


def grn(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    try:
        menuname = request.session['mylist']
        accesskey = request.session['accesskey']
        url = "http://13.235.112.1/ziva/mobile-api/vendormasterlist.php"

        payload = json.dumps({"accesskey":accesskey})
        headers = {
            'Content-Type': 'text/plain'
        }

        response = requests.request("GET", url, headers=headers, data=payload)

        data = response.json()
        vendor_masterlist = data['vendormasterlist']

        url = "http://13.235.112.1/ziva/mobile-api/warehousemaster-list.php"

        payload = json.dumps({"accesskey":accesskey})
        headers = {
            'Content-Type': 'text/plain'
        }

        response = requests.request("GET", url, headers=headers, data=payload)
        data1 = response.json()
        wh_masterlist = data1['warehouselist']

        if request.method == "POST":
            url = "http://13.235.112.1/ziva/mobile-api/create-grn.php"
            payload = {
                "accesskey": "MDExNjczMjAyMi0xMi0xNyAwNjoxNzo1Nw==",
                "vendorname": request.POST.get('vname'),
                "invoiceno": request.POST.get('invno'),
                "invoicedate": request.POST.get('invoicedate'),
                "invoiceamount": request.POST.get('invoiceamount'),
                "vendorid": request.POST.get('vid'),
                "whcode": request.POST.get('whname')
            }
            payload = json.dumps(payload, cls=BytesEncoder)
            headers = {
                'Content-Type': 'application/json'
            }
            r = requests.post(url, payload, headers=headers)

            if r.status_code == 200:
                data2 = r.json()
                grn = data2['grnnumber']
                request.session['grnnumber'] = grn
                messages.success(request, data2['message'])
                return redirect('add_grnitem')
            else:
                data2 = r.json()
                messages.error(request, data2['message'])
                return redirect('add_grn')
        else:
            return render(request, 'grn/grn_new.html', {'menuname':menuname,'all_data': vendor_masterlist, 'all_data1': wh_masterlist})
    except:
        if response.status_code == 400:
            messages.error(request, data['message'])
            return redirect('/login')
    return render(request, 'grn/grn_new.html', {'menuname': menuname})

def deliver_challan(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    displayrole = request.session['displayrole']
    if  displayrole == "DEPOT STORE EXECUTIVE":
        menuname = request.session['mylist']
        tdate = datetime.date.today()
        tdate = tdate.strftime("%Y-%m-%d")
        try:
            accesskey = request.session['accesskey']
            regionid = request.session['regionid']
            deponame = request.session['depoid']
            warehousename = request.session['warehousename']
            url = "http://13.235.112.1/ziva/mobile-api/dropdownlist-storemaster.php"

            payload = json.dumps({"accesskey": accesskey, "type": "Bus Station",
                                  "warehousename": warehousename,
                                  "regionid": regionid,
                                  "depoid": deponame})
            headers = {
                'Content-Type': 'text/plain'
            }
            response = requests.request("GET", url, headers=headers, data=payload)

            data = response.json()
            data1  = data['dropdownlist']
            url = "http://13.235.112.1/ziva/mobile-api/vehicle-dropdownlist.php"
            payload = json.dumps({
                "accesskey": accesskey
            })
            headers = {
                'Content-Type': 'application/json'
            }
            response = requests.request("GET", url, headers=headers, data=payload)
            data = response.json()
            vehicals = data['vehicleslist']

            if request.method == 'POST':
                date = request.POST.get('date')
                accesskey = request.session['accesskey']
                busstation = request.POST.get('busstationname1')
                busstationid1 =request.POST.get('busstationid')

                url = "http://13.235.112.1/ziva/mobile-api/delivery-pending-list.php"

                payload = json.dumps({
                    "accesskey": accesskey,
                    "date":request.POST.get('date'),
                    "busstation":busstation,
                    "type":"Pending"
                })
                headers = {
                    'Content-Type': 'application/json'
                }

                response = requests.request("GET", url, headers=headers, data=payload)
                if response.status_code == 200:
                    data = response.json()
                    deliv_challan = data['deliverypendinglist']
                    return render(request, 'deliverychallan/deliverychallan.html', {'approve':'pending',"all_data": deliv_challan,'data1':data1,'vehicals':vehicals,'date':date,'status':'Delivery Pending','busstation':busstation,'busstationid1':busstationid1,'menuname':menuname})
                else:
                    return render(request, 'deliverychallan/deliverychallan.html', {'data1': data1,'date':date,'vehicals':vehicals,'status':'Delivery Pending','busstation':busstation,'busstationid1':busstationid1,'menuname':menuname})
            else:

                    url = "http://13.235.112.1/ziva/mobile-api/delivery-pending-list.php"
                    payload = json.dumps({
                        "accesskey": accesskey,
                        "busstation": "All",
                        "date": "All",
                        "type": "Pending"
                    })
                    headers = {
                        'Content-Type': 'application/json'
                    }

                    response = requests.request("GET", url, headers=headers, data=payload)
                    if response.status_code == 200:
                        data = response.json()
                        deliv_challan = data['deliverypendinglist']
                        return render(request, 'deliverychallan/deliverychallan.html',
                                      {'approve':'pending',"all_data": deliv_challan, 'data1': data1,'date':tdate,'vehicals':vehicals,'busstation':'All','menuname':menuname})
                    else:
                        return render(request, 'deliverychallan/deliverychallan.html',{'data1':data1,'vehicals':vehicals,'date':tdate,'busstation':'All','menuname':menuname})
        except:
                if response.status_code == 400:
                    messages.error(request,data['message'])
                    return render(request,'login1.html')
        return render(request, 'deliverychallan/deliverychallan.html',{'menuname':menuname})
    else:

        menuname = request.session['mylist']
        tdate = datetime.date.today()
        tdate = tdate.strftime("%Y-%m-%d")
        try:
            accesskey = request.session['accesskey']
            regionid = request.session['regionid']
            deponame = request.session['depoid']
            warehousename = request.session['warehousename']
            url = "http://13.235.112.1/ziva/mobile-api/dropdownlist-storemaster.php"

            payload = json.dumps({"accesskey": accesskey, "type": "Bus Station",
                                  "warehousename": warehousename,
                                  "regionid": regionid,
                                  "depoid": deponame})
            headers = {
                'Content-Type': 'text/plain'
            }
            response = requests.request("GET", url, headers=headers, data=payload)

            data = response.json()
            data1  = data['dropdownlist']

            if request.method == 'POST':
                date = request.POST.get('date')
                accesskey = request.session['accesskey']
                busstation = request.POST.get('busstationname1')
                busstationid1 =request.POST.get('busstationid')

                url = "http://13.235.112.1/ziva/mobile-api/delivery-pending-list.php"

                payload = json.dumps({
                    "accesskey": accesskey,
                    "date":request.POST.get('date'),
                    "busstation":busstation,
                    "type":"Pending"
                })
                headers = {
                    'Content-Type': 'application/json'
                }

                response = requests.request("GET", url, headers=headers, data=payload)
                if response.status_code == 200:
                    data = response.json()
                    deliv_challan = data['deliverypendinglist']
                    return render(request, 'deliverychallan/deliverychallan.html', {'approve':'pending',"all_data": deliv_challan,'data1':data1,'date':date,'status':'Delivery Pending','busstation':busstation,'busstationid1':busstationid1,'menuname':menuname})
                else:
                    return render(request, 'deliverychallan/deliverychallan.html', {'approve':'pending','data1': data1,'date':date,'status':'Delivery Pending','busstation':busstation,'busstationid1':busstationid1,'menuname':menuname})
            else:

                    url = "http://13.235.112.1/ziva/mobile-api/delivery-pending-list.php"
                    payload = json.dumps({
                        "accesskey": accesskey,
                        "busstation": "All",
                        "date": "All",
                        "type": "Pending"
                    })
                    headers = {
                        'Content-Type': 'application/json'
                    }

                    response = requests.request("GET", url, headers=headers, data=payload)
                    if response.status_code == 200:
                        data = response.json()
                        deliv_challan = data['deliverypendinglist']
                        return render(request, 'deliverychallan/deliverychallan.html',
                                      {'approve':'pending',"all_data": deliv_challan, 'data1': data1,'date':tdate,'busstation':'All','menuname':menuname})
                    else:
                        return render(request, 'deliverychallan/deliverychallan.html',{'approve':'pending','data1':data1,'date':tdate,'busstation':'All','menuname':menuname})
        except:
                if response.status_code == 400:
                    messages.error(request,data['message'])
                    return render(request,'login1.html')
        return render(request, 'deliverychallan/deliverychallan.html',{'menuname':menuname})

def get_salebus(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    accesskey = request.session['accesskey']
    regionid = request.session['regionid']
    warehousename = request.session['warehousename']
    url = "http://13.235.112.1/ziva/mobile-api/dropdownlist-storemaster.php"

    payload = json.dumps({"accesskey": accesskey, "type": "Bus Station",
                          "warehousename": warehousename,
                          "regionid": regionid,
                          "depoid": request.POST.get('depo')})
    headers = {
        'Content-Type': 'text/plain'
    }
    response = requests.request("GET", url, headers=headers, data=payload)
    if response.status_code == 200:
        data = response.json()
        return JsonResponse({'data': data})
    elif response.status_code == 400:
        data = response.json()
        return redirect('/login')



def medeliver_challan(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    menuname = request.session['mylist']
    tdate = datetime.date.today()
    tdate = tdate.strftime("%Y-%m-%d")
    role = request.session['role']
    try:
        accesskey = request.session['accesskey']
        regionid = request.session['regionid']
        deponame = request.session['depoid']
        warehousename = request.session['warehousename']

        url = "http://13.235.112.1/ziva/mobile-api/warehousemaster-list.php"

        payload = json.dumps({"accesskey": accesskey})
        headers = {
            'Content-Type': 'text/plain'
        }
        response = requests.request("GET", url, headers=headers, data=payload)

        data = response.json()
        wh_masterlist = data['warehouselist']
        url = "http://13.235.112.1/ziva/mobile-api/dropdownlist-storemaster.php"

        payload = json.dumps({"accesskey": accesskey, "type": "Depo",
                              "warehousename": warehousename,
                              "regionid": regionid,
                              "depoid": deponame})
        headers = {
            'Content-Type': 'text/plain'
        }
        response = requests.request("GET", url, headers=headers, data=payload)

        data = response.json()
        data1 = data['dropdownlist']
        url = "http://13.235.112.1/ziva/mobile-api/dates-filter.php"

        payload = json.dumps({"accesskey": accesskey})
        headers = {
            'Content-Type': 'text/plain'
        }
        response = requests.request("GET", url, headers=headers, data=payload)

        data = response.json()
        selectrange = data['timingslist']
        if request.method == 'POST':
            date = request.POST.get('from')
            busstation = request.POST.get('busstationid')
            depo = request.POST.get('depoid')


            url = "http://13.235.112.1/ziva/mobile-api/delivery-pending-list-region.php"
            if role == 'Admin':
                if date == 'Custom Dates':
                    payload = json.dumps({
                        "accesskey": accesskey,
                        "date":date,
                        "fdate": request.POST.get('ldate'),
                        "depo": request.POST.get('depoid1'),
                        "busstation": request.POST.get('busstationname1'),
                        "regionid": request.POST.get('regionid1'),
                        "warehouseid": request.POST.get('warehouseid1'),
                        "type": "Approve"
                    })
                else:
                    payload = json.dumps({
                        "accesskey": accesskey,
                        "date":date,
                        "fdate":date,
                        "depo": request.POST.get('depoid1'),
                        "busstation": request.POST.get('busstationname1'),
                        "regionid": request.POST.get('regionid1'),
                        "warehouseid": request.POST.get('warehouseid1'),
                        "type": "Approve"
                    })
            else:

                payload = json.dumps({
                    "accesskey": accesskey,
                    "date": request.POST.get('from'),
                    "depo":request.POST.get('depotname'),
                    "busstation": request.POST.get('busstationname'),
                    "type": "Approve"
                })
            headers = {
                'Content-Type': 'application/json'
            }

            response = requests.request("GET", url, headers=headers, data=payload)
            if response.status_code == 200:
                data = response.json()
                deliv_challan = data['deliverypendinglist']
                return render(request, 'deliverychallan/medeliverychallan.html',
                              {"selectrange":selectrange,"wh_masterlist":wh_masterlist,"all_data": deliv_challan, 'data1': data1, 'date': date,'busstation':busstation,'depo':depo,'menuname':menuname})
            else:
                return render(request, 'deliverychallan/medeliverychallan.html',
                              {"selectrange":selectrange,"wh_masterlist":wh_masterlist,'data1': data1,'date': date,'busstation':busstation,'depo':depo,'menuname':menuname})
        else:

            url = "http://13.235.112.1/ziva/mobile-api/delivery-pending-list-region.php"
            payload = json.dumps({
                "accesskey": accesskey,
                "busstation": "All",
                "date": "Current Month",
                "depo":"All",
                "regionid": "All",
                "warehouseid": "All",
                "type": "Approve"
            })
            headers = {
                'Content-Type': 'application/json'
            }

            response = requests.request("GET", url, headers=headers, data=payload)
            if response.status_code == 200:
                data = response.json()
                deliv_challan = data['deliverypendinglist']
                return render(request, 'deliverychallan/medeliverychallan.html',
                              {"selectrange":selectrange,"wh_masterlist":wh_masterlist,"all_data": deliv_challan, 'data1': data1, "busstation": "All",'depo':'All','date':tdate,'menuname':menuname})
            else:
                return render(request, 'deliverychallan/medeliverychallan.html',
                              {"selectrange":selectrange,"wh_masterlist":wh_masterlist,'data1': data1, "busstation": "All",'depo':'All','date':tdate,'menuname':menuname})

    except:
        messages.error(request, response.text)
    return render(request, 'deliverychallan/medeliverychallan.html',{'menuname':menuname})

def medeliver_challan_pending(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')

    try:
        menuname = request.session['mylist']
        tdate = datetime.date.today()
        tdate = tdate.strftime("%Y-%m-%d")
        accesskey = request.session['accesskey']
        regionid = request.session['regionid']
        deponame = request.session['depoid']
        warehousename = request.session['warehousename']
        role = request.session['role']

        url = "http://13.235.112.1/ziva/mobile-api/warehousemaster-list.php"

        payload = json.dumps({"accesskey": accesskey})
        headers = {
            'Content-Type': 'text/plain'
        }
        response = requests.request("GET", url, headers=headers, data=payload)

        data = response.json()
        wh_masterlist = data['warehouselist']

        url = "http://13.235.112.1/ziva/mobile-api/dropdownlist-storemaster.php"

        payload = json.dumps({"accesskey": accesskey, "type": "Depo",
                                  "warehousename": warehousename,
                                  "regionid": regionid,
                                  "depoid": deponame})
        headers = {
                'Content-Type': 'text/plain'
        }
        response = requests.request("GET", url, headers=headers, data=payload)
        data = response.json()
        data1 = data['dropdownlist']

        url = "http://13.235.112.1/ziva/mobile-api/dates-filter.php"

        payload = json.dumps({"accesskey": accesskey})
        headers = {
            'Content-Type': 'text/plain'
        }
        response = requests.request("GET", url, headers=headers, data=payload)

        data = response.json()
        selectrange = data['timingslist']

        if request.method == 'POST':
            date = request.POST.get('date')
            accesskey = request.session['accesskey']
            busstation = request.POST.get('busstationname1')
            depo = request.POST.get('deponame1')

            url = "http://13.235.112.1/ziva/mobile-api/delivery-pending-list-region.php"
            if role == 'Admin':
                date = request.POST.get('from')
                if date == 'Custom Dates':
                    payload = json.dumps({
                        "accesskey": accesskey,
                        "date": request.POST.get('from'),
                        "fdate": request.POST.get('ldate'),
                        "depo":request.POST.get('depoid1'),
                        "busstation": request.POST.get('busstationname1'),
                        "regionid":request.POST.get('regionid1'),
                        "warehouseid":request.POST.get('warehouseid1'),
                        "type": "Pending"
                    })
                else:
                    payload = json.dumps({
                        "accesskey": accesskey,
                        "date": request.POST.get('from'),
                        "fdate": request.POST.get('from'),
                        "depo": request.POST.get('depoid1'),
                        "busstation": request.POST.get('busstationname1'),
                        "regionid": request.POST.get('regionid1'),
                        "warehouseid": request.POST.get('warehouseid1'),
                        "type": "Pending"
                    })
            else:
                payload = json.dumps({
                    "accesskey": accesskey,
                    "date": request.POST.get('date'),
                    "depo": request.POST.get('depoid'),
                    "busstation": request.POST.get('busstationname'),
                    "regionid": regionid,
                    "warehouseid": "All",
                    "type": "Pending"
                })
            headers = {
                'Content-Type': 'application/json'
            }

            response = requests.request("GET", url, headers=headers, data=payload)
            if response.status_code == 200:
                data = response.json()
                deliv_challan = data['deliverypendinglist']
                return render(request, 'deliverychallan/medeliverychallan_pending.html',
                              {"all_data": deliv_challan, 'wh_masterlist':wh_masterlist,'data1': data1, 'date': date,'busstation':busstation,'depo':depo,'menuname':menuname,'mewh':warehousename,'mereg':regionid,'selectrange':selectrange})
            else:
                return render(request, 'deliverychallan/medeliverychallan_pending.html',
                              {'data1': data1,'date': date,'wh_masterlist':wh_masterlist,'busstation':busstation,'depo':depo,'menuname':menuname,'mewh':warehousename,'mereg':regionid,'selectrange':selectrange})
        else:

            url = "http://13.235.112.1/ziva/mobile-api/delivery-pending-list-region.php"
            payload = json.dumps({
                "accesskey": accesskey,
                "busstation": "All",
                "fdate": "Current Month",
                "date":"Current Month",
                "depo":"All",
                "regionid":"All",
                "warehouseid": "All",
                "type": "Pending"
            })
            headers = {
                'Content-Type': 'application/json'
            }

            response = requests.request("GET", url, headers=headers, data=payload)
            if response.status_code == 200:
                data = response.json()
                deliv_challan = data['deliverypendinglist']
                return render(request, 'deliverychallan/medeliverychallan_pending.html',
                              {'mewh':warehousename,'mereg':regionid,"all_data": deliv_challan, 'wh_masterlist':wh_masterlist,'data1': data1,"busstation": "All",'date':tdate,'menuname':menuname,'selectrange':selectrange})
            else:
                return render(request, 'deliverychallan/medeliverychallan_pending.html',
                              {'mewh':warehousename,'mereg':regionid,'data1': data1,"busstation": "All",'wh_masterlist':wh_masterlist,'date':tdate,'menuname':menuname,'selectrange':selectrange})

    except:
        if response.status_code == 400:
            messages.error(request, data['message'])
            return render(request,'login1.html')
    return render(request, 'deliverychallan/medeliverychallan_pending.html',{'menuname':menuname})


def deliver_challan_approve(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    try:
        menuname = request.session['mylist']
        tdate = datetime.date.today()
        tdate = tdate.strftime("%Y-%m-%d")
        accesskey = request.session['accesskey']
        regionid = request.session['regionid']
        deponame = request.session['depoid']
        warehousename = request.session['warehousename']
        url = "http://13.235.112.1/ziva/mobile-api/dropdownlist-storemaster.php"

        payload = json.dumps({"accesskey": accesskey, "type": "Bus Station",
                              "warehousename": warehousename,
                              "regionid": regionid,
                              "depoid": deponame})
        headers = {
            'Content-Type': 'text/plain'
        }
        response = requests.request("GET", url, headers=headers, data=payload)

        data = response.json()
        data1 = data['dropdownlist']

        if request.method == 'POST':
            date = request.POST.get('date')
            accesskey = request.session['accesskey']
            url = "http://13.235.112.1/ziva/mobile-api/delivery-pending-list.php"

            payload = json.dumps({
                "accesskey": accesskey,
                "date": request.POST.get('date'),
                "busstation": request.POST.get('busstationname1'),
                "type": "Approve"
            })
            headers = {
                'Content-Type': 'application/json'
            }

            response = requests.request("GET", url, headers=headers, data=payload)
            if response.status_code == 200:
                data = response.json()
                deliv_challan = data['deliverypendinglist']
                return render(request, 'deliverychallan/deliverychallan_approve.html',
                              {"all_data": deliv_challan, 'data1': data1, 'date': tdate, 'menuname': menuname,
                               'approve': 'approve'})
            else:
                return render(request, 'deliverychallan/deliverychallan_approve.html',
                              { 'data1': data1, 'date': tdate, 'menuname': menuname,
                               'approve': 'approve'})
        else:

            url = "http://13.235.112.1/ziva/mobile-api/delivery-pending-list.php"
            payload = json.dumps({
                "accesskey": accesskey,
                "busstation": "All",
                "date": "All",
                "type": "Approve"
            })
            headers = {
                'Content-Type': 'application/json'
            }

            response = requests.request("GET", url, headers=headers, data=payload)
            if response.status_code == 200:
                data = response.json()
                deliv_challan = data['deliverypendinglist']
                return render(request, 'deliverychallan/deliverychallan_approve.html',
                              {"all_data": deliv_challan, 'data1': data1,'date':tdate,'menuname':menuname,'approve':'approve'})
            else:
                return render(request, 'deliverychallan/deliverychallan_approve.html', {'menuname':menuname,'data1': data1,'date':tdate})

    except:
        if response.status_code == 400:
            messages.error(request, data['message'])
            return render(request,'login1.html')
    return render(request, 'deliverychallan/deliverychallan_approve.html',{'menuname':menuname})
def deliver_challan_status(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')

    accesskey = request.session['accesskey']
    role = request.session['role']
    id = request.POST.getlist('txtHdnId[]')
    id = str(id).replace('[', '').replace(']', '').replace("'", '')
    if role == 'Admin':
        url = "http://13.235.112.1/ziva/mobile-api/delivery-challan-admin.php"

        payload = json.dumps({
            "accesskey": accesskey,
            "id": id,
            "agentname": request.POST.get('agentname'),
            "vehicledetails": request.POST.get('vehicaldetails'),
            "remarks": request.POST.get('remarks'),
            "contactno": request.POST.get('agentno')
        })
        headers = {
            'Content-Type': 'application/json'
        }

        response = requests.request("GET", url, headers=headers, data=payload)

        if response.status_code == 200:
            data = response.json()
            messages.success(request, data['message'])
            return redirect('medeliver_challan_pending')
        elif response.status_code == 400:
            data = response.json()
            text = data['message']
            if text in  'some details are missing':
                return redirect('medeliver_challan_pending')
            else:
                messages.error(request, data['message'])
                return redirect('/login')
        elif response.status_code == 503:
            data = response.json()
            message = data['message']
            if message =='Your avl quantity is 0':
                messages.error(request, message)
                return redirect('medeliver_challan_pending')
            else:
                messages.error(request, "Please  select any  check box")
                return redirect('medeliver_challan_pending')

        else:
            messages.error(request, "something went wrong")
            return redirect('medeliver_challan_pending')

    else:
            url = "http://13.235.112.1/ziva/mobile-api/delivery-challan.php"

            payload = json.dumps({
                "accesskey":accesskey,
                "id":id,
                "agentname":request.POST.get('agentname'),
                "vehicledetails":request.POST.get('vehicaldetails'),
                "remarks":request.POST.get('remarks'),
                "contactno":request.POST.get('agentno')
            })
            headers = {
                'Content-Type': 'application/json'
            }

            response = requests.request("GET", url, headers=headers, data=payload)

            if response.status_code == 200:
                data = response.json()
                messages.success(request, data['message'])
                return redirect('deliver_challan')
            elif response.status_code == 400:
                data = response.json()
                text = data['message']
                if text in 'some details are missing':
                    return redirect('deliver_challan')
                else:
                    messages.error(request, data['message'])
                    return redirect('/login')
            elif response.status_code == 503:
                data = response.json()
                messages.error(request, "Please select any checkbox")
                return redirect('deliver_challan')
            else:
                messages.error(request,"something went wrong")
                return redirect('deliver_challan')

def deliver_challan_update(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')

    accesskey = request.session['accesskey']
    paymentmode = request.POST.get('paymenttype')
    if paymentmode:
            paymentmode = request.POST.get('paymenttype')
    else:
            paymentmode = request.POST.get('paymenttype1')
    role = request.session['role']
    medepoid = request.session['medepoid']
    if role == 'Admin':
            if paymentmode == 'CASH':
                url = "http://13.235.112.1/ziva/mobile-api/tax-invoice-paymentupdate-admin.php"
                payload = json.dumps({
                    "accesskey": accesskey,
                    "depoid":medepoid,
                    "sonumber": request.POST.get('txtHdnId'),
                    "paymentmode": paymentmode,
                    "transaction_status": "success",
                    "transaction_id": "",
                })
            elif paymentmode == 'SCANNER':
                url = "http://13.235.112.1/ziva/mobile-api/tax-invoice-paymentupdate-admin.php"
                payload = json.dumps({
                    "accesskey": accesskey,
                    "depoid": medepoid,
                    "sonumber": request.POST.get('txtHdnId'),
                    "paymentmode":paymentmode,
                    "transaction_status": "success",
                    "transaction_id": request.POST.get("txnid"),
                })
            else:
                url = "http://13.235.112.1/ziva/mobile-api/tax-invoice-paymentupdate-admin.php"
                payload = json.dumps({
                    "accesskey": accesskey,
                    "depoid": medepoid,
                    "sonumber": request.POST.get('txtHdnId2'),
                    "paymentmode": paymentmode,
                    "transaction_status": "success"
                })
            headers = {
                'Content-Type': 'application/json'
            }
            response = requests.request("GET", url, headers=headers, data=payload)
            if response.status_code == 200:
                data = response.json()
                messages.success(request, data['message'])
                return redirect('sales_admin_list')
            elif response.status_code == 400:
                data = response.json()
                if data['message'] == 'Sorry! some details are missing':
                    messages.error(request, data['message'])
                    return render(request, 'create_indent/indent-list-admin.html')
                else:
                    messages.error(request, data['message'])
                    return redirect('/login')
            else:
                data = response.json()
                messages.error(request, data['message'])
                return redirect('sales_admin_list')
    else:
                if paymentmode == 'CASH':
                        url = "http://13.235.112.1/ziva/mobile-api/tax-invoice-paymentupdate.php"
                        payload = json.dumps({
                            "accesskey": accesskey,
                            "sonumber": request.POST.get('txtHdnId'),
                            "paymentmode": request.POST.get('paymenttype'),
                            "transaction_status": "success",
                            "transaction_id": "",
                        })
                elif paymentmode == 'scanner':
                        url = "http://13.235.112.1/ziva/mobile-api/tax-invoice-paymentupdate.php"
                        payload = json.dumps({
                            "accesskey": accesskey,
                            "sonumber": request.POST.get('txtHdnId'),
                            "paymentmode": request.POST.get('paymenttype'),
                            "transaction_status": "success",
                            "transaction_id": request.POST.get("txnid"),
                        })
                else:
                    url = "http://13.235.112.1/ziva/mobile-api/tax-invoice-qtyupdate.php"
                    payload = json.dumps({
                        "accesskey":accesskey,
                        "sonumber":request.POST.get('txtHdnId2'),
                        "paymentmode":request.POST.get('paymentmode'),
                        "transaction_status": "success"
                    })
                headers = {
                    'Content-Type': 'application/json'
                }
                response = requests.request("GET", url, headers=headers, data=payload)
                if response.status_code == 200:
                    data = response.json()
                    messages.success(request, data['message'])
                    return redirect('sales_list')
                elif response.status_code == 400:
                    data = response.json()
                    if data['message'] == 'Sorry! some details are missing':
                        messages.error(request, data['message'])
                        return redirect('sales_list')
                    else:
                        messages.error(request, data['message'])
                        return redirect('/login')
                else:
                    data = response.json()
                    messages.error(request, data['message'])
                    return redirect('sales_list')




def deliver_challan_item_update(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    accesskey = request.session['accesskey']
    id1=request.POST.get('txtHdnId')
    id2 = request.POST.get('status')
    url = "http://13.235.112.1/ziva/mobile-api/tax-invoice-itemqtyupdate.php"
    payload = json.dumps({
        "accesskey": accesskey,
        "sonumber":id1,
        "qty": request.POST.get('qty'),
        "uom": request.POST.get('cases'),
        "mrp": request.POST.get('mrp'),
        "sno": request.POST.get('sno')
    })
    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.request("GET", url, headers=headers, data=payload)
    if response.status_code == 200:
        data = response.json()
        messages.success(request, data['message'])
        url = reverse('sales_item_list_pending', args=[id1,id2])
        return redirect(url)
    elif response.status_code == 400:
        data = response.json()
        if data['message'] == 'Sorry! some details are missing':
            messages.error(request, data['message'])
            url = reverse('sales_item_list_pending', args=[id1,id2])
            return redirect(url)
        else:
            messages.error(request, data['message'])
            return render(request, 'login1.html')
    else:
        try:
            data = response.json()
            messages.error(request, data['message'])
        except:
            messages.error(request,"something went wrong")
        url = reverse('sales_item_list_pending', args=[id1,id2])
        return redirect(url)


def create_indent(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')

    try:
        displayrole = request.session['displayrole']
        code = request.session['codee']
        if displayrole == 'DEPOT STORE EXECUTIVE':
            menuname = request.session['mylist']
            accesskey = request.session['accesskey']
            url = "http://13.235.112.1/ziva/mobile-api/itemmaster-list-new.php"

            payload = json.dumps({"accesskey": accesskey})
            headers = {
                'Content-Type': 'application/json'
            }
            response = requests.request("GET", url, headers=headers, data=payload)
            data = response.json()
            item_masterlist = data['itemmasterlist']
            url = "http://13.235.112.1/ziva/mobile-api/warehousemaster-list.php"

            payload = json.dumps({"accesskey": accesskey})
            headers = {
                'Content-Type': 'text/plain'
            }
            response = requests.request("GET", url, headers=headers, data=payload)
            if response.status_code == 200:
                data = response.json()
                wh_masterlist = data['warehouselist']

            if request.method == 'POST':

                if code == 'BSP0135':
                    url = "http://13.235.112.1/ziva/mobile-api/create-busstation-indent-item.php"

                    payload = json.dumps({
                        "accesskey": accesskey,
                        "indentno": "",
                        "itemname": request.POST.get('itemname'),
                        "itemcode": request.POST.get('itemcode'),
                        "date ": request.POST.get('date'),
                        "qty": request.POST.get('quantity'),
                        "mrp": request.POST.get('price'),

                    })
                else:

                    url = "http://13.235.112.1/ziva/mobile-api/create-indent-item.php"

                    payload = json.dumps({
                            "accesskey": accesskey,
                            "indentno": "",
                            "itemname": request.POST.get('itemname'),
                            "itemcode": request.POST.get('itemcode'),
                            "warehouseid": request.POST.get('whcode'),
                            "warehousename": request.POST.get('whname'),
                            "date ": request.POST.get('date'),
                            "qty": request.POST.get('quantity'),
                            "mrp": request.POST.get('price'),

                        })
                headers = {
                    'Content-Type': 'text/plain'
                }
                response = requests.request("GET", url, headers=headers, data=payload)
                if response.status_code == 200:
                    data = response.json()
                    id=data['indentno']
                    messages.success(request, data['message'])
                    url = reverse('indent_item_list', args=[id])
                    return redirect(url)
                else:
                    try:
                        data = response.json()
                        messages.error(request, data['message'])
                        return redirect('/indent_list')
                    except:
                        messages.error(request,response.text)
                    return redirect('indent_list')
            return render(request, 'create_indent/create_indent.html',{'menuname':menuname,'item_masterlist':item_masterlist,'item_masterlist1':item_masterlist[0],'wh_masterlist':wh_masterlist})
        else:
            deponame = request.session['deponame']
            depoid = request.session['depoid']
            menuname = request.session['mylist']
            accesskey = request.session['accesskey']
            url = "http://13.235.112.1/ziva/mobile-api/itemmaster-list.php"

            payload = json.dumps({"accesskey": accesskey})
            headers = {
                'Content-Type': 'application/json'
            }
            response = requests.request("GET", url, headers=headers, data=payload)
            if response.status_code == 200:
                data = response.json()
                item_masterlist = data['itemmasterlist']
            url = "http://13.235.112.1/ziva/mobile-api/warehousemaster-list.php"

            payload = json.dumps({"accesskey": accesskey})
            headers = {
                'Content-Type': 'text/plain'
            }
            response = requests.request("GET", url, headers=headers, data=payload)
            if response.status_code == 200:
                data = response.json()
                wh_masterlist = data['warehouselist']

            if request.method == 'POST':
                if code == 'BSP0135':
                    url = "http://13.235.112.1/ziva/mobile-api/create-busstation-indent-item.php"

                    payload = json.dumps({
                        "accesskey": accesskey,
                        "indentno": "",
                        "itemname": request.POST.get('itemname'),
                        "itemcode": request.POST.get('itemcode'),
                        "date ": request.POST.get('date'),
                        "qty": request.POST.get('quantity'),
                        "mrp": request.POST.get('price'),

                    })
                else:
                    url = "http://13.235.112.1/ziva/mobile-api/create-indent-item.php"

                    payload = json.dumps({
                        "accesskey": accesskey,
                        "indentno": "",
                        "itemname": request.POST.get('itemname'),
                        "itemcode": request.POST.get('itemcode'),
                        "warehouseid": deponame,
                        "warehousename": depoid,
                        "date ": request.POST.get('date'),
                        "qty": request.POST.get('quantity'),
                        "mrp": request.POST.get('price'),

                    })
                headers = {
                    'Content-Type': 'text/plain'
                }
                response = requests.request("GET", url, headers=headers, data=payload)
                if response.status_code == 200:
                    data = response.json()
                    id = data['indentno']
                    messages.success(request, data['message'])
                    url = reverse('indent_item_list', args=[id])
                    return redirect(url)
                else:
                    try:
                        data = response.json()
                        messages.error(request, data['message'])
                        return redirect('indent_list')
                    except:
                        messages.error(request, response.text)
                    return redirect('indent_list')
            return render(request, 'create_indent/create_indent.html',
                          {'menuname': menuname, 'item_masterlist': item_masterlist, 'item_masterlist1': item_masterlist[0],
                           'wh_masterlist': wh_masterlist,"deponame":deponame})
    except:
        if response.status_code == 400:
            data = response.json()
            messages.error(request, data['message'])
            return render(request, 'login1.html')
    return render(request,'create_indent/create_indent.html')


def indent_list(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    menuname = request.session['mylist']
    accesskey = request.session['accesskey']
    displayrole = request.session['displayrole']
    role = request.session['role']
    if role == 'Admin':
        url = "http://13.235.112.1/ziva/mobile-api/indent-list-admin.php"

        payload = json.dumps({
                "accesskey": accesskey,"status": "Pending"
            })
        headers = {
                'Content-Type': 'application/json'
            }

        response = requests.request("GET", url, headers=headers, data=payload)
        if response.status_code == 200:
            data = response.json()
            ind_list = data['indentlist']
            return render(request, 'create_indent/indent-list-admin.html',
                          {"all_data": ind_list, 'all_data1': ind_list[0], 'menuname': menuname,'status':'Pending'})
        elif response.status_code == 400:
            data = response.json()
            messages.error(request, data['message'])
            return render(request, 'login1.html')
        else:
            return render(request, 'create_indent/indent-list-admin.html', {'menuname': menuname,'status':'Pending'})
    else:
            url = "http://13.235.112.1/ziva/mobile-api/indent-list-new.php"

            if displayrole == 'DEPOT STORE EXECUTIVE':
                payload = json.dumps({
                    "accesskey": accesskey,
                    "type": "Region",
                    "status":"Pending"
                })
            else:
                payload = json.dumps({
                    "accesskey": accesskey,
                    "type": "Bus station",
                    "status":"Pending"
                })
            headers = {
                'Content-Type': 'application/json'
            }

            response = requests.request("GET", url, headers=headers, data=payload)
            if response.status_code == 200:
                data = response.json()
                ind_list = data['indentlist']
                return render(request, 'create_indent/indent_list.html', {"all_data": ind_list,'all_data1':ind_list[0],'menuname':menuname})
            elif response.status_code == 400:
                data = response.json()
                messages.error(request, data['message'])
                return render(request, 'login1.html')
            else:
                return render(request, 'create_indent/indent_list.html',{'menuname':menuname})

def indent_list_approve(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    menuname = request.session['mylist']
    accesskey = request.session['accesskey']
    displayrole = request.session['displayrole']
    role = request.session['role']
    if role == 'Admin':
        url = "http://13.235.112.1/ziva/mobile-api/indent-list-admin.php"
        payload = json.dumps({
                "accesskey": accesskey,
                "status": "Approve"
            })
        headers = {
            'Content-Type': 'application/json'
        }
        response = requests.request("GET", url, headers=headers, data=payload)
        if response.status_code == 200:
            data = response.json()
            ind_list = data['indentlist']
            return render(request, 'create_indent/indent-list-admin.html',
                          {"all_data": ind_list, 'all_data1': ind_list[0], 'menuname': menuname})
        elif response.status_code == 400:
            data = response.json()
            if data['message'] == 'Sorry! some details are missing':
                messages.error(request, data['message'])
                return render(request, 'create_indent/indent-list-admin.html', {'menuname': menuname})
            else:
                messages.error(request, data['message'])
                return redirect('/login')
        else:
            return render(request, 'create_indent/indent_list.html', {'menuname': menuname})
    else:
            url = "http://13.235.112.1/ziva/mobile-api/indent-list-new.php"

            if displayrole == 'DEPOT STORE EXECUTIVE':
                payload = json.dumps({
                    "accesskey": accesskey,
                    "type": "Region",
                    "status":"Approve"
                })
            else:
                payload = json.dumps({
                    "accesskey": accesskey,
                    "type": "Bus station",
                    "status":"Approve"
                })
            headers = {
                'Content-Type': 'application/json'
            }

            response = requests.request("GET", url, headers=headers, data=payload)
            if response.status_code == 200:
                data = response.json()
                ind_list = data['indentlist']
                return render(request, 'create_indent/indent_list.html', {"all_data": ind_list,'all_data1':ind_list[0],'menuname':menuname})
            elif response.status_code == 400:
                data = response.json()
                if data['message'] == 'Sorry! some details are missing':
                    messages.error(request, data['message'])
                    return render(request, 'create_indent/indent_list.html', {'menuname': menuname})
                else:
                    messages.error(request, data['message'])
                    return redirect('/login')
            else:
                return render(request, 'create_indent/indent_list.html',{'menuname':menuname})

def indent_item_list1(request,id):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    menuname = request.session['mylist']
    accesskey = request.session['accesskey']
    url = "http://13.235.112.1/ziva/mobile-api/indent-itemqtyupdated-list.php"

    payload = json.dumps({
         "accesskey":accesskey,
            "dcnumber":id,
            "type":"Ready to Ship"})
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    if response.status_code == 200:
        data = response.json()
        ind_item_list = data['indentitemlist']
        return render(request, 'create_indent/indent_item_list1.html', {"all_data": ind_item_list,'menuname':menuname,'id':id})
    elif response.status_code == 400:
        data = response.json()
        if data['message'] == 'Sorry! some details are missing':
            messages.error(request, data['message'])
            return render(request, 'create_indent/indent-list-admin.html', {'menuname': menuname})
        else:
            messages.error(request, data['message'])
            return redirect('/login')
    else:
        try:
            r = response.json()
            messages.error(request, r['message'])
        except:
            messages.error(request, response.text)
        return render(request, 'create_indent/indent_item_list1.html',{'menuname':menuname,'id':id})




def indent_item_list_approve(request,id):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    menuname = request.session['mylist']
    accesskey = request.session['accesskey']
    url = "http://13.235.112.1/ziva/mobile-api/indent-itemqtyupdated-list.php"

    payload = json.dumps({
         "accesskey":accesskey,
            "dcnumber":id,
            "type":"Ready to Ship"})
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    if response.status_code == 200:
        data = response.json()
        ind_item_list = data['indentitemlist']
        return render(request, 'create_indent/indent_item_list_approve.html', {"all_data": ind_item_list,'menuname':menuname,'id':id})
    elif response.status_code == 400:
        data = response.json()
        messages.error(request, data['message'])
        return render(request, 'login1.html')
    else:
        return render(request, 'create_indent/indent_item_list_approve.html',{'menuname':menuname,'id':id})

def indent_item_list2(request,id):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    menuname = request.session['mylist']
    accesskey = request.session['accesskey']
    url = "http://13.235.112.1/ziva/mobile-api/indent-itemqtyupdated-list.php"

    payload = json.dumps({
         "accesskey":accesskey,
            "dcnumber":id,
            "type":"Partially Supplied"})
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    if response.status_code == 200:
        data = response.json()
        ind_item_list = data['indentitemlist']
        return render(request, 'create_indent/indent_item_list1.html', {"all_data": ind_item_list,'menuname':menuname})
    elif response.status_code == 400:
        data = response.json()
        messages.error(request, data['message'])
        return render(request, 'login1.html')
    else:
        return render(request, 'create_indent/indent_item_list1.html',{'menuname':menuname})

def qtyupdate_readytoship(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    id = request.POST.get('txtHdnId')
    dcid = request.POST.get('dcid')
    accesskey = request.session['accesskey']
    url = "http://13.235.112.1/ziva/mobile-api/qtyupdate-readytoship.php"

    payload = json.dumps({
        "accesskey": accesskey,
        "qty": request.POST.get('qty'),
        "sno": id,
    })
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    if response.status_code == 200:
        data = response.json()
        messages.success(request, data['message'])
        url = reverse('indent_item_list1', args=[dcid])
        return redirect(url)
    elif response.status_code == 400:
        data = response.json()
        messages.error(request, data['message'])
        return render(request, 'login1.html')
    else:
        try:
            data = response.json()
            messages.error(request, data['message'])
            url = reverse('indent_item_list1', args=[dcid])
            return redirect(url)
        except:
            messages.error(request, response.text)
        url = reverse('indent_item_list1', args=[id])
        return redirect(url)
def update_ack(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    accesskey = request.session['accesskey']
    id1 = request.session['id']
    fromname = request.session['fromname']
    fromid = request.session['fromid']
    toid = request.session['toid']
    toname = request.session['toname']
    id=request.POST.get('txtHdnId')
    id2 = request.POST.get('sno')
    url = "http://13.235.112.1/ziva/mobile-api/update-dispatchqty.php"

    payload = json.dumps({
        "accesskey": accesskey,
        "dispatchqty": request.POST.get('qty'),
        "fromname": fromname,
        "fromid": fromid,
        "remarks": request.POST.get('remarks'),
        "sno":id,
        "toid": toid,
        "toname":  toname
    })
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    if response.status_code == 200:
        data = response.json()
        messages.success(request,data['message'])
        #url = reverse('indent_item_list_ack', args=[id2])
        return redirect('/pending_indent_ack')
    elif response.status_code == 400:
        data = response.json()
        messages.error(request, data['message'])
        return render(request, 'login1.html')
    else:
        try:
            data = response.json()
            messages.error(request, data['message'])
            #url = reverse('indent_item_list_ack', args=[id2])
            return redirect('/pending_indent_ack')
        except:
            messages.error(request,response.text)
        #url = reverse('indent_item_list_ack', args=[id2])
        return redirect('/pending_indent_ack')
def add_indentitem(request,id):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    menuname = request.session['mylist']
    accesskey = request.session['accesskey']
    if role == 'Admin':
        if request.method == 'POST':
            url = "http://13.235.112.1/ziva/mobile-api/create-indent-item-admin.php"

            payload = json.dumps({
                "accesskey": accesskey,
                "indentno": "",
                "itemname": request.POST.get('itemname'),
                "itemcode": request.POST.get('itemname'),
                "qty": "1",
                "mrp": "8.75",
                "to_name": "Uppal",
                "to_id": "WDP0002",
                "from_name": "PKT",
                "from_id": "DEPO0059",
                "date": "2023-07-13"

            })
            headers = {
                'Content-Type': 'text/plain'
            }
            response = requests.request("GET", url, headers=headers, data=payload)
            if response.status_code == 200:
                data = response.json()
                id = data['indentno']
                messages.success(request, data['message'])
                url = reverse('indent_item_list', args=[id])
                return redirect(url)
            elif response.status_code == 400:
                data = response.json()
                messages.error(request, data['message'])
                return render(request, 'login1.html')
            else:
                try:
                    data = response.json()
                    messages.error(request, data['message'])
                    url = reverse('indent_item_list', args=[id])
                    return redirect(url)
                except:
                    messages.error(request, response.text)
                url = reverse('indent_item_list', args=[id])
                return redirect(url)
        url = reverse('indent_item_list', args=[id])
        return redirect(url)

    else:
                if request.method == 'POST':
                    code = request.session['codee']
                    if code == 'BSP0135':
                        url = "http://13.235.112.1/ziva/mobile-api/create-busstation-indent-item.php"

                        payload = json.dumps({
                            "accesskey": accesskey,
                            "indentno": id,
                            "itemname": request.POST.get('itemname'),
                            "itemcode": request.POST.get('itemcode'),
                            "date ": request.POST.get('date'),
                            "qty": request.POST.get('quantity'),
                            "mrp": request.POST.get('price'),

                        })
                    else:
                        url = "http://13.235.112.1/ziva/mobile-api/create-indent-item.php"

                        payload = json.dumps({
                            "accesskey": accesskey,
                            "indentno": id,
                            "itemname": request.POST.get('itemname'),
                            "itemcode": request.POST.get('itemcode'),
                            "warehouseid": request.POST.get('whcode'),
                            "warehousename": request.POST.get('whname'),
                            "date ": request.POST.get('date'),
                            "qty": request.POST.get('quantity'),
                            "mrp": request.POST.get('price'),

                        })
                    headers = {
                        'Content-Type': 'text/plain'
                    }
                    response = requests.request("GET", url, headers=headers, data=payload)
                    if response.status_code == 200:
                        data = response.json()
                        id = data['indentno']
                        messages.success(request, data['message'])
                        url = reverse('indent_item_list', args=[id])
                        return redirect(url)
                    elif response.status_code == 400:
                        data = response.json()
                        messages.error(request, data['message'])
                        return render(request, 'login1.html')
                    else:
                        try:
                            data = response.json()
                            messages.error(request, data['message'])
                            url = reverse('indent_item_list', args=[id])
                            return redirect(url)
                        except:
                            messages.error(request, response.text)
                        url = reverse('indent_item_list', args=[id])
                        return redirect(url)
                url = reverse('indent_item_list', args=[id])
                return redirect(url)


def indent_item_list(request,id):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    try:
        menuname = request.session['mylist']
        accesskey = request.session['accesskey']
        url = "http://13.235.112.1/ziva/mobile-api/itemmaster-list-new.php"

        payload = json.dumps({"accesskey": accesskey})
        headers = {
            'Content-Type': 'application/json'
        }
        response = requests.request("GET", url, headers=headers, data=payload)
        data = response.json()
        item_masterlist = data['itemmasterlist']
        role = request.session['role']
        if role  == 'Admin':
            if request.method == 'POST':
                url = "http://13.235.112.1/ziva/mobile-api/create-indent-item.php"

                payload = json.dumps({
                    "accesskey": accesskey,
                    "indentno": id,
                    "itemname": request.POST.get('itemname'),
                    "itemcode": request.POST.get('itemcode'),
                    "warehouseid": request.POST.get('whcode'),
                    "warehousename": request.POST.get('whname'),
                    "date ": request.POST.get('date'),
                    "qty": request.POST.get('quantity'),
                    "mrp": request.POST.get('price'),

                })
                headers = {
                    'Content-Type': 'text/plain'
                }
                response = requests.request("GET", url, headers=headers, data=payload)
                if response.status_code == 200:
                    data = response.json()
                    id = data['indentno']
                    messages.success(request, data['message'])
                    url = reverse('indent_item_list', args=[id])
                    return redirect(url)
                else:
                    try:
                        data = response.json()
                        messages.error(request, data['message'])
                        url = reverse('indent_item_list', args=[id])
                        return redirect(url)
                    except:
                        messages.error(request, response.text)
                    url = reverse('indent_item_list', args=[id])
                    return redirect(url)
            url = "http://13.235.112.1/ziva/mobile-api/indent-item-list.php"

            payload = json.dumps({
                "accesskey": accesskey,
                "indentno": id
            })
            headers = {
                'Content-Type': 'application/json'
            }

            response = requests.request("GET", url, headers=headers, data=payload)
            if response.status_code == 200:
                data = response.json()
                ind_item_list = data['indentitemlist']
                return render(request, 'create_indent/indent_item_list.html',
                              {"all_data": ind_item_list, 'data': ind_item_list[0], 'id': id, 'menuname': menuname,
                               'item_masterlist': item_masterlist})
            elif response.status_code == 400:
                data = response.json()
                messages.error(request, data['message'])
                return render(request, 'login1.html')
            else:
                return render(request, 'create_indent/indent_item_list.html',
                              {'menuname': menuname, 'id': id, 'data': 'Pending', 'item_masterlist':item_masterlist})
        else:

            if request.method == 'POST':
                code = request.session['codee']
                if code == 'BSP0135':
                    url = "http://13.235.112.1/ziva/mobile-api/create-busstation-indent-item.php"

                    payload = json.dumps({
                        "accesskey": accesskey,
                        "indentno": id,
                        "itemname": request.POST.get('itemname'),
                        "itemcode": request.POST.get('itemcode'),
                        "date ": request.POST.get('date'),
                        "qty": request.POST.get('quantity'),
                        "mrp": request.POST.get('price'),

                    })
                else:

                    url = "http://13.235.112.1/ziva/mobile-api/create-indent-item.php"

                    payload = json.dumps({
                        "accesskey": accesskey,
                        "indentno": id,
                        "itemname": request.POST.get('itemname'),
                        "itemcode": request.POST.get('itemcode'),
                        "qty": request.POST.get('quantity'),
                        "mrp": request.POST.get('mrp1'),
                    })
                headers = {
                    'Content-Type': 'text/plain'
                }
                response = requests.request("GET", url, headers=headers, data=payload)
                if response.status_code == 200:
                    data = response.json()
                    id = data['indentno']
                    messages.success(request, data['message'])
                    url = reverse('indent_item_list', args=[id])
                    return redirect(url)
                else:
                    try:
                        data = response.json()
                        messages.error(request, data['message'])
                        url = reverse('indent_item_list', args=[id])
                        return redirect(url)
                    except:
                        messages.error(request, response.text)
                    url = reverse('indent_item_list', args=[id])
                    return redirect(url)
            url = "http://13.235.112.1/ziva/mobile-api/indent-item-list.php"

            payload = json.dumps({
                "accesskey": accesskey,
                "indentno":id
            })
            headers = {
                'Content-Type': 'application/json'
            }

            response = requests.request("GET", url, headers=headers, data=payload)
            if response.status_code == 200:
                data = response.json()
                ind_item_list = data['indentitemlist']
                return render(request, 'create_indent/indent_item_list.html', {"all_data": ind_item_list,'data':ind_item_list[0],'id':id,'menuname':menuname,'item_masterlist':item_masterlist})
            elif response.status_code == 400:
                data = response.json()
                messages.error(request, data['message'])
                return render(request, 'login1.html')
            else:
                return render(request, 'create_indent/indent_item_list.html',{'menuname':menuname,'id':id,'data':'Pending','item_masterlist':item_masterlist})
    except:
        if response.status_code == 400:
            data = response.json()
            messages.error(request, data['message'])
            return render(request, 'login1.html')
    return render(request,'create_indent/indent_item_list.html')


def pending_indent_item_list(request,id):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    menuname = request.session['mylist']
    accesskey = request.session['accesskey']
    url = "http://13.235.112.1/ziva/mobile-api/indent-item-list.php"

    payload = json.dumps({
        "accesskey": accesskey,
        "indentno": id
    })
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    if response.status_code == 200:
        data = response.json()
        ind_item_list = data['indentitemlist']
        return render(request, 'create_indent/pending_indent_item_list.html',
                      {"all_data": ind_item_list, 'id': id, 'menuname': menuname,
                       })
    elif response.status_code == 400:
        data = response.json()
        messages.error(request, data['message'])
        return render(request, 'login1.html')
    else:
        try:
            data = response.json()
            messages.error(request, data['message'])
            return render(request, 'create_indent/pending_indent_item_list.html', {'menuname': menuname,"id":id})
        except:
            return render(request, 'create_indent/pending_indent_item_list.html', {'menuname': menuname, "id": id})

def delete_indent_item(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    menuname = request.session['mylist']
    role = request.session['role']
    accesskey = request.session['accesskey']
    if role == 'Admin':

            url = "http://13.235.112.1/ziva/mobile-api/delete-indentitem-admin.php"
            id = request.POST.get('indentid')
            payload = json.dumps({
                "accesskey": accesskey,
                "sno": request.POST.get('sno')
            })
            headers = {
                'Content-Type': 'application/json'
            }

            response = requests.request("GET", url, headers=headers, data=payload)
            if response.status_code == 200:
                data = response.json()
                messages.success(request, data['message'])
                url = reverse('indent_item_list', args=[id])
                return redirect(url)
            elif response.status_code == 400:
                data = response.json()
                messages.error(request, data['message'])
                return render(request, 'login1.html')
            else:
                data = response.json()
                messages.success(request, data['message'])
                url = reverse('indent_item_list', args=[id])
                return redirect(url)
    else:
        url = "http://13.235.112.1/ziva/mobile-api/delete-indentitem.php"
        id = request.POST.get('indentid')
        payload = json.dumps({
            "accesskey": accesskey,
            "sno": request.POST.get('sno')
        })
        headers = {
            'Content-Type': 'application/json'
        }

        response = requests.request("GET", url, headers=headers, data=payload)
        if response.status_code == 200:
            data = response.json()
            messages.success(request, data['message'])
            url = reverse('indent_item_list', args=[id])
            return redirect(url)
        elif response.status_code == 400:
            data = response.json()
            messages.error(request, data['message'])
            return render(request, 'login1.html')
        else:
            data = response.json()
            messages.success(request, data['message'])
            url = reverse('indent_item_list', args=[id])
            return redirect(url)
def delete_indent(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    menuname = request.session['mylist']
    accesskey = request.session['accesskey']
    role = request.session['role']
    if role == 'Admin':
        url = "http://13.235.112.1/ziva/mobile-api/delete-indent-admin.php"

        payload = json.dumps({
            "accesskey": accesskey,
            "indentno": request.POST.get('indentid')
        })

        headers = {
            'Content-Type': 'application/json'
        }

        response = requests.request("GET", url, headers=headers, data=payload)
        if response.status_code == 200:
            data = response.json()
            messages.success(request,data['message'])
            return redirect('/indent_list')
        elif response.status_code == 400:
            data = response.json()
            messages.error(request, data['message'])
            return render(request, 'login1.html')
        else:
            data = response.json()
            messages.success(request, data['message'])
            return redirect('/indent_list')
    else:
        url = "http://13.235.112.1/ziva/mobile-api/delete-indent.php"

        payload = json.dumps({
            "accesskey": accesskey,
            "indentno": request.POST.get('indentid')
        })
        headers = {
            'Content-Type': 'application/json'
        }

        response = requests.request("GET", url, headers=headers, data=payload)
        if response.status_code == 200:
            data = response.json()
            messages.success(request, data['message'])
            return redirect('/indent_list')
        elif response.status_code == 400:
            data = response.json()
            messages.error(request, data['message'])
            return render(request, 'login1.html')
        else:
            data = response.json()
            messages.success(request, data['message'])
            return redirect('/indent_list')

def indent_item_list_ack(request, id):
        if 'accesskey' not in request.session:
            messages.error(request, 'Access denied!')
            return redirect('/login')
        menuname = request.session['mylist']
        accesskey = request.session['accesskey']

        url = "http://13.235.112.1/ziva/mobile-api/indent-item-list.php"

        payload = json.dumps({
            "accesskey": accesskey,
            "indentno": id
        })
        headers = {
            'Content-Type': 'application/json'
        }
        response = requests.request("GET", url, headers=headers, data=payload)
        if response.status_code == 200:
            data = response.json()
            ind_item_list = data['indentitemlist']
            fromname = data['fromname']
            fromid = data['fromid']
            toname = data['toname']
            toid = data['toid']
            request.session['fromname']=fromname
            request.session['fromid'] = fromid
            request.session['toname'] = toname
            request.session['toid'] = toid
            return render(request, 'create_indent/indent_list_ack.html', {'menuname':menuname,"all_data": ind_item_list,'id':id})
        elif response.status_code == 400:
            data = response.json()
            messages.error(request, data['message'])
            return render(request, 'login1.html')
        else:
            return render(request, 'create_indent/indent_list_ack.html',{'menuname':menuname,'id':id})


def out_passlist(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    menuname = request.session['mylist']
    accesskey = request.session['accesskey']
    if request.method == 'POST':
        url = "http://13.235.112.1/ziva/mobile-api/outpassgenerate-list.php"

        payload = json.dumps({
            "accesskey": accesskey,
            "fdate": request.POST.get('fdate'),
            "tdate": request.POST.get('tdate'),
            "status":"Pending"

        })
        headers = {
            'Content-Type': 'application/json'
        }

        response = requests.request("GET", url, headers=headers, data=payload)
        if response.status_code == 200:
            data = response.json()
            outpass_list = data['indentlist']

            return render(request, 'create_indent/outpass_list.html', {"all_data": outpass_list,'menuname':menuname})
        elif response.status_code == 400:
            data = response.json()
            messages.error(request, data['message'])
            return render(request, 'login1.html')
        else:

            return render(request, 'create_indent/outpass_list.html',{'menuname':menuname})
    else:

        url = "http://13.235.112.1/ziva/mobile-api/outpassgenerate-list.php"

        payload = json.dumps({
            "accesskey": accesskey,
            "fdate": 'All',
            "tdate": 'All',
            "status":"Pending"
        })
        headers = {
            'Content-Type': 'application/json'
        }

        response = requests.request("GET", url, headers=headers, data=payload)
        if response.status_code == 200:
            data = response.json()
            outpass_list = data['indentlist']
            return render(request, 'create_indent/outpass_list.html', {"all_data": outpass_list, 'menuname': menuname})
        elif response.status_code == 400:
            data = response.json()
            messages.error(request, data['message'])
            return render(request, 'login1.html')
        else:

            return render(request, 'create_indent/outpass_list.html', {'menuname': menuname})


def out_pass_itemlist(request,id):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    menuname = request.session['mylist']
    accesskey = request.session['accesskey']
    url = "http://13.235.112.1/ziva/mobile-api/outpassitem-list.php"

    payload = json.dumps({
        "accesskey": accesskey,
        "dcnumber":id
    })
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    if response.status_code == 200:
        data = response.json()
        outpassitem_list = data['Outpassitemlist']
        return render(request, 'create_indent/out_pass_itemlist.html', {"all_data": outpassitem_list,'menuname':menuname})
    elif response.status_code == 400:
        data = response.json()
        messages.error(request, data['message'])
        return render(request, 'login1.html')
    else:
        return render(request, 'create_indent/out_pass_itemlist.html',{'menuname':menuname})



def out_pass_scanner(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    menuname = request.session['mylist']
    if request.method == 'POST':

        accesskey = request.session['accesskey']
        url = "http://13.235.112.1/ziva/mobile-api/outpassapproved.php"
        outpass_id = request.POST.get("outpassid")
        encoded_id = base64.b64encode(outpass_id.encode('utf-8'))
        payload = {
        "accesskey":accesskey,
        "outpass_number":encoded_id

        }
        payload = json.dumps(payload, cls=BytesEncoder)
        headers = {
            'Content-Type': 'application/json'
        }

        response = requests.request("POST", url, headers=headers, data=payload)
        if response.status_code == 200:
            data2 = response.json()
            messages.success(request,data2['message'])
            return render(request, 'create_indent/out_pass_scanner.html',{'menuname':menuname})
        elif response.status_code == 400:
            data = response.json()
            messages.error(request, data['message'])
            return render(request, 'login1.html')
        else:
            try:
                data2 = response.json()
                messages.error(request,data2['message'])
                return render(request, 'create_indent/out_pass_scanner.html',{'menuname':menuname})
            except:
                messages.error(request,response.text)
            return render(request, 'create_indent/out_pass_scanner.html',{'menuname':menuname})
    return render(request, 'create_indent/out_pass_scanner.html',{'menuname':menuname})



def out_passlist1(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    menuname = request.session['mylist']
    accesskey = request.session['accesskey']
    if request.method == 'POST':
        url = "http://13.235.112.1/ziva/mobile-api/outpassgenerate-list.php"

        payload = json.dumps({
            "accesskey": accesskey,
            "fdate": request.POST.get('fdate'),
            "tdate": request.POST.get('tdate'),
            "status":"Approve"
        })
        headers = {
            'Content-Type': 'application/json'
        }
        response = requests.request("GET", url, headers=headers, data=payload)
        if response.status_code == 200:
            data = response.json()
            outpass_list = data['indentlist']
            return render(request, 'create_indent/outpass_list.html', {"all_data": outpass_list,'menuname':menuname})
        elif response.status_code == 400:
            data = response.json()
            messages.error(request, data['message'])
            return render(request, 'login1.html')
        else:
            return render(request, 'create_indent/outpass_list.html',{'menuname':menuname})
    else:

        url = "http://13.235.112.1/ziva/mobile-api/outpassgenerate-list.php"

        payload = json.dumps({
            "accesskey": accesskey,
            "fdate": 'All',
            "tdate": 'All',
            "status": "Approve"
        })
        headers = {
            'Content-Type': 'application/json'
        }

        response = requests.request("GET", url, headers=headers, data=payload)
        if response.status_code == 200:
            data = response.json()
            outpass_list = data['indentlist']
            return render(request, 'create_indent/outpass_list.html', {"all_data": outpass_list, 'menuname': menuname})
        elif response.status_code == 400:
            data = response.json()
            messages.error(request, data['message'])
            return render(request, 'login1.html')
        else:
            return render(request, 'create_indent/outpass_list.html', {'menuname': menuname})


def out_pass_itemlist(request,id):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    menuname = request.session['mylist']
    accesskey = request.session['accesskey']
    url = "http://13.235.112.1/ziva/mobile-api/outpassitem-list.php"

    payload = json.dumps({
        "accesskey": accesskey,
        "dcnumber":id
    })
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    if response.status_code == 200:
        data = response.json()
        outpassitem_list = data['Outpassitemlist']
        return render(request, 'create_indent/out_pass_itemlist.html', {"all_data": outpassitem_list,'menuname':menuname})
    elif response.status_code == 400:
        data = response.json()
        messages.error(request, data['message'])
        return render(request, 'login1.html')
    else:
        return render(request, 'create_indent/out_pass_itemlist.html',{'menuname':menuname})



def out_pass_scanner(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    menuname = request.session['mylist']
    if request.method == 'POST':

        accesskey = request.session['accesskey']
        url = "http://13.235.112.1/ziva/mobile-api/outpassapproved.php"
        outpass_id = request.POST.get("outpassid")
        encoded_id = base64.b64encode(outpass_id.encode('utf-8'))
        payload = {
        "accesskey":accesskey,
        "outpass_number":encoded_id

        }
        payload = json.dumps(payload, cls=BytesEncoder)
        headers = {
            'Content-Type': 'application/json'
        }

        response = requests.request("POST", url, headers=headers, data=payload)
        if response.status_code == 200:
            data2 = response.json()
            messages.success(request,data2['message'])
            return render(request, 'create_indent/out_pass_scanner.html',{'menuname':menuname})
        elif response.status_code == 400:
            data = response.json()
            messages.error(request, data['message'])
            return render(request, 'login1.html')
        else:
            try:
                data2 = response.json()
                messages.error(request,data2['message'])
                return render(request, 'create_indent/out_pass_scanner.html',{'menuname':menuname})
            except:
                messages.error(request,response.text)
            return render(request, 'create_indent/out_pass_scanner.html',{'menuname':menuname})
    return render(request, 'create_indent/out_pass_scanner.html',{'menuname':menuname})
def approved_indlist_pending(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    menuname = request.session['mylist']
    accesskey = request.session['accesskey']
    if request.method == 'POST':
        url = "http://13.235.112.1/ziva/mobile-api/departmentstock-list.php"
        fdate = request.POST.get('fdate')
        tdate = request.POST.get('tdate')
        payload = json.dumps({
            "accesskey": accesskey,
            "fdate": fdate,
            "tdate": tdate,
            "status":"Out For Delivery"
        })
        headers = {
            'Content-Type': 'application/json'
        }

        response = requests.request("GET", url, headers=headers, data=payload)
        if response.status_code == 200:
            data = response.json()
            approved_list = data['stocklist']
            return render(request, 'create_indent/approved_indlist.html', {"all_data": approved_list,'menuname':menuname,'fdate':fdate,'tdate':tdate})
        elif response.status_code == 400:
            data = response.json()
            if data['message'] == 'Sorry! some details are missing':
                messages.error(request, data['message'])
                return redirect('/busstation_item_add')
            else:
                messages.error(request, data['message'])
                return redirect('/login')
        else:
            return render(request, 'create_indent/approved_indlist.html',{'menuname':menuname,'fdate':fdate,'tdate':tdate})
    else:
        url = "http://13.235.112.1/ziva/mobile-api/departmentstock-list.php"
        payload = json.dumps({
            "accesskey": accesskey,
            "fdate": "All",
            "tdate": "All",
            "status": "Out For Delivery"
        })
        headers = {
            'Content-Type': 'application/json'
        }

        response = requests.request("GET", url, headers=headers, data=payload)
        if response.status_code == 200:
            data = response.json()
            approved_list = data['stocklist']

            return render(request, 'create_indent/approved_indlist.html',
                          {"all_data": approved_list, 'menuname': menuname})
        elif response.status_code == 400:
            data = response.json()
            if data['message'] == 'Sorry! some details are missing':
                messages.error(request, data['message'])
                return redirect('/busstation_item_add')
            else:
                messages.error(request, data['message'])
                return redirect('/login')
        else:
            return render(request, 'create_indent/approved_indlist.html',
                          {'menuname': menuname})

def approve_item_list(request,id):
        if 'accesskey' not in request.session:
            messages.error(request, 'Access denied!')
            return redirect('/login')
        menuname = request.session['mylist']
        accesskey = request.session['accesskey']

        url = "http://13.235.112.1/ziva/mobile-api/departitemstocklist.php"

        payload = json.dumps({
            "accesskey": accesskey,
            "dcnumber": id
        })
        headers = {
            'Content-Type': 'application/json'
        }

        response = requests.request("GET", url, headers=headers, data=payload)

        if response.status_code == 200:
            data = response.json()
            approved_item_list = data['stocklist']
            return render(request, 'create_indent/approved_item_list.html', {"all_data": approved_item_list,'menuname':menuname})
        elif response.status_code == 400:
            data = response.json()
            messages.error(request, data['message'])
            return render(request, 'login1.html')
        else:
            return render(request, 'create_indent/approved_item_list.html',{'menuname':menuname})


def approve_accept(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    accesskey = request.session['accesskey']
    role = request.session['role']
    if role == 'Admin':
        url = "http://13.235.112.1/ziva/mobile-api/submit-items-accepted-admin.php"

        payload = json.dumps({
            "accesskey": accesskey,
            "outpass_number": request.POST.get("id"),
            "remarks": request.POST.get("remarks"),
            "qty": request.POST.get("qty")
        })
        headers = {
            'Content-Type': 'application/json'
        }

        response = requests.request("GET", url, headers=headers, data=payload)
        if response.status_code == 200:
            data = response.json()
            messages.success(request, data['message'])
            return redirect('/approve_list_admin1')
        elif response.status_code == 400:
            data = response.json()
            messages.error(request, data['message'])
            return render(request, 'login1.html')
        else:
            try:
                data = response.json()
                messages.error(request, data['message'])

            except:
                messages.error(request, response.text)
            return redirect('/approve_list_admin1')
    else:
            url = "http://13.235.112.1/ziva/mobile-api/submit-items-accepted.php"

            payload = json.dumps({
                "accesskey": accesskey,
                "outpass_number": request.POST.get("id"),
                "remarks": request.POST.get("remarks"),
                "qty": request.POST.get("qty")
            })
            headers = {
                'Content-Type': 'application/json'
            }

            response = requests.request("GET", url, headers=headers, data=payload)
            if response.status_code == 200:
                data = response.json()
                messages.success(request,data['message'])
                return redirect('/approved_indlist_accept')
            elif response.status_code == 400:
                data = response.json()
                messages.error(request, data['message'])
                return render(request, 'login1.html')
            else:
                try:
                    data = response.json()
                    messages.error(request, data['message'])

                except:
                    messages.error(request,response.text)
                return redirect('/approved_indlist_accept')
def approved_indlist_accept(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    menuname = request.session['mylist']
    accesskey = request.session['accesskey']
    if request.method == 'POST':
        url = "http://13.235.112.1/ziva/mobile-api/departmentstock-list.php"
        fdate = request.POST.get('fdate')
        tdate = request.POST.get('tdate')
        payload = json.dumps({
            "accesskey": accesskey,
            "fdate": fdate,
            "tdate": tdate,
            "status": "Accept",

        })
        headers = {
            'Content-Type': 'application/json'
        }

        response = requests.request("GET", url, headers=headers, data=payload)
        if response.status_code == 200:
            data = response.json()
            approved_list = data['stocklist']

            return render(request, 'create_indent/approved_indlist.html', {"all_data": approved_list,'menuname':menuname,'fdate':fdate,'tdate':tdate})
        elif response.status_code == 400:
            data = response.json()
            messages.error(request, data['message'])
            return render(request, 'login1.html')
        else:
            return render(request, 'create_indent/approved_indlist.html',{'menuname':menuname,'fdate':fdate,'tdate':tdate})
    else:
        url = "http://13.235.112.1/ziva/mobile-api/departmentstock-list.php"

        payload = json.dumps({
            "accesskey": accesskey,
            "fdate": "All",
            "tdate": "All",
            "status": "Accept"
        })
        headers = {
            'Content-Type': 'application/json'
        }

        response = requests.request("GET", url, headers=headers, data=payload)
        if response.status_code == 200:
            data = response.json()
            approved_list = data['stocklist']
            return render(request, 'create_indent/approved_indlist.html',
                          {"all_data": approved_list, 'menuname': menuname})
        elif response.status_code == 400:
            data = response.json()
            messages.error(request, data['message'])
            return render(request, 'login1.html')
        else:
            return render(request, 'create_indent/approved_indlist.html', {'menuname': menuname})

def get_grn_item_data(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    accesskey = request.session['accesskey']
    itemname = request.POST.get('itemname')

    url = "http://13.235.112.1/ziva/mobile-api/itemmaster-search-new.php"

    payload = json.dumps({
        "accesskey": accesskey,
    })

    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    if response.status_code == 200:
        data = response.json()
        itemmasterlist = data['itemmasterlist']
        for i in itemmasterlist:
            if str(i['itemcode']) == itemname:
                data = {"mrp": i["mrp"], "uom": i["uom"], "itemname": i["itemname"],"sno":i['sno']}
        return JsonResponse({'data': data})
    elif response.status_code == 400:
        data = response.json()
        messages.error(request, data['message'])
        return render(request, 'login1.html')
    else:
            try:
                data = response.json()
                messages.error(request, data['message'])
            except:
                messages.error(request, response.text)
            return redirect('/add_grnitem')

def get_grn_item(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    accesskey = request.session['accesskey']
    id=request.POST.get('itemcode')
    url = "http://13.235.112.1/ziva/mobile-api/grn-item-list.php"

    payload = json.dumps({
        "accesskey": accesskey,
        "grnno":request.POST.get('id')
    })

    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    if response.status_code == 200:
        data = response.json()
        grnitemlist = data['grnitemlist']
        for i in grnitemlist:
            if str(i['item_code']) == id:
                data = {"id":i['id'],"mrp": i["mrp"], "quantity":i["quantity"],"noofbottles":i['noofbottles'],"uom": i["uom"],
                        "item_code":i['item_code'],"batch_no":i['batch_no'],"itemname": i["item_name"],"sno":i['inv_sno'],"purchase_price":i['purchase_price'],'expiry_date':i['expiry_date']}
        return JsonResponse({'data': data})
    elif response.status_code == 400:
        data = response.json()
        messages.error(request, data['message'])
        return render(request, 'login1.html')
    else:
            try:
                data = response.json()
                messages.error(request, data['message'])
            except:
                messages.error(request, response.text)
            return redirect('/add_grnitem')

def get_price1(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    region = request.session['regionid']
    accesskey = request.session['accesskey']
    itemcode = request.POST.get('itemname')

    url = "http://13.235.112.1/ziva/mobile-api/price-master-list.php"

    payload = json.dumps({
        "accesskey":accesskey,
        "regioncode":region,
        "itemcode":itemcode
    })

    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    if response.status_code == 200:
        data2 = response.json()
        return JsonResponse({'data': data2})
    elif response.status_code == 400:
        data = response.json()
        if data['message'] == 'Sorry! some details are missing':
            return JsonResponse({'data': data})
        else:
            messages.error(request, data['message'])
            return redirect('/login')
    elif response.status_code == 503:
        data = response.json()
        return JsonResponse({'data': data})
    elif response.status_code == 500:
        data = {'error': 'true', 'message': 'Internal server error'}
        return JsonResponse({'data': data})
    else:
        data = {'error': 'true', 'message': 'something went wrong'}
        return JsonResponse({'data': data})
def proforma_item(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    accesskey = request.session['accesskey']
    itemname = request.POST.get('itemname')
    role =  request.session['role']
    if role == 'Admin':
        url = "http://13.235.112.1/ziva/mobile-api/itemmaster-list-admin.php"
        payload = json.dumps({
            "accesskey": accesskey,"warehousename": "All", "regionid": "All", "depoid":request.POST.get('depo')
        })
    else:
        url = "http://13.235.112.1/ziva/mobile-api/itemmaster-list.php"
        payload = json.dumps({
            "accesskey": accesskey,
        })

    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    if response.status_code == 200:
        data = response.json()
        list = data['itemmasterlist']
        for i in list:
            if str(i['itemcode']) == itemname:
                data = {"itemname": i["itemname"], "itemcode": i["itemcode"], "uom": i["uom"],
                         "mrp": i['mrp'],
                        }
        return JsonResponse({'data': data})
    elif response.status_code == 400:
        data = response.json()
        if data['message'] == 'Sorry! some details are missing':
            return JsonResponse({'data': data})
        else:
            messages.error(request, data['message'])
            return redirect('/login')
    elif response.status_code == 503:
        data = response.json()
        return JsonResponse({'data': data})
    elif response.status_code == 500:
        data = {'error': 'true', 'message': 'Internal server error'}
        return JsonResponse({'data': data})
    else:
        data = {'error': 'true', 'message': 'something went wrong'}
        return JsonResponse({'data': data})



def get_indentitem(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    accesskey = request.session['accesskey']
    itemname = request.POST.get('itemname')

    url = "http://13.235.112.1/ziva/mobile-api/itemmaster-search.php"

    payload = json.dumps({
        "accesskey": accesskey,
        "itemcode": itemname
    })

    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    if response.status_code == 200:
        data2 = response.json()
        return JsonResponse({'data': data2})
    elif response.status_code == 400:
        data = response.json()
        if data['message'] == 'Sorry! some details are missing':
            return JsonResponse({'data': data})
        else:
            messages.error(request, data['message'])
            return redirect('/login')
    elif response.status_code == 503:
        data = response.json()
        return JsonResponse({'data': data})
    elif response.status_code == 500:
        data = {'error': 'true', 'message': 'Internal server error'}
        return JsonResponse({'data': data})
    else:
        data = {'error':'true','message': 'something went wrong'}
        return JsonResponse({'data': data})


@csrf_exempt
def get_item_data(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    accesskey = request.session['accesskey']

    name = request.POST.get('name')

    url = "http://13.235.112.1/ziva/mobile-api/itemmaster-search.php"

    payload = json.dumps({
        "accesskey": accesskey,
        "itemcode": name
    })

    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    if response.status_code == 200:
        data2 = response.json()
        return JsonResponse({'data': data2})
    elif response.status_code == 400:
        data = response.json()
        if data['message'] == 'Sorry! some details are missing':
            return JsonResponse({'data': data})
        else:
            messages.error(request, data['message'])
            return redirect('/login')
    elif response.status_code == 503:
        data = response.json()
        return JsonResponse({'data': data})
    elif response.status_code == 500:
        data = {'error': 'true', 'message': 'Internal server error'}
        return JsonResponse({'data': data})
    else:
        data = {'error': 'true', 'message': 'something went wrong'}
        return JsonResponse({'data': data})


@csrf_exempt
def get_sale_item_data(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    itemname = request.POST.get('itemcode')

    url = "http://13.235.112.1/ziva/mobile-api/inventory-search.php"

    payload = json.dumps({

        "accesskey": "MDY5MjAyMDIyLTEyLTE3IDA2OjE1OjU4",
        "searchterm": itemname,
        "storeid": request.POST.get("storeid"),

    })

    headers = {
        'Content-Type': 'application/json'
    }

    if response.status_code == 200:
        data2 = response.json()
        return JsonResponse({'data': data2})
    elif response.status_code == 400:
        data = response.json()
        if data['message'] == 'Sorry! some details are missing':
            return JsonResponse({'data': data})
        else:
            messages.error(request, data['message'])
            return redirect('/login')
    elif response.status_code == 503:
        data = response.json()
        return JsonResponse({'data': data})
    elif response.status_code == 500:
        data = {'error': 'true', 'message': 'Internal server error'}
        return JsonResponse({'data': data})
    else:
        data = {'error': 'true', 'message': 'something went wrong'}
        return JsonResponse({'data': data})


def item_edit(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    accesskey = request.session['accesskey']


    if request.method == "POST":
        url = "http://13.235.112.1/ziva/mobile-api/edit-itemmaster.php"

        payload = json.dumps({
            "accesskey":accesskey ,
            "itemname": request.POST.get('nameitem'),
            "hsncode": request.POST.get('hsn1'),
            "lpp": request.POST.get('latestpurchase'),
            "gst": request.POST.get('gst'),
            "item_code":request.POST.get('codeitem'),
            "category": request.POST.get('category'),
            "mrp": request.POST.get('mrp'),
            "manufacturername": request.POST.get('manufacture'),
            "uom": request.POST.get('uom'),
            "sno": request.POST.get('itemid')
        })
        headers = {
            'Content-Type': 'application/json'
        }

        response = requests.request("GET", url, headers=headers, data=payload)

        data = response.json()

        if response.status_code == 200:
            messages.success(request, data['message'])
            return redirect('/item_list')
        elif response.status_code == 400:
            data = response.json()
            text =  data['message']
            if  'some details are missing' in text:
                messages.error(request, data['message'])
                return redirect('/item_list')
            else:
                messages.error(request, data['message'])
                return redirect('/login')
        else:
            try:
                r = response.json()
                messages.error(request, r['message'])
            except:
                messages.error(request, response.text)
            return redirect('/item_list')
    return redirect('/item_list')

def vendor_edit(request):
    pass


def get_warehouse(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    accesskey = request.session['accesskey']
    id = request.POST.get('id')
    url = "http://13.235.112.1/ziva/mobile-api/warehousemaster-list.php"

    payload = json.dumps({
        "accesskey":accesskey
    })
    headers = {
        'Content-Type': 'text/plain'
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    if response.status_code == 200:
        data = response.json()
        wh_masterlist = data['warehouselist']
        for i in wh_masterlist:
            if str(i['warehouseid']) == id:
                data = {"sno":i["sno"],"warehouseid":i["warehouseid"],"warehousename":i["warehousename"],"wh_manager":i['wh_manager'],
                        "gst_no":i['gst_no'],"panno":i['panno'],"address":i['address'],"licenseno":i['licenseno'],
                        "wh_contact_no":i["wh_contact_no"],"location":i["location"],"whcode":i["warehouse_code_org"]}
    return JsonResponse({'data': data})




def warehouse_edit(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    accesskey = request.session['accesskey']
    if request.method == 'POST':
        url = "http://13.235.112.1/ziva/mobile-api/edit-warehousemaster.php"

        payload = json.dumps({
            "accesskey": accesskey,
            "warehouseid": request.POST.get('whid'),
            "warehousename": request.POST.get('warehousename1'),
            "gstnumber": request.POST.get('gstwh'),
            "licenseno": request.POST.get('licnumwh'),
            "panno": request.POST.get('panwh'),
            "address": request.POST.get('addresswh'),
            "wh_manager":request.POST.get('manager'),
            "location": request.POST.get('location'),
            "wh_contact_no": request.POST.get('mobilewh'),
            "warehouse_code":request.POST.get('whcode'),
        })
        headers = {
            'Content-Type': 'application/json'
        }

        response = requests.request("GET", url, headers=headers, data=payload)

        if response.status_code == 200:
            data = response.json()
            messages.success(request, data['message'])
            return redirect('/warehouse_list')
        elif response.status_code == 400:
            data = response.json()
            if data['message'] == 'Sorry! some details are missing':
                messages.error(request, data['message'])
                return redirect('/warehouse_list')
            else:
                messages.error(request, data['message'])
                return redirect('/login')
        else:
            try:
                r = response.json()
                messages.error(request, r['message'])
            except:
                messages.error(request, response.text)
            return redirect('/warehouse_list')



def des_edit(request):
    pass
def get_depo(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    accesskey = request.session['accesskey']
    url = "http://13.235.112.1/ziva/mobile-api/depo-search.php"

    payload = json.dumps({
        "accesskey": accesskey,
        "depoid": request.POST.get('id')
    })

    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    if response.status_code == 200:
        data2 = response.json()
        return JsonResponse({'data': data2})
    elif response.status_code == 400:
        data = response.json()
        if data['message'] == 'Sorry! some details are missing':
            return JsonResponse({'data': data})
        else:
            messages.error(request, data['message'])
            return redirect('/login')
    elif response.status_code == 503:
        data = response.json()
        return JsonResponse({'data': data})
    else:
        return redirect('/depo_list')
def depo_edit(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    accesskey = request.session['accesskey']
    payload = json.dumps({"accesskey": accesskey})
    headers = {
        'Content-Type': 'application/json'
    }
    url = "http://13.235.112.1/ziva/mobile-api/region-list.php"
    response = requests.request("POST", url, headers=headers, data=payload)
    if response.status_code == 200:
        data = response.json()
        regionlist = data['regionlist']
    else:
        try:
            data = response.json()
            messages.error(request, response.text)
            return redirect('/depo_list')
        except:
            messages.error(request, response.text)
        return redirect('/depo_list')
    if request.method == "POST":
        id = request.POST.get("regionid1")
        if id:
            for i in regionlist:
                if i['region_id'] == id:
                    whid = i['warehouseid']
                    whname = i['warehousename']
                    regionname = i['regionname']
            url = "http://13.235.112.1/ziva/mobile-api/edit-depomaster.php"

            payload = json.dumps({

                "accesskey": accesskey,
                "depoid": request.POST.get('depoid'),
                "depocode": request.POST.get('depocode'),
                "deponame": request.POST.get('deponame1'),
                "gstnumber": request.POST.get('gstnumber1'),
                "address": request.POST.get('address1'),
                "licenseno": request.POST.get('license1'),
                "depo_manager":request.POST.get('depomanager1'),
                "depo_contact_no":request.POST.get('mobileno1'),
                "warehouseid":whid,
                "warehouse":whname,
                "regionid": request.POST.get('regionid1'),
                "region":request.POST.get('regionname1'),
            })
            headers = {
                'Content-Type': 'application/json'
            }

            response = requests.request("GET", url, headers=headers, data=payload)

            if response.status_code == 200:
                data = response.json()
                messages.success(request, data['message'])
                return redirect('depo_list')
            elif response.status_code == 400:
                data = response.json()
                text  = data['message']
                if 'some details are missing' in text:
                    messages.error(request, data['message'])
                    return redirect('depo_list')
                else:
                    messages.error(request, data['message'])
                    return redirect('/login')
            else:
                try:
                    r = response.json()
                    messages.error(request, r['message'])
                except:
                    messages.error(request, response.text)
                return redirect('depo_list')
        else:
            messages.error(request,' region id not exist')
            return redirect('depo_list')
    return redirect('depo_list')


def level_edit(request):
    pass


def pending_indent_ack(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    menuname = request.session['mylist']
    accesskey = request.session['accesskey']

    url = "http://13.235.112.1/ziva/mobile-api/warehouse-indent-list.php"

    payload = json.dumps({
        "accesskey": accesskey,
        "status": "Acknowledgement"
    })
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    if response.status_code == 200:
        data = response.json()
        data = data['indentlist']
        return render(request, 'create_indent/wh_indent_ack.html', {'data': data,'menuname':menuname})
    elif response.status_code == 400:
        data = response.json()
        messages.error(request, data['message'])
        return render(request, 'login1.html')
    else:
        return render(request, 'create_indent/wh_indent_ack.html',{'menuname':menuname})

def pending_indent_pending(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    menuname = request.session['mylist']
    accesskey = request.session['accesskey']
    if request.method == 'POST':
        url = "http://13.235.112.1/ziva/mobile-api/warehouse-indent-list.php"
        fdate = request.POST.get('fdate')
        tdate = request.POST.get('tdate')
        payload = json.dumps({
            "accesskey": accesskey,
            "status": "Pending",
            "fdate":fdate,
            "tdate":tdate
        })
        headers = {
            'Content-Type': 'application/json'
        }
        response = requests.request("GET", url, headers=headers, data=payload)
        if response.status_code == 200:
            data = response.json()
            data = data['indentlist']
            return render(request, 'create_indent/wh_indent_pending.html', {'status':'pending','data': data,'menuname':menuname,'fdate':fdate,'tdate':tdate})
        elif response.status_code == 400:
            data = response.json()
            if data['message'] == 'Sorry! some details are missing':
                messages.error(request, data['message'])
                return render(request, 'create_indent/wh_indent_pending.html', {'status':'pending','data': data,'menuname':menuname,'fdate':fdate,'tdate':tdate})
            else:
                data = response.json()
                messages.error(request, data['message'])
                return render(request, 'login1.html')
        else:
            return render(request, 'create_indent/wh_indent_pending.html',{'status':'pending','menuname':menuname,'fdate':fdate,'tdate':tdate,})
    else:
        url = "http://13.235.112.1/ziva/mobile-api/warehouse-indent-list.php"

        payload = json.dumps({
            "accesskey": accesskey,
            "status": "Pending",
            "fdate":"All",
            "tdate":"All"
        })
        headers = {
            'Content-Type': 'application/json'
        }

        response = requests.request("GET", url, headers=headers, data=payload)
        if response.status_code == 200:
            data = response.json()
            data = data['indentlist']
            return render(request, 'create_indent/wh_indent_pending.html', {'data': data,'status':'pending','menuname': menuname})
        elif response.status_code == 400:
            data = response.json()
            messages.error(request, data['message'])
            return render(request, 'login1.html')
        else:
            return render(request, 'create_indent/wh_indent_pending.html', {'menuname': menuname,'status':'pending'})


def pending_indent_pending1(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    menuname = request.session['mylist']
    accesskey = request.session['accesskey']
    role = request.session['role']
    if role == 'Admin':
        url = "http://13.235.112.1/ziva/mobile-api/warehousemaster-list.php"
        payload = json.dumps({"accesskey": accesskey})
        headers = {
            'Content-Type': 'text/plain'
        }
        response = requests.request("GET", url, headers=headers, data=payload)
        data = response.json()
        wh_masterlist = data['warehouselist']

        url = "http://13.235.112.1/ziva/mobile-api/depo-list.php"

        payload = json.dumps({"accesskey": accesskey})
        headers = {
            'Content-Type': 'text/plain'
        }
        response = requests.request("GET", url, headers=headers, data=payload)
        data = response.json()
        depolist = data['depolist']

        if request.method == 'POST':
            tdate = request.POST.get('fdate')
            ldate = request.POST.get('ldate')
            if tdate:
                tdate = tdate
            else:
                tdate = 'All'
            if ldate:
                ldate = ldate
            else:
                ldate = 'All'

            url = "http://13.235.112.1/ziva/mobile-api/indent-pendinglist-admin.php"
            payload = json.dumps({
                "depoid": request.POST.get('depoid1'),
                "tdate": ldate,
                "accesskey": accesskey,
                "warehouseid": request.POST.get('warehouseid1'),
                "status": "Approve",
                "fdate": tdate,
            })

            headers = {
                'Content-Type': 'application/json'
            }

            response = requests.request("GET", url, headers=headers, data=payload)
            if response.status_code == 200:
                data = response.json()
                list = data['indentlist']
                return render(request, 'create_indent/pending_indent_admin.html',
                              {"depolist": depolist, 'menuname': menuname, 'wh_masterlist': wh_masterlist,
                               'list': list})
            else:
                return render(request, 'create_indent/pending_indent_admin.html',
                              {'menuname': menuname, 'wh_masterlist': wh_masterlist, "depolist": depolist})
        else:
            url = "http://13.235.112.1/ziva/mobile-api/indent-pendinglist-admin.php"
            payload = json.dumps({
                "depoid": "All",
                "tdate": "All",
                "accesskey": accesskey,
                "warehouseid": "All",
                "status": "Approve ",
                "fdate": "All"
            })

            headers = {
                'Content-Type': 'application/json'
            }

            response = requests.request("GET", url, headers=headers, data=payload)
            if response.status_code == 200:
                data = response.json()
                list = data['indentlist']
                return render(request, 'create_indent/pending_indent_admin.html',
                              {'menuname': menuname, 'wh_masterlist': wh_masterlist, 'list': list, 'data1': list[0],
                               "depolist": depolist})
            else:
                return render(request, 'create_indent/pending_indent_admin.html',
                              {'menuname': menuname, 'wh_masterlist': wh_masterlist, "depolist": depolist})

    else:
            if request.method == 'POST':
                url = "http://13.235.112.1/ziva/mobile-api/warehouse-indent-list.php"
                fdate = request.POST.get('fdate')
                tdate = request.POST.get('tdate')
                payload = json.dumps({
                    "accesskey": accesskey,
                    "status": "Approve",
                    "fdate":fdate,
                    "tdate":tdate
                })
                headers = {
                    'Content-Type': 'application/json'
                }

                response = requests.request("GET", url, headers=headers, data=payload)
                if response.status_code == 200:
                    data = response.json()
                    data = data['indentlist']
                    return render(request, 'create_indent/wh_indent_pending.html', {'list': data,'data1':data[0],'menuname':menuname,'fdate':fdate,'tdate':tdate})
                elif response.status_code == 400:
                    data = response.json()
                    messages.error(request, data['message'])
                    return render(request, 'login1.html')
                else:
                    return render(request, 'create_indent/wh_indent_pending.html',{'menuname':menuname,'fdate':fdate,'tdate':tdate})
            else:
                url = "http://13.235.112.1/ziva/mobile-api/warehouse-indent-list.php"

                payload = json.dumps({
                    "accesskey": accesskey,
                    "status": "Approve",
                    "fdate":"All",
                    "tdate":"All"
                })
                headers = {
                    'Content-Type': 'application/json'
                }

                response = requests.request("GET", url, headers=headers, data=payload)
                if response.status_code == 200:
                    data = response.json()
                    data = data['indentlist']
                    return render(request, 'create_indent/wh_indent_pending.html', {'data': data, 'menuname': menuname})
                elif response.status_code == 400:
                    data = response.json()
                    messages.error(request, data['message'])
                    return render(request, 'login1.html')
                else:
                    return render(request, 'create_indent/wh_indent_pending.html', {'menuname': menuname})

def pending_ind_status(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    role = request.session['role']
    accesskey = request.session['accesskey']
    if role == 'Admin':
        url = "http://13.235.112.1/ziva/mobile-api/dc-generate-admin.php"
        payload = json.dumps({
            "accesskey": accesskey,
            "indentno": request.POST.get('txtHdnId'),
            "fromname": request.POST.get('from'),
            "fromid": request.POST.get('fromid'),
            "toid": request.POST.get('toid'),
            "toname": request.POST.get('to'),
            "remarks": request.POST.get('comment')
        })
        headers = {
            'Content-Type': 'application/json'
        }

        response = requests.request("GET", url, headers=headers, data=payload)
        if response.status_code == 200:
            data = response.json()
            messages.success(request, data['message'])
            return redirect('pending_indent_admin')
        elif response.status_code == 400:
            data = response.json()
            messages.error(request, data['message'])
            return render(request, 'login1.html')
        else:
            try:
                data = response.json()
                messages.error(request, data['message'])
                return redirect('pending_indent_admin')
            except:
                messages.error(request, response.text)
            return redirect('pending_indent_admin')
    else:
        url = "http://13.235.112.1/ziva/mobile-api/dc-generate-new.php"
        payload = json.dumps({
            "accesskey": accesskey,
            "indentno":request.POST.get('txtHdnId'),
            "fromname":request.POST.get('from'),
            "fromid":request.POST.get('fromid'),
            "toid":request.POST.get('toid'),
            "toname":request.POST.get('to'),
            "remarks":request.POST.get('comment')
        })
        headers = {
            'Content-Type': 'application/json'
        }

        response = requests.request("GET", url, headers=headers, data=payload)
        if response.status_code == 200:
            data = response.json()
            messages.success(request, data['message'])
            return redirect('pending_indent_pending')
        elif response.status_code == 400:
            data = response.json()
            messages.error(request, data['message'])
            return render(request, 'login1.html')
        else:
            try:
                data = response.json()
                messages.error(request, data['message'])
                return redirect('pending_indent_pending')
            except:
                messages.error(request, response.text)
            return redirect('pending_indent_pending')



def readyto_ship(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    try:
        menuname = request.session['mylist']
        accesskey = request.session['accesskey']
        url = "http://13.235.112.1/ziva/mobile-api/vehicle-dropdownlist.php"
        payload = json.dumps({

            "accesskey": accesskey
        })
        headers = {
            'Content-Type': 'application/json'
        }
        response = requests.request("GET", url, headers=headers, data=payload)
        data = response.json()
        vehicals = data['vehicleslist']
        if request.method == 'POST':
            fdate=request.POST.get('fdate')
            tdate = request.POST.get('tdate')
            url = "http://13.235.112.1/ziva/mobile-api/quantityupdated-list.php"

            payload = json.dumps({
                "accesskey":accesskey,
                "fdate":fdate,
                "tdate":tdate,
                "status":"Ready to Ship"

            })
            headers = {
                'Content-Type': 'application/json'
            }

            response = requests.request("GET", url, headers=headers, data=payload)
            if response.status_code == 200:
                data1 = response.json()
                data2 = data1['indentlist']
                #messages.success(request,data1['message'])
                return render(request, 'create_indent/readytoship.html', {'status':'Pending','data': data2,'vehicals':vehicals,'menuname':menuname,'fdate':fdate,'tdate':tdate})
            elif response.status_code == 400:
                data = response.json()
                messages.error(request, data['message'])
                return render(request, 'login1.html')
            else:
                return render(request, 'create_indent/readytoship.html', {'vehicals':vehicals,'status':'Pending','menuname':menuname,'fdate':fdate,'tdate':tdate})
        else:
            url = "http://13.235.112.1/ziva/mobile-api/quantityupdated-list.php"

            payload = json.dumps({
                "accesskey": accesskey,
                "status": "Ready to Ship",
                "fdate":"All",
                "tdate":"All"
            })
            headers = {
                'Content-Type': 'application/json'
            }

            response = requests.request("GET", url, headers=headers, data=payload)
            if response.status_code == 200:
                data1 = response.json()
                data2 = data1['indentlist']
                #messages.success(request, data1['message'])
                return render(request, 'create_indent/readytoship.html',
                              {'data': data2, 'vehicals': vehicals, 'menuname': menuname,'status':'Pending',})
            elif response.status_code == 400:
                data = response.json()
                messages.error(request, data['message'])
                return render(request, 'login1.html')
            else:
                return render(request, 'create_indent/readytoship.html', {'vehicals': vehicals, 'menuname': menuname,'status':'Pending',})
    except:
        messages.error(request,response.text)
    return render(request, 'create_indent/readytoship.html', {'menuname': menuname})
def readyto_ship1(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    try:
        menuname = request.session['mylist']
        accesskey = request.session['accesskey']
        url = "http://13.235.112.1/ziva/mobile-api/vehicle-dropdownlist.php"
        payload = json.dumps({

            "accesskey": accesskey
        })
        headers = {
            'Content-Type': 'application/json'
        }
        response = requests.request("GET", url, headers=headers, data=payload)
        data = response.json()
        vehicals = data['vehicleslist']
        if request.method == 'POST':
            fdate=request.POST.get('fdate')
            tdate = request.POST.get('tdate')
            url = "http://13.235.112.1/ziva/mobile-api/quantityupdated-list.php"

            payload = json.dumps({
                "accesskey":accesskey,
                "fdate":fdate,
                "tdate":tdate,
                "status":"Approve"

            })
            headers = {
                'Content-Type': 'application/json'
            }

            response = requests.request("GET", url, headers=headers, data=payload)
            if response.status_code == 200:
                data1 = response.json()
                data2 = data1['indentlist']
                messages.success(request,data1['message'])
                return render(request, 'create_indent/readytoship.html', {'status':'Approve','data': data2,'vehicals':vehicals,'menuname':menuname,'fdate':fdate,'tdate':tdate})
            else:
                return render(request, 'create_indent/readytoship.html', {'vehicals':vehicals,'status':'Approve','menuname':menuname,'fdate':fdate,'tdate':tdate})
        else:
            url = "http://13.235.112.1/ziva/mobile-api/quantityupdated-list.php"

            payload = json.dumps({
                "accesskey": accesskey,
                "status": "Approve",
                "fdate":"All",
                "tdate":"All"
            })
            headers = {
                'Content-Type': 'application/json'
            }

            response = requests.request("GET", url, headers=headers, data=payload)
            if response.status_code == 200:
                data1 = response.json()
                data2 = data1['indentlist']
                messages.success(request, data1['message'])
                return render(request, 'create_indent/readytoship.html',
                              {'data': data2,'status':'Approve', 'vehicals': vehicals, 'menuname': menuname})
            else:
                return render(request, 'create_indent/readytoship.html', {'vehicals': vehicals, 'status':'Approve','menuname': menuname})
    except:
        if response.status_code == 400:
            data = response.json()
            messages.error(request, data['message'])
            return render(request, 'login1.html')
    messages.error(request,response.text)
    return render(request, 'create_indent/readytoship.html', {'menuname': menuname})

def generate_gate_pass(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    accesskey = request.session['accesskey']
    role = request.session['role']
    if role == 'Admin':
        url = "http://13.235.112.1/ziva/mobile-api/outpass-generated.php"
        payload = json.dumps({

            "accesskey": accesskey,
            "dcnumber": request.POST.get('id'),
            "indentno":request.POST.get('indno'),
            "vehiclenumber": request.POST.get('vehicaldetails'),
            "drivername": request.POST.get('agentname'),
            "remarks": request.POST.get('remarks'),
            "fromname": request.POST.get('rname'),
            "fromid": request.POST.get('rid'),
            "toname": request.POST.get('wname'),
            "toid": request.POST.get('wid')})
        headers = {
            'Content-Type': 'application/json'
        }

        response = requests.request("GET", url, headers=headers, data=payload)
        if response.status_code == 200:
            data = response.json()
            messages.success(request, data['message'])
            return redirect('ready_toship_admin')
        elif response.status_code == 400:
            data = response.json()
            messages.error(request, data['message'])
            return render(request, 'login1.html')
        else:
            try:
                data = response.json()
                messages.success(request, data['message'])
                return redirect('ready_toship_admin')
            except:
                messages.success(request, data['message'])
            return redirect('ready_toship_admin')

    else:
        url="http://13.235.112.1/ziva/mobile-api/outpass-generated.php"
        payload = json.dumps({

            "accesskey":accesskey,
            "dcnumber": request.POST.get('id'),
            "vehiclenumber":request.POST.get('vehicaldetails'),
            "drivername":request.POST.get('agentname'),
            "remarks": request.POST.get('remarks'),
            "fromname": request.POST.get('rname'),
            "fromid": request.POST.get('rid'),
            "toname": request.POST.get('wname'),
            "toid": request.POST.get('wid') })
        headers = {
            'Content-Type': 'application/json'
        }

        response = requests.request("GET", url, headers=headers, data=payload)
        if response.status_code == 200:
            data = response.json()
            messages.success(request,data['message'])
            return redirect('readyto_ship')
        elif response.status_code == 400:
            data = response.json()
            messages.error(request, data['message'])
            return render(request, 'login1.html')
        else:
            try:
                data = response.json()
                messages.success(request, data['message'])
                return redirect('readyto_ship')
            except:
                messages.success(request, data['message'])
            return redirect('readyto_ship')

'''def partially_supplied(request):

    accesskey = request.session['accesskey']
    url = "http://13.235.112.1/ziva/mobile-api/quantityupdated-list.php"

    payload = json.dumps({
        "accesskey": accesskey,
        "status":"Partially Supplied",
    })
    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.request("GET", url, headers=headers, data=payload)
    if response.status_code == 200:
        data = response.json()
        data = data['indentlist']
        return render(request, 'create_indent/partiallysupplied.html', {'data': data})
    else:
        return render(request, 'create_indent/partiallysupplied.html')'''
def sales_list(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    try:
        menuname = request.session['mylist']
        if request.method  == 'POST':
            date = request.POST.get('date')
            accesskey = request.session['accesskey']
            url = "http://13.235.112.1/ziva/mobile-api/sales-list.php"

            payload = json.dumps({
                "accesskey": accesskey,
                "type": "Pending",
                "date":date
            })
            headers = {
                'Content-Type': 'application/json'
            }
            response = requests.request("GET", url, headers=headers, data=payload)
            if response.status_code == 200:
                data = response.json()
                data = data['saleslist']
                return render(request, 'sales/sales_list.html', {'data': data,"status":data[0],'date':date,'menuname':menuname})
            elif response.status_code == 400:
                    data = response.json()
                    messages.error(request,data['message'])
                    return render(request, 'login1.html')
            else:
                return render(request, 'sales/sales_list.html',{'date':date,'menuname':menuname})
        else:
            accesskey = request.session['accesskey']
            url = "http://13.235.112.1/ziva/mobile-api/sales-list.php"

            payload = json.dumps({
                "accesskey": accesskey,
                "type": "Pending",
                "date":"All"
            })
            headers = {
                'Content-Type': 'application/json'
            }
            response = requests.request("GET", url, headers=headers, data=payload)
            if response.status_code == 200:
                data = response.json()
                data = data['saleslist']
                return render(request, 'sales/sales_list.html', {"data": data,"status":"Approved", 'menuname': menuname})
            elif response.status_code == 400:
                    data = response.json()
                    messages.error(request,data['message'])
                    return render(request, 'login1.html')
            else:
                return render(request, 'sales/sales_list.html',{'menuname':menuname,"status":"Approved"})
    except:
        messages.error(request, response.text)
    return render(request, 'sales/sales_list.html', {'menuname': menuname,"status":"Approved"})

def sales_list_outpass(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    menuname = request.session['mylist']
    if request.method == 'POST':
        date = request.POST.get('date')
        accesskey = request.session['accesskey']
        url = "http://13.235.112.1/ziva/mobile-api/sales-list.php"

        payload = json.dumps({
            "accesskey": accesskey,
            "type": "Outpass",
            "date": date
        })
        headers = {
            'Content-Type': 'application/json'
        }
        response = requests.request("GET", url, headers=headers, data=payload)
        if response.status_code == 200:
            data = response.json()
            data = data['saleslist']
            return render(request, 'sales/sales_list.html', {'data': data, 'date': date,'menuname':menuname})
        elif response.status_code == 400:
            data = response.json()
            messages.error(request,data['message'])
            return render(request, 'login1.html')
        else:
            return render(request, 'sales/sales_list.html', {'date': date,'menuname':menuname})
    else:
        accesskey = request.session['accesskey']
        url = "http://13.235.112.1/ziva/mobile-api/sales-list.php"

        payload = json.dumps({
            "accesskey": accesskey,
            "type": "Outpass",
            "date": "All"
        })
        headers = {
            'Content-Type': 'application/json'
        }
        response = requests.request("GET", url, headers=headers, data=payload)
        if response.status_code == 200:
            data = response.json()
            data = data['saleslist']
            return render(request, 'sales/sales_list.html', {"data": data,'menuname':menuname})
        elif response.status_code == 400:
            data = response.json()
            messages.error(request,data['message'])
            return render(request, 'login1.html')
        else:
            return render(request, 'sales/sales_list.html',{'menuname':menuname})

def sales_admin_list(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    try:
        menuname = request.session['mylist']
        accesskey = request.session['accesskey']
        url = "http://13.235.112.1/ziva/mobile-api/warehousemaster-list.php"

        payload = json.dumps({"accesskey": accesskey})
        headers = {
            'Content-Type': 'text/plain'
        }
        response = requests.request("GET", url, headers=headers, data=payload)

        data = response.json()
        wh_masterlist = data['warehouselist']
        if request.method == 'POST':
            wh2 = request.POST.get('warehousename1')
            wh = request.POST.get('warehousename1')
            reg = request.POST.get('regionname1')
            depo = request.POST.get('deponame1')
            bus = request.POST.get('busstationname1')
            date = request.POST.get('date')
            accesskey = request.session['accesskey']
            url = "http://13.235.112.1/ziva/mobile-api/sales-list-admin.php"

            payload = json.dumps({
                "accesskey": accesskey,
                "warehouseid": request.POST.get('warehouseid1'),
                "depoid": request.POST.get('depoid1'),
                "regionid": request.POST.get('regionid1'),
                "busstationid": request.POST.get('busstationid1'),
                "type": "Pending",
                "date": date
            })
            headers = {
                'Content-Type': 'application/json'
            }
            response = requests.request("GET", url, headers=headers, data=payload)
            if response.status_code == 200:
                data = response.json()
                data = data['saleslist']
                return render(request, 'sales/sales_admin_list.html', {'data': data,'status':'Approved', 'date': date, 'menuname': menuname,'wh_masterlist':wh_masterlist})
            elif response.status_code == 400:
                    data = response.json()
                    messages.error(request, data['message'])
                    return redirect('login')
            else:
                try:
                    data = response.json()
                    messages.error(request,data['message'])
                except:
                    messages.error(request, response.text)
                return render(request, 'sales/sales_admin_list.html', {'date': date,'status':'Approved','menuname': menuname,'wh_masterlist':wh_masterlist})
        else:
            accesskey = request.session['accesskey']
            url = "http://13.235.112.1/ziva/mobile-api/sales-list-admin.php"

            payload = json.dumps({
                "accesskey": accesskey,
                "warehouseid": "All",
                "depoid": "All",
                "regionid": "All",
                "busstationid": "All",
                "type": "Pending",
                "date": "All"
            })
            headers = {
                'Content-Type': 'application/json'
            }
            response = requests.request("GET", url, headers=headers, data=payload)
            if response.status_code == 200:
                data = response.json()
                data = data['saleslist']
                return render(request, 'sales/sales_admin_list.html', {"data": data,'status':'Approved', 'menuname': menuname,'wh_masterlist':wh_masterlist})
            else:
                return render(request, 'sales/sales_admin_list.html', {'menuname': menuname,'status':'Approved','wh_masterlist':wh_masterlist})
    except:
        if response.status_code == 400:
            data = response.json()
            messages.error(request, data['message'])
            return render(request, 'login1.html')
    return render(request, 'sales/sales_admin_list.html')

def sales_admin_approvelist(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    try:
        menuname = request.session['mylist']
        accesskey = request.session['accesskey']
        url = "http://13.235.112.1/ziva/mobile-api/warehousemaster-list.php"

        payload = json.dumps({"accesskey": accesskey})
        headers = {
            'Content-Type': 'text/plain'
        }
        response = requests.request("GET", url, headers=headers, data=payload)

        data = response.json()
        wh_masterlist = data['warehouselist']
        if request.method == 'POST':
            date = request.POST.get('date')
            accesskey = request.session['accesskey']
            url = "http://13.235.112.1/ziva/mobile-api/sales-list-admin.php"

            payload = json.dumps({
                "accesskey": accesskey,
                "warehouseid": request.POST.get('warehouseid1'),
                "depoid": request.POST.get('depoid1'),
                "regionid": request.POST.get('regionid1'),
                "busstationid": request.POST.get('busstationname1'),
                "type": "Approved",
                "date": date
            })
            headers = {
                'Content-Type': 'application/json'
            }
            response = requests.request("GET", url, headers=headers, data=payload)
            if response.status_code == 200:
                data = response.json()
                data = data['saleslist']
                return render(request, 'sales/sales_admin_list.html',
                              {'data': data,'status':data[0], 'date': date, 'menuname': menuname, 'wh_masterlist': wh_masterlist})
            else:
                return render(request, 'sales/sales_admin_list.html',
                              {'date': date, 'menuname': menuname, 'wh_masterlist': wh_masterlist})
        else:
            accesskey = request.session['accesskey']
            url = "http://13.235.112.1/ziva/mobile-api/sales-list-admin.php"

            payload = json.dumps({
                "accesskey": accesskey,
                "type": "Approved",
                "warehouseid": "All",
                "regionid": "All",
                "depoid": "All",
                "busstationid": "All",
                "date": "All"
            })
            headers = {
                'Content-Type': 'application/json'
            }
            response = requests.request("GET", url, headers=headers, data=payload)
            if response.status_code == 200:
                data = response.json()
                data = data['saleslist']
                return render(request, 'sales/sales_admin_list.html',
                              {"data": data,'status':data[0], 'menuname': menuname, 'wh_masterlist': wh_masterlist})
            else:
                return render(request, 'sales/sales_admin_list.html',
                              {'menuname': menuname, 'wh_masterlist': wh_masterlist})
    except:
        if response.status_code == 400:
            data = response.json()
            messages.error(request, data['message'])
            return render(request, 'login1.html')
    return render(request,'sales/sales_admin_list.html')
def dc_pending(request):
        if 'accesskey' not in request.session:
            messages.error(request, 'Access denied!')
            return redirect('/login')

        url = "http://13.235.112.1/ziva/mobile-api/dc-pending.php"

        payload = json.dumps({
        "accesskey":"LTIwMjIxMjIwMDc2ODg1",
        "sonumber":request.POST.get('txtHdnId'),
        "paymentmode":request.POST.get('paymenttype'),
        "remarks":""
        })
        headers = {
        'Content-Type': 'application/json'
        }

        response = requests.request("GET", url, headers=headers, data=payload)

        data=response.json()
        print(payload)
        if response.status_code == 200:
            messages.success(request, data['message'])
            return redirect('sales')
        elif response.status_code == 400:
            data = response.json()
            messages.error(request, data['message'])
            return render(request, 'login1.html')
        else:
            messages.error(request, data['message'])
            return redirect('sale_item_list')

def taxinvoice_list(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    menuname = request.session['mylist']
    accesskey = request.session['accesskey']
    tdate = datetime.date.today()
    tdate = tdate.strftime("%Y-%m-%d")
    if request.method == 'POST':
        fdate = request.POST.get('fdate')
        tdate = request.POST.get('tdate')
        url = "http://13.235.112.1/ziva/mobile-api/tax-invoicelist.php"

        payload = json.dumps({
            "accesskey":accesskey,
            "fdate":request.POST.get('fdate'),
            "tdate":request.POST.get('tdate'),
            "status": "Approved"
        })
        headers = {
            'Content-Type': 'application/json'
        }

        response = requests.request("GET", url, headers=headers, data=payload)

        if response.status_code == 200:
            data = response.json()
            invlist = data['deliverypendinglist']
            return render(request,'sales/taxinvoicelist.html',{'list':invlist,'fdate':fdate,'tdate':tdate,'menuname':menuname})
        elif response.status_code == 400:
            data = response.json()
            messages.error(request,data['messsage'])
            return render(request,'login1.html')
        else:
            return render(request, 'sales/taxinvoicelist.html',{'fdate':fdate,'tdate':tdate,'menuname':menuname})
    else:
        url = "http://13.235.112.1/ziva/mobile-api/tax-invoicelist.php"
        payload = json.dumps({
            "accesskey": accesskey,
            "fdate":tdate,
            "tdate": tdate
        })
        headers = {
            'Content-Type': 'application/json'
        }

        response = requests.request("GET", url, headers=headers, data=payload)

        if response.status_code == 200:
            data = response.json()
            invlist = data['deliverypendinglist']
            return render(request, 'sales/taxinvoicelist.html', {'list': invlist, 'fdate': tdate, 'tdate': tdate,'menuname':menuname})
        elif response.status_code == 400:
            data = response.json()
            messages.error(request, data['message'])
            return render(request, 'login1.html')
        else:
            return render(request, 'sales/taxinvoicelist.html', {'fdate': tdate, 'tdate': tdate,'menuname':menuname})



def taxinvoice(request,id):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    menuname = request.session['mylist']
    accesskey = request.session['accesskey']
    url = "http://13.235.112.1/ziva/mobile-api/tax-invoice.php"

    payload = json.dumps({
        "accesskey": accesskey,
        "invoiceno": id,

    })
    headers = {
        'Content-Type': 'application/json'
    }

    response1 = requests.request("GET", url, headers=headers, data=payload)
    if response1.status_code == 200:
        data = response1.json()
        data1 = data['itemslist']
        return render(request, 'sales/invoice.html',{'data1':data1,'data':data,'menuname':menuname})
    elif response1.status_code == 400:
        data = response1.json()
        text = data['message']
        if text in 'some details are missing':
            messages.error(request, data['message'])
            return redirect('/taxinvoice_list')
        else:
            messages.error(request, data['message'])
            return render(request, 'login1.html')
    else:
        try:
            data = response1.json()
            messages.error(request,data['message'])
        except:
            messages.error(request,response1.text)
        return redirect('/taxinvoice_list')


def stock_transfer(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    try:
        menuname = request.session['mylist']
        accesskey = request.session['accesskey']
        displayrole = request.session['displayrole']

        code = request.session['codee']
        url = "http://13.235.112.1/ziva/mobile-api/quantitytypelist.php"
        payload = json.dumps({
            "accesskey": accesskey,
        })
        headers = {
            'Content-Type': 'application/json'
        }
        response = requests.request("GET", url, headers=headers, data=payload)

        if response.status_code == 200:
          data = response.json()
          type = data['qtyupdatedlist']

        url = "http://13.235.112.1/ziva/mobile-api/warehouseinventory-search-new.php"
        payload = json.dumps({
            "accesskey": accesskey,
            "id": code
        })
        headers = {
            'Content-Type': 'application/json'
        }
        response = requests.request("GET", url, headers=headers, data=payload)
        data = response.json()
        warehouseinventorylist = data['warehouseinventorylist']

        request.session['warehouseinventorylist'] =warehouseinventorylist

        url = "http://13.235.112.1/ziva/mobile-api/search-warehousemaster-new.php"
        payload = json.dumps({
            "accesskey": accesskey,
            "type": "Depo"
        })
        headers = {
            'Content-Type': 'application/json'
        }
        response = requests.request("GET", url, headers=headers, data=payload)
        data = response.json()
        depolist = data['warehouselist']
        request.session['depolist'] = depolist

        url = "http://13.235.112.1/ziva/mobile-api/search-warehousemaster-new.php"
        payload = json.dumps({
            "accesskey": accesskey,
            "type": "Warehouse"

        })
        headers = {
            'Content-Type': 'application/json'
        }
        response = requests.request("GET", url, headers=headers, data=payload)
        data = response.json()
        warehouselist = data['warehouselist']
        request.session['warehouselist']=warehouselist

        url = "http://13.235.112.1/ziva/mobile-api/search-warehousemaster-new.php"
        payload = json.dumps({
            "accesskey": accesskey,
            "type": "Bus station"

        })
        headers = {
            'Content-Type': 'application/json'
        }
        response = requests.request("GET", url, headers=headers, data=payload)
        data = response.json()
        buslist = data['warehouselist']
        request.session['buslist'] = buslist



        request.session['type'] = type

        url = "http://13.235.112.1/ziva/mobile-api/stock-translist.php"

        payload = json.dumps({
            "accesskey": accesskey,

        })
        headers = {

            'Content-Type': 'application/json'

        }
        response = requests.request("GET", url, headers=headers, data=payload)
        if response.status_code == 200:
            data = response.json()
            stocktransferlistto = data['stocktransferlistto']
            request.session['stocktransferlistto'] = stocktransferlistto
            return render(request, 'stock_transfer/stock_transfer_home.html',{'type':type,'data':stocktransferlistto,'depolist':depolist,'buslist':buslist,'warehouselist':warehouselist[0],'menuname':menuname,'warehouseinventorylist':warehouseinventorylist})
        else:
            return render(request, 'stock_transfer/stock_transfer_home.html',{'type':type,'warehouselist':warehouselist[0],'depolist':depolist,'buslist':buslist,'menuname':menuname,'displayrole':displayrole,'warehouseinventorylist':warehouseinventorylist})
    except:
        if response.status_code == 400:
            data = response.json()
            messages.error(request, data['message'])
            return render(request, 'login1.html')
    messages.error(request,response.text)
    return render(request, 'login1.html')


def get_store_data(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    accesskey = request.session['accesskey']
    serchterm = request.POST.get('searchterm')
    stid = request.POST.get('storeid')

    url = "http://13.235.112.1/ziva/mobile-api/inventory-search.php"

    payload = json.dumps({
        "accesskey": accesskey,
        "serchterm":serchterm,
        "storeid":stid

    })
    headers = {

        'Content-Type': 'application/json'

    }
    response = requests.request("GET", url, headers=headers, data=payload)
    if response.status_code == 400:
        data = response.json()
        messages.error(request,data['message'])
        return render(request,'login1.html')
    if response.status_code == 200:
        data = response.json()
        return JsonResponse({'data': data})


def store_search(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    accesskey = request.session['accesskey']
    serchterm = request.POST.get('store')
    url = "http://13.235.112.1/ziva/mobile-api/store-master-search.php"

    payload = json.dumps({
            "accesskey":accesskey,
            "storename":serchterm,
             "depoid":request.POST.get('depo')
    })
    headers = {
        'Content-Type': 'text/plain'
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    if response.status_code == 200:
        data = response.json()
        return JsonResponse({'data': data})
    elif response.status_code == 400:
        data = response.json()
        messages.error(request, data['message'])
        return render(request, 'login1.html')

def get_wh_item(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    role = request.session['role']
    depoid = request.session['depoid']
    accesskey = request.session['accesskey']
    serchterm = request.POST.get('searchterm')
    pattern = r"\d+[mM][lL]"
    match = re.search(pattern, serchterm, re.IGNORECASE)
    if role == 'Admin':
        itemcode = request.POST.get('itemcode')
        wh_code = request.session['wh_code']
        url = "http://13.235.112.1/ziva/mobile-api/warehouseinventory-search-new-admin.php"
        payload = json.dumps({
            "accesskey": accesskey,
            "id": wh_code,
            "type": "Warehouse"
        })
        headers = {
            'Content-Type': 'application/json'
        }
        response = requests.request("GET", url, headers=headers, data=payload)
        if response.status_code == 200:
            data = response.json()
            list = data['warehouseinventorylist']
            for i in list:
                if str(i['itemcode']) == itemcode:
                    data = {"whmrp": i["mrp"], "whuom": i["uom"], "whitemname": i["itemname"], "whcp_sno": i['cp_sno'],"whexpirydate":i['expirydate']}
            return JsonResponse({'data': data})
        elif response.status_code == 400:
            data = response.json()
            if data['message'] == 'Sorry! some details are missing':
                messages.error(request, data['message'])
                return redirect('/generate_transid')
            else:
                messages.error(request, data['message'])
                return redirect('/login')
    else:

        if match:
            extracted_text = match.group()
            print(extracted_text)

            url = "http://13.235.112.1/ziva/mobile-api/warehouseinventory-searchlist.php"

            payload = json.dumps({
                "accesskey": accesskey,
                "searchterm": extracted_text,
                "id": depoid,
            })
            headers = {
                'Content-Type': 'application/json'

            }
        response = requests.request("GET", url, headers=headers, data=payload)
        if response.status_code == 200:
            data=response.json()
            return JsonResponse({'data': data})
        elif response.status_code == 400:
            data = response.json()
            messages.error(request, data['message'])
            return render(request, 'login1.html')

def get_user(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    userid = request.POST.get('id')
    accesskey = request.session['accesskey']
    url = "http://13.235.112.1/ziva/mobile-api/user-list.php"

    payload = json.dumps({
        "accesskey": accesskey
    })
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    if response.status_code == 200:
        data = response.json()
        list = data['userlist']
        for i in list:
            if str(i['userid']) == userid:
                data1 = {"userid": i["userid"], "username": i["username"], "mobile": i["mobile"], "emailid": i['emailid'],
                        "region": i['region'], "regionid": i['regionid'], "warehouseid": i['warehouseid'], "warehousename": i['warehousename'], "depoid": i['depoid'],
                        "deponame": i['deponame'], "busstationid": i['busstationid'], "busstationname": i['busstationname'], "role": i['role'], "level": i['level'],"role2": i['role2'],
                        }
        return JsonResponse({'data': data1})
    elif response.status_code == 400:
        data = response.json()
        if data['message'] == 'Sorry! some details are missing':
            messages.error(request, data['message'])
            return redirect('/user_list')
        else:
            messages.error(request, data['message'])
            return redirect('/login')

def get_ps(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    accesskey = request.session['accesskey']
    url = "http://13.235.112.1/ziva/mobile-api/product-superviserlist.php"
    payload = json.dumps({
        "accesskey": accesskey,"depoid":request.POST.get('depo')
    })
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    if response.status_code == 200:
        data = response.json()
        return JsonResponse({'data': data})
    elif response.status_code == 400:
        data = response.json()
        if data['message'] == 'Sorry! some details are missing':
            return JsonResponse({'data': data})
        else:
            messages.error(request, data['message'])
            return redirect('/login')
    elif response.status_code == 503:
        data = response.json()
        return JsonResponse({'data': data})
    else:
        return redirect('/internal_consumption')


def wh_search(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    accesskey = request.session['accesskey']
    url = "http://13.235.112.1/ziva/mobile-api/search-warehousemaster.php"

    payload = json.dumps({"accesskey": accesskey,
                          "searchterm": request.POST.get('searchterm'),
                          "type": "Warehouse"
                          })
    headers = {
        'Content-Type': 'text/plain'
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    if response.status_code == 200:
        data = response.json()
        return JsonResponse({'data':data})
    if response.status_code == 400:
        data = response.json()
        messages.error(request, data['message'])
        return render(request, 'login1.html')


def wh_add_stf(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    accesskey = request.session['accesskey']
    code = request.session['codee']
    menuname = request.session['mylist']
    stocktransferlistto = request.session['stocktransferlistto']
    warehouselist =request.session['warehouselist']
    buslist = request.session['buslist']
    type= request.session['type']

    if  request.method == 'POST':

        url = "http://13.235.112.1/ziva/mobile-api/generate-transitid.php"

        payload = json.dumps({
            "accesskey": accesskey,
            "id": request.POST.get('warehouseid'),
            "name": request.POST.get('warehousename'),
            "type": "Warehouse"

        })
        headers = {
            'Content-Type': 'application/json'
        }

        response = requests.request("GET", url, headers=headers, data=payload)
        if response.status_code == 200:
            data = response.json()
            request.session['taxinvoice'] = data['taxinvoice']

            url = "http://13.235.112.1/ziva/mobile-api/warehouseinventory-search-new.php"

            payload = json.dumps({
                "accesskey": accesskey,
                "id": code
            })
            headers = {
                'Content-Type': 'application/json'
            }

            response = requests.request("GET", url, headers=headers, data=payload)

            data = response.json()
            warehouseinventorylist = data['warehouseinventorylist']
            messages.success(request, data['message'])
            return render(request,'stock_transfer/stock_transfer_home.html',{'buslist':buslist,'type':type,'warehouselist':warehouselist[0],'warehouseinventorylist':warehouseinventorylist,'menuname':menuname,'wh':'active','data':stocktransferlistto})
        elif response.status_code == 400:
            data = response.json()
            messages.error(request, data['message'])
            return render(request, 'login1.html')
        else:
            try:
                data = response.json()
                messages.error(request, data['message'])
            except:
                messages.error(request,response.text)
            return redirect('stock_transfer')
    else:
        return redirect('stock_transfer')


def wh_item_add(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    accesskey = request.session['accesskey']

    depoid = request.session['depoid']
    buslist = request.session['buslist']
    taxinvoice = request.session['taxinvoice']
    if request.method == 'POST':
                url = "http://13.235.112.1/ziva/mobile-api/add-stockitem-warehouse.php"

                payload = json.dumps({
                    "accesskey":accesskey,
                    "noofbottles":request.POST.get('nob'),
                    "type":request.POST.get('typeid') ,
                    "cp_sno": request.POST.get('cpsno'),
                    "quantity": request.POST.get('quantity'),
                    "freeqty":" ",
                    "id": depoid,
                    "transitid": taxinvoice
                })
                headers = {
                    'Content-Type': 'application/json'
                }

                response = requests.request("GET", url, headers=headers, data=payload)
                if response.status_code == 200:
                    data = response.json()
                    messages.success(request, data['message'])
                    return redirect('wh_item_list')
                elif response.status_code == 400:
                    data = response.json()
                    messages.error(request, data['message'])
                    return render(request, 'login1.html')
                else:
                    try:
                        data = response.json()
                        messages.error(request, data['message'])
                        return redirect('wh_item_list')
                    except:
                        messages.error(request,response.text)
                    return redirect('stock_transfer')

    else:
                return redirect('stock_transfer')



def wh_item_list(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    warehouselist = request.session['warehouselist']
    buslist = request.session['buslist']
    stocktransferlistto = request.session['stocktransferlistto']
    menuname = request.session['mylist']
    type = request.session['type']
    accesskey = request.session['accesskey']
    taxinvoice  = request.session['taxinvoice']

    code = request.session['codee']
    url = "http://13.235.112.1/ziva/mobile-api/warehouseinventory-search-new.php"

    payload = json.dumps({
        "accesskey": accesskey,
        "id": code
    })
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("GET", url, headers=headers, data=payload)

    data = response.json()
    warehouseinventorylist = data['warehouseinventorylist']

    url = "http://13.235.112.1/ziva/mobile-api/stocktransfer-item-list.php"

    payload = json.dumps({"accesskey":accesskey,
        "transitid":taxinvoice
        })
    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.request("GET", url, headers=headers, data=payload)
    if response.status_code == 200:
        data=response.json()
        wh_item_list=data['stocktransferitemlist']
        return render(request,'stock_transfer/stock_transfer_home.html',{'type':type,'taxinvoice':taxinvoice,'warehouseinventorylist':warehouseinventorylist,'warehouselist':warehouselist[0],'wh_item_list':wh_item_list,'menuname':menuname,'data':stocktransferlistto,'wh':'active','status':'ok','buslist':buslist,'response':'wh200'})
    elif response.status_code == 400:
        data = response.json()
        messages.error(request, data['message'])
        return render(request, 'login1.html')
    else:
        return render(request, 'stock_transfer/stock_transfer_home.html',
                      {'response':'wh200','type':type,'warehouseinventorylist' : warehouseinventorylist, 'menuname': menuname,'data':stocktransferlistto,'taxinvoice':taxinvoice,'wh':'active','warehouselist':warehouselist[0],'buslist':buslist})

def delete_stk_item(request,id):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')

    accesskey = request.session['accesskey']
    role = request.session['role']
    url = "http://13.235.112.1/ziva/mobile-api/delete-stocktransferwarehouse-item.php"
    if role == 'Admin':
        whtaxinvoice = request.session['whtaxinvoice']
        payload = json.dumps({
                "accesskey": accesskey,
                "transitid": whtaxinvoice,
                "sno":id
            })
    else:
        taxinvoice = request.session['taxinvoice']
        payload = json.dumps({
            "accesskey": accesskey,
            "transitid": taxinvoice,
            "sno": id
        })
    headers = {
            'Content-Type': 'application/json'
        }

    response = requests.request("GET", url, headers=headers, data=payload)
    if response.status_code == 200:
            data = response.json()
            messages.success(request, data['message'])
            if role == 'Admin':
                return redirect('/wh_item_list_admin')
            else:
                return redirect('/wh_item_list')
    elif response.status_code == 400:
        data = response.json()
        messages.error(request, data['message'])
        return render(request, 'login1.html')
    else:
        try:
                data = response.json()
                messages.error(request, data['message'])
                if role == 'Admin':
                    return redirect('/wh_item_list_admin')
                else:
                    return redirect('/wh_item_list')
        except:
                messages.error(request, response.text)
        return redirect('/stock_tranfer_admin')

def delete_stkbus_item(request,id):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')

    accesskey = request.session['accesskey']
    role = request.session['role']

    if role == 'Admin':
        url = "http://13.235.112.1/ziva/mobile-api/delete-stocktransferwarehouse-item.php"
        bustaxinvoice = request.session['bustaxinvoice']
        payload = json.dumps({
            "accesskey": accesskey,
            "transitid": bustaxinvoice,
            "sno": id
        })
        headers = {
            'Content-Type': 'application/json'
        }

        response = requests.request("GET", url, headers=headers, data=payload)
        if response.status_code == 200:
            data = response.json()
            messages.success(request, data['message'])
            return redirect('bus_item_list_admin')
        elif response.status_code == 400:
            data = response.json()
            messages.error(request, data['message'])
            return render(request, 'login1.html')
        else:
            try:
                data = response.json()
                messages.error(request, data['message'])
                return redirect('bus_item_list_admin')
            except:
                messages.error(request, response.text)
            return redirect('stock_tranfer_admin')

    else:
        url = "http://13.235.112.1/ziva/mobile-api/delete-stocktransferwarehouse-item.php"
        taxinvoice = request.session['taxinvoice']
        payload = json.dumps({
                "accesskey": accesskey,
                "transitid": taxinvoice,
                "sno":id
            })
        headers = {
            'Content-Type': 'application/json'
        }

        response = requests.request("GET", url, headers=headers, data=payload)
        if response.status_code == 200:
            data = response.json()
            messages.success(request, data['message'])
            return redirect('busstation_item_list')
        elif response.status_code == 400:
            data = response.json()
            messages.error(request, data['message'])
            return render(request, 'login1.html')
        else:
            try:
                data = response.json()
                messages.error(request, data['message'])
                return redirect('busstation_item_list')
            except:
                messages.error(request, response.text)
            return redirect('stock_transfer')


def delete_stkdepo_item(request,id):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')

    accesskey = request.session['accesskey']
    role = request.session['role']
    if role == 'Admin':
        url = "http://13.235.112.1/ziva/mobile-api/delete-stocktransferwarehouse-item.php"
        depot_taxinvoice = request.session['depot_taxinvoice']
        payload = json.dumps({
            "accesskey": accesskey,
            "transitid": depot_taxinvoice,
            "sno": id
        })
        headers = {
            'Content-Type': 'application/json'
        }

        response = requests.request("GET", url, headers=headers, data=payload)
        if response.status_code == 200:
            data = response.json()
            messages.success(request, data['message'])
            return redirect('depot_item_list_admin')
        elif response.status_code == 400:
            data = response.json()
            if data['message'] == 'Sorry! some details are missing':
                messages.error(request, data['message'])
                return redirect('depot_item_list_admin')
            else:
                messages.error(request, data['message'])
                return redirect('/login')
        else:
            try:
                data = response.json()
                messages.error(request, data['message'])
                return redirect('depot_item_list_admin')
            except:
                messages.error(request, response.text)
            return redirect('stock_tranfer_admin')

    else:
            taxinvoice = request.session['taxinvoice']
            url = "http://13.235.112.1/ziva/mobile-api/delete-stocktransferwarehouse-item.php"

            payload = json.dumps({
                    "accesskey": accesskey,
                    "transitid": taxinvoice,
                    "sno":id
                })
            headers = {
                    'Content-Type': 'application/json'
                }

            response = requests.request("GET", url, headers=headers, data=payload)
            if response.status_code == 200:
                    data = response.json()
                    messages.success(request, data['message'])
                    return redirect('depo_item_list')
            elif response.status_code == 400:
                data = response.json()
                messages.error(request, data['message'])
                return render(request, 'login1.html')
            else:
                try:
                        data = response.json()
                        messages.error(request, data['message'])
                        return redirect('depo_item_list')
                except:
                        messages.error(request, response.text)
                return redirect('stock_transfer')



def edit_stk_item(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')

    accesskey = request.session['accesskey']
    role = request.session['role']
    displayrole = request.session['displayrole']
    if role == 'Admin':
        whtaxinvoice = request.session['whtaxinvoice']
        url = "http://13.235.112.1/ziva/mobile-api/edit-stocktransfer-item.php"

        payload = json.dumps({
            "accesskey": accesskey,
            "noofbottles": request.POST.get('nob1'),
            "sno": request.POST.get('editsno'),
            "quantity": request.POST.get('qty'),
            "type": " Warehouse",
            "transitid": whtaxinvoice
        })
        headers = {
            'Content-Type': 'application/json'
        }
        response = requests.request("GET", url, headers=headers, data=payload)
        if response.status_code == 200:
            data = response.json()
            messages.success(request, data['message'])
            return redirect('wh_item_list_admin')
        elif response.status_code == 400:
            data = response.json()
            messages.error(request, data['message'])
            return render(request, 'login1.html')
        else:
            try:
                data = response.json()
                messages.error(request, data['message'])
                return redirect('wh_item_list_admin')
            except:
                messages.error(request, response.text)
            return redirect('wh_item_list_admin')
    else:
        if request.method == 'POST':
            taxinvoice = request.session['taxinvoice']
            url = "http://13.235.112.1/ziva/mobile-api/edit-stocktransfer-item.php"

            payload = json.dumps({
                "accesskey": accesskey,
                "noofbottles":request.POST.get('nob1'),
                "sno": request.POST.get('sno'),
                "quantity":request.POST.get('qty'),
                "type": " Warehouse",
                "transitid": taxinvoice
            })
            headers = {
                'Content-Type': 'application/json'
            }

            response = requests.request("GET", url, headers=headers, data=payload)
            if response.status_code == 200:
                data = response.json()
                messages.success(request, data['message'])
                return redirect('wh_item_list')
            elif response.status_code == 400:
                data = response.json()
                messages.error(request, data['message'])
                return render(request, 'login1.html')
            else:
                try:
                    data = response.json()
                    messages.error(request, data['message'])
                    return redirect('wh_item_list')
                except:
                    messages.error(request, response.text)
                return redirect('wh_item_list')
        else:
            return redirect('stock_transfer')


def complete_busstk_admin(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')

    accesskey = request.session['accesskey']
    bustaxinvoice = request.session['bustaxinvoice']
    url = "http://13.235.112.1/ziva/mobile-api/complete-stock.php"

    payload = json.dumps({
        "accesskey": accesskey,
        "transid": bustaxinvoice,
        "remarks": request.POST.get('remarks'),
        "date": request.POST.get('date'),

    })
    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.request("GET", url, headers=headers, data=payload)
    if response.status_code == 200:
        data = response.json()
        messages.success(request, data['message'])
        return redirect('stock_tranfer_admin')
    elif response.status_code == 400:
        data = response.json()
        messages.error(request, data['message'])
        return render(request, 'login1.html')
    else:
        try:
            data = response.json()
            messages.error(request, data['message'])
            return redirect('stock_tranfer_admin')
        except Exception as e:
            messages.error(request, str(e))
        return redirect('stock_tranfer_admin')




def complete_stk_admin(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    menuname = request.session['mylist']
    accesskey = request.session['accesskey']
    whtaxinvoice = request.session['whtaxinvoice']
    url = "http://13.235.112.1/ziva/mobile-api/complete-stock.php"

    payload = json.dumps({
        "accesskey": accesskey,
        "transid": whtaxinvoice,
        "remarks": request.POST.get('remarks'),
        "date": request.POST.get('date'),

    })
    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.request("GET", url, headers=headers, data=payload)
    if response.status_code == 200:
        data = response.json()
        messages.success(request, data['message'])
        return redirect('stock_tranfer_admin')
    elif response.status_code == 400:
        data = response.json()
        messages.error(request, data['message'])
        return render(request, 'login1.html')
    else:
        try:
            data = response.json()
            messages.error(request, data['message'])
            return redirect('stock_tranfer_admin')
        except Exception as e:
            messages.error(request, str(e))
        return redirect('stock_tranfer_admin')


def complete_whinv(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    menuname = request.session['mylist']
    accesskey = request.session['accesskey']
    taxinvoice = request.session['taxinvoice']
    stocktransferlistto = request.session['stocktransferlistto']

    if  request.method == 'POST':
        url = "http://13.235.112.1/ziva/mobile-api/complete-stock.php"

        payload = json.dumps({
            "accesskey": accesskey,
            "transid": taxinvoice,
            "remarks": request.POST.get('remarks'),
            "date": request.POST.get('date'),

        })
        headers = {
            'Content-Type': 'application/json'
        }
        response = requests.request("GET", url, headers=headers, data=payload)
        if response.status_code == 200:
            data = response.json()
            messages.success(request, data['message'])
            return redirect('stock_transfer')
        elif response.status_code == 400:
            data = response.json()
            messages.error(request, data['message'])
            return render(request, 'login1.html')
        else:
            try:
                data = response.json()
                messages.error(request, data['message'])
                return redirect('stock_transfer')
            except:
                messages.error(request,response.text)
            return redirect('stock_transfer')
    else:
        return render(request,'stock_transfer/stock_transfer_home.html',{'wh_item_list':wh_item_list,'menuname':menuname,'data':stocktransferlistto})

def depo_search(request):
        if 'accesskey' not in request.session:
            messages.error(request, 'Access denied!')
            return redirect('/login')
        accesskey = request.session['accesskey']
        url = "http://13.235.112.1/ziva/mobile-api/search-warehousemaster.php"

        payload = json.dumps({"accesskey": accesskey,
                              "searchterm": request.POST.get('searchterm'),
                              "type": "Depo"
                              })
        headers = {
            'Content-Type': 'text/plain'
        }

        response = requests.request("GET", url, headers=headers, data=payload)
        if response.status_code == 200:
            data = response.json()
            return JsonResponse({'data': data})
        elif response.status_code == 400:
            data = response.json()
            messages.error(request, data['message'])
            return render(request, 'login1.html')
        else:
            return render(request, 'depo_list.html')


def get_depo_item(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    code = request.session['codee']
    accesskey = request.session['accesskey']
    serchterm = request.POST.get('searchterm')
    pattern = r"\d+[mM][lL]"
    match = re.search(pattern, serchterm, re.IGNORECASE)
    role=request.session['role']
    if role == 'Admin':
        depoitemcode = request.POST.get('depoitemcode')
        fromid =  request.session['fromid']
        url = "http://13.235.112.1/ziva/mobile-api/warehouseinventory-search-new-admin.php"
        payload = json.dumps({
            "accesskey": accesskey,
            "id": fromid,
            "type": "Depo"
        })
        headers = {
            'Content-Type': 'application/json'
        }
        response = requests.request("GET", url, headers=headers, data=payload)
        if response.status_code == 200:
            data = response.json()
            list = data['warehouseinventorylist']
            for i in list:
                if str(i['itemcode']) == depoitemcode:
                    data = {"depot_mrp": i["mrp"], "depot_uom": i["uom"], "depot_name": i["itemname"],
                            "depot_sno": i['cp_sno'],
                            "depotexpdate": i['expirydate']}
            return JsonResponse({'data': data})
        elif response.status_code == 400:
            data = response.json()
            if data['message'] == 'Sorry! some details are missing':
                messages.error(request, data['message'])
                return redirect('/generate_transid')
            else:
                messages.error(request, data['message'])
                return redirect('/login')
    else:
        if match:
            extracted_text = match.group()
            print(extracted_text)

        url = "http://13.235.112.1/ziva/mobile-api/warehouseinventory-searchlist.php"

        payload = json.dumps({
            "accesskey": accesskey,
            "searchterm":extracted_text,
            "id": code,
        })
        headers = {
            'Content-Type': 'application/json'

        }
        response = requests.request("GET", url, headers=headers, data=payload)
        if response.status_code == 200:
            data=response.json()
            return JsonResponse({'data': data})
        elif response.status_code == 400:
            data = response.json()
            messages.error(request, data['message'])
            return render(request, 'login1.html')
def depo_add_stf(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    code = request.session['codee']
    menuname = request.session['mylist']
    accesskey = request.session['accesskey']
    stocktransferlistto = request.session['stocktransferlistto']
    depo_list = request.session['warehouselist']
    type = request.session['type']
    if request.method  == 'POST':
        deponame = request.POST.get('txtdeposearch')
        request.session['deponame'] = deponame
        txtDepoId = request.POST.get('txtDepoId')
        request.session['txtDepoId'] = txtDepoId
        url = "http://13.235.112.1/ziva/mobile-api/generate-transitid.php"

        payload = json.dumps({
            "accesskey": accesskey,
            "id":txtDepoId,
            "name":deponame,
            "type": "Depo"
        })
        headers = {
            'Content-Type': 'application/json'
        }
        response = requests.request("GET", url, headers=headers, data=payload)
        if response.status_code == 200:
            data1 = response.json()
            taxinvoice =  data1['taxinvoice']
            request.session['taxinvoice'] =taxinvoice

            url = "http://13.235.112.1/ziva/mobile-api/warehouseinventory-search-new.php"

            payload = json.dumps({
                "accesskey": accesskey,
                "id": code
            })
            headers = {
                'Content-Type': 'application/json'
            }

            response = requests.request("GET", url, headers=headers, data=payload)

            data = response.json()
            depoinventorylist = data['warehouseinventorylist']
            request.session['warehouseinventorylist'] = depoinventorylist
            messages.success(request,data1['message'])
            return redirect('depo_item_add')
        elif response.status_code == 400:
            data = response.json()
            messages.error(request, data['message'])
            return render(request, 'login1.html')
        else:
            try:
                data = response.json()
                messages.error(request, data['message'])
            except:
                messages.error(request,response.text)
            return redirect('depo_item_list')
    else:
        return render(request,'stock_transfer/stock_transfer_home.html',{'type':type,'data':stocktransferlistto,'depo':'active','menuname':menuname})

def depo_item_add(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    depolist = request.session['depolist']
    depoinventorylist = request.session['warehouseinventorylist']
    menuname = request.session['mylist']
    code = request.session['codee']
    taxinvoice  = request.session['taxinvoice']
    accesskey = request.session['accesskey']
    stocktransferlistto = request.session['stocktransferlistto']
    txtDepoId = request.session['txtDepoId']
    type = request.session['type']
    if request.method == 'POST':
        url = "http://13.235.112.1/ziva/mobile-api/add-stockitem-warehouse.php"

        payload = json.dumps({
            "accesskey":accesskey,
            "cp_sno": request.POST.get('depocpsno'),
            "quantity": request.POST.get('quantity'),
            "noofbottles": request.POST.get('deponob'),
            "freeqty": "",
            "id":code,
            "transitid": taxinvoice
        })
        headers = {
            'Content-Type': 'application/json'
        }

        response = requests.request("GET", url, headers=headers, data=payload)
        if response.status_code == 200:
            data = response.json()
            messages.success(request, data['message'])
            return redirect('depo_item_list')
        elif response.status_code == 400:
            data = response.json()
            if data['message'] == 'Sorry! some details are missing':
                messages.error(request, data['message'])
                return redirect('/depo_item_add')
            else:
                messages.error(request, data['message'])
                return redirect('/login')
        else:
            try:
                data = response.json()
                messages.error(request, data['message'])
                return redirect('depo_item_list')
            except:
                messages.error(request,response.text)
            return render(request,'stock_transfer/stock_transfer_home.html',{'type':type,'depolist':depolist,'taxinvoice':taxinvoice,'items':depoinventorylist,'data':stocktransferlistto,'depo':'active','menuname':menuname,'txtDepoId':txtDepoId})

    else:
        return render(request,'stock_transfer/stock_transfer_home.html',{'type':type,'depolist':depolist,'taxinvoice':taxinvoice,'items':depoinventorylist,'data':stocktransferlistto,'depo':'active','menuname':menuname,'txtDepoId':txtDepoId,'response':'depo200'})

def depo_item_list(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    txtDepoId = request.session['txtDepoId']
    depo_list = request.session['depolist']
    type = request.session['type']
    stocktransferlistto = request.session['stocktransferlistto']
    menuname = request.session['mylist']
    accesskey = request.session['accesskey']
    taxinvoice  = request.session['taxinvoice']
    depoinventorylist =  request.session['warehouseinventorylist']
    url = "http://13.235.112.1/ziva/mobile-api/stocktransfer-item-list.php"

    payload = json.dumps({"accesskey":accesskey,
        "transitid":taxinvoice
        })
    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.request("GET", url, headers=headers, data=payload)
    if response.status_code == 200:
        data=response.json()
        depo_item_list=data['stocktransferitemlist']
        return render(request,'stock_transfer/stock_transfer_home.html',{'response':'depo200','type':type,'txtDepoId':txtDepoId,'depolist':depo_list,'items':depoinventorylist,'taxinvoice':taxinvoice,'data':stocktransferlistto,'depo':'active','depo_item_list':depo_item_list,'menuname':menuname,'status':'ok'})
    elif response.status_code == 400:
        data = response.json()
        messages.error(request, data['message'])
        return render(request, 'login1.html')
    else:
        return render(request, 'stock_transfer/stock_transfer_home.html',
                      {'txtDepoId': txtDepoId, 'depolist': depo_list, 'items': depoinventorylist,
                       'taxinvoice': taxinvoice, 'data': stocktransferlistto, 'depo': 'active',
                        'menuname': menuname,'type':type,'response':'depo200'})


def complete_depoinv(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    stocktransferlistto = request.session['stocktransferlistto']
    menuname = request.session['mylist']
    deponame = request.session['name']
    accesskey = request.session['accesskey']
    taxinvoice = request.session['taxinvoice']
    if  request.method == 'POST':
        url = "http://13.235.112.1/ziva/mobile-api/complete-stock.php"

        payload = json.dumps({
            "accesskey": accesskey,
            "transid": taxinvoice,
            "remarks": request.POST.get('remarks'),
            "date": request.POST.get('date'),

        })
        headers = {
            'Content-Type': 'application/json'
        }
        response = requests.request("GET", url, headers=headers, data=payload)
        if response.status_code == 200:
            data = response.json()
            del request.session['taxinvoice']
            messages.success(request, data['message'])
            return redirect('stock_transfer')
        elif response.status_code == 400:
            data = response.json()
            messages.error(request, data['message'])
            return render(request, 'login1.html')
        else:
            try:
                data = response.json()
                messages.error(request, data['message'])
                return redirect('stock_transfer')
            except:
                messages.error(request,response.text)
            return redirect('stock_transfer')
    else:
        return render(request,'stock_transfer/stock_transfer_home.html',{'data':stocktransferlistto,'depo':'active','wh_item_list':wh_item_list,'deponame':deponame,'menuname':menuname})


def busstation_search(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    accesskey = request.session['accesskey']
    url = "http://13.235.112.1/ziva/mobile-api/search-warehousemaster.php"

    payload = json.dumps({"accesskey": accesskey,
                              "searchterm": request.POST.get('searchterm'),
                              "type": "Bus station"
                              })
    headers = {
            'Content-Type': 'text/plain'
        }

    response = requests.request("GET", url, headers=headers, data=payload)
    if response.status_code == 200:
        data = response.json()
        return JsonResponse({'data': data})
    elif response.status_code == 400:
        data = response.json()
        messages.error(request, data['message'])
        return render(request, 'login1.html')


def get_busstation_item(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    code = request.session['codee']
    accesskey = request.session['accesskey']
    serchterm = request.POST.get('searchterm')
    pattern = r"\d+[mM][lL]"
    match = re.search(pattern, serchterm, re.IGNORECASE)
    role = request.session['role']
    if role == 'Admin':
        busitemcode = request.POST.get('busitemcode')
        busid1 = request.session['busid1']
        url = "http://13.235.112.1/ziva/mobile-api/warehouseinventory-search-new-admin.php"
        payload = json.dumps({
            "accesskey": accesskey,
            "id": busid1,
            "type": "Bus Station"
        })
        headers = {
            'Content-Type': 'application/json'
        }
        response = requests.request("GET", url, headers=headers, data=payload)
        if response.status_code == 200:
            data = response.json()
            list = data['warehouseinventorylist']
            for i in list:
                if str(i['itemcode']) == busitemcode:
                    data = {"busmrp": i["mrp"], "busuom": i["uom"], "busitemname": i["itemname"], "buscp_sno": i['cp_sno'],
                            "busexpdate": i['expirydate']}
            return JsonResponse({'data': data})
        elif response.status_code == 400:
            data = response.json()
            if data['message'] == 'Sorry! some details are missing':
                messages.error(request, data['message'])
                return redirect('/generate_transid')
            else:
                messages.error(request, data['message'])
                return redirect('/login')
    else:
            if match:
                extracted_text = match.group()
                print(extracted_text)

            url = "http://13.235.112.1/ziva/mobile-api/warehouseinventory-search.php"

            payload = json.dumps({
                "accesskey": accesskey,
                "searchterm":extracted_text,
                "id": code,
            })
            headers = {
                'Content-Type': 'application/json'

            }
            response = requests.request("GET", url, headers=headers, data=payload)
            if response.status_code == 200:
                data=response.json()
                return JsonResponse({'data': data})
            elif response.status_code == 400:
                data = response.json()
                messages.error(request, data['message'])
                return render(request, 'login1.html')



def busstation_add_stf(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    stocktransferlistto = request.session['stocktransferlistto']
    menuname = request.session['mylist']
    accesskey = request.session['accesskey']
    warehouseinventorylist = request.session['warehouseinventorylist']
    buslist = request.session['buslist']
    if request.method  == 'POST':
        busname = request.POST.get('txtBussearch')
        request.session['busname'] = busname
        url = "http://13.235.112.1/ziva/mobile-api/generate-transitid.php"

        payload = json.dumps({
            "accesskey": accesskey,
            "id": request.POST.get('busname'),
            "name":busname,
            "type": "Bus station"

        })
        headers = {
            'Content-Type': 'application/json'
        }
        response = requests.request("GET", url, headers=headers, data=payload)
        if response.status_code == 200:
            data = response.json()
            request.session['taxinvoice'] = data['taxinvoice']
            request.session['busid'] = request.POST.get('busname')
            return redirect('busstation_item_add')
        elif response.status_code == 400:
            data = response.json()
            if data['message'] == 'Sorry! some details are missing':
                messages.error(request, data['message'])
                return redirect('depot_item_list_admin')
            else:
                messages.error(request, data['message'])
                return redirect('/login')
        else:
            try:
                data = response.json()
                messages.error(request, data['message'])
            except:
                messages.error(request,response.text)
            return redirect('busstation_item_list')
    else:
        return render(request,'stock_transfer/stock_transfer_home.html',{'buslist':buslist,'bus':'active','menuname':menuname,'data':stocktransferlistto,'warehouseinventorylist':warehouseinventorylist})


def busstation_item_add(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    type = request.session['type']
    warehouseinventorylist = request.session['warehouseinventorylist']
    stocktransferlistto = request.session['stocktransferlistto']
    menuname = request.session['mylist']
    busstation_name =  request.session['busid']
    code = request.session['codee']
    taxinvoice = request.session['taxinvoice']
    accesskey = request.session['accesskey']
    buslist = request.session['buslist']

    if request.method == 'POST':
        url = "http://13.235.112.1/ziva/mobile-api/add-stockitem-warehouse.php"

        payload = json.dumps({
            "accesskey": accesskey,
            "type": request.POST.get('typeid2'),
            "cp_sno": request.POST.get('buscpsno'),
            "quantity": request.POST.get('quantity'),
            "freeqty": "",
            "noofbottles":request.POST.get('busnob'),
            "id": code,
            "transitid": taxinvoice
        })
        headers = {
            'Content-Type': 'application/json'
        }
        response = requests.request("GET", url, headers=headers, data=payload)
        if response.status_code == 200:
            data = response.json()
            messages.success(request, data['message'])
            return redirect('busstation_item_list')
        elif response.status_code == 400:
            data = response.json()
            if data['message'] == 'Sorry! some details are missing':
                messages.error(request, data['message'])
                return redirect('/busstation_item_add')
            else:
                messages.error(request, data['message'])
                return redirect('/login')
        else:
            try:
                data = response.json()
                messages.error(request, data['message'])
                return redirect('busstation_item_list')
            except:
                messages.error(request, response.text)

            return render(request, 'stock_transfer/stock_transfer_home.html', {'type':type,'buslist':buslist,'taxinvoice':taxinvoice,'busstation_name': busstation_name,'warehouseinventorylist':warehouseinventorylist,'bus':'active','data':stocktransferlistto,'menuname':menuname})

    else:
        return render(request, 'stock_transfer/stock_transfer_home.html', {'type':type,'buslist':buslist,'taxinvoice':taxinvoice,'busstation_name': busstation_name,'bus':'active','data':stocktransferlistto,'menuname':menuname,'warehouseinventorylist':warehouseinventorylist,'response':'bus200'})



def busstation_item_list(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    type = request.session['type']
    warehouseinventorylist = request.session['warehouseinventorylist']
    busstation_name =  request.session['busid']
    stocktransferlistto = request.session['stocktransferlistto']
    menuname = request.session['mylist']
    buslist = request.session['buslist']
    #busstation_name = request.session['name']
    accesskey = request.session['accesskey']
    taxinvoice  = request.session['taxinvoice']
    url = "http://13.235.112.1/ziva/mobile-api/stocktransfer-item-list.php"

    payload = json.dumps({"accesskey":accesskey,
        "transitid":taxinvoice
        })
    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.request("GET", url, headers=headers, data=payload)
    if response.status_code == 200:
        data=response.json()
        bus_item_list=data['stocktransferitemlist']
        return render(request,'stock_transfer/stock_transfer_home.html',{'status':'ok','response':'bus200','type':type,'buslist':buslist,'warehouseinventorylist':warehouseinventorylist,'taxinvoice':taxinvoice,'bus':'active','busstation_name': busstation_name,'data':stocktransferlistto,'menuname':menuname,'bus_item_list':bus_item_list,'bus_item_list1':bus_item_list[0]})
    elif response.status_code == 400:
        data = response.json()
        if data['message'] == 'Sorry! some details are missing':
            messages.error(request, data['message'])
            return redirect('busstation_item_list')
        else:
            messages.error(request, data['message'])
            return redirect('/login')
    else:
        return render(request, 'stock_transfer/stock_transfer_home.html',
                      {'response':'bus200','type':type,'buslist':buslist,'warehouseinventorylist': warehouseinventorylist, 'bus':'active','busstation_name': busstation_name,'data':stocktransferlistto,'menuname':menuname,'taxinvoice':taxinvoice})


def edit_stkbus_item(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    accesskey = request.session['accesskey']
    role = request.session['role']
    if role == 'Admin':
        bustaxinvoice = request.session['bustaxinvoice']
        url = "http://13.235.112.1/ziva/mobile-api/edit-stocktransfer-item.php"
        payload = json.dumps({
            "accesskey": accesskey,
            "noofbottles": request.POST.get('nob1'),
            "sno": request.POST.get('editsno'),
            "quantity": request.POST.get('qty'),
            "type": "Bus station",
            "transitid": bustaxinvoice
        })
        headers = {
            'Content-Type': 'application/json'
        }

        response = requests.request("GET", url, headers=headers, data=payload)
        if response.status_code == 200:
            data = response.json()
            messages.success(request, data['message'])
            return redirect('bus_item_list_admin')
        elif response.status_code == 400:
            data = response.json()
            messages.error(request, data['message'])
            return render(request, 'login1.html')
        else:
            try:
                data = response.json()
                messages.error(request, data['message'])
                return redirect('bus_item_list_admin')
            except:
                messages.error(request, response.text)
            return redirect('bus_item_list_admin')

    else:
            if request.method == 'POST':
                taxinvoice = request.session['taxinvoice']
                url = "http://13.235.112.1/ziva/mobile-api/edit-stocktransfer-item.php"
                payload = json.dumps({
                    "accesskey": accesskey,
                    "noofbottles":request.POST.get('nob1'),
                    "sno": request.POST.get('sno'),
                    "quantity":request.POST.get('qty'),
                    "type": "Bus station",
                    "transitid": taxinvoice
                })
                headers = {
                    'Content-Type': 'application/json'
                }

                response = requests.request("GET", url, headers=headers, data=payload)
                if response.status_code == 200:
                    data = response.json()
                    messages.success(request, data['message'])
                    return redirect('busstation_item_list')
                elif response.status_code == 400:
                    data = response.json()
                    messages.error(request, data['message'])
                    return render(request,'login1.html')
                else:
                    try:
                        data = response.json()
                        messages.error(request, data['message'])
                        return redirect('busstation_item_list')
                    except:
                        messages.error(request, response.text)
                    return redirect('busstation_item_list')
            else:
                return redirect('stock_transfer')

def edit_stkdepo_item(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    displayrole = request.session['displayrole']
    accesskey = request.session['accesskey']
    role = request.session['role']
    if role == 'Admin':
        depot_taxinvoice = request.session['depot_taxinvoice']
        url = "http://13.235.112.1/ziva/mobile-api/edit-stocktransfer-item.php"
        if displayrole == "UPPAL ZONAL STORES":
            payload = json.dumps({
                "accesskey": accesskey,
                "noofbottles": request.POST.get('nob1'),
                "sno": request.POST.get('editsno'),
                "quantity": request.POST.get('qty'),
                "type": "Warehouse",
                "transitid": depot_taxinvoice
            })
        else:
            payload = json.dumps({
                "accesskey": accesskey,
                "noofbottles": request.POST.get('nob1'),
                "sno": request.POST.get('editsno'),
                "quantity": request.POST.get('qty'),
                "type": "Bus station",
                "transitid": depot_taxinvoice
            })
        headers = {
            'Content-Type': 'application/json'
        }

        response = requests.request("GET", url, headers=headers, data=payload)
        if response.status_code == 200:
            data = response.json()
            messages.success(request, data['message'])
            return redirect('depot_item_list_admin')
        elif response.status_code == 400:
            data = response.json()
            if data['message'] == 'Sorry! some details are missing':
                messages.error(request, data['message'])
                return redirect('depot_item_list_admin')
            else:
                messages.error(request, data['message'])
                return redirect('/login')
        else:
            try:
                data = response.json()
                messages.error(request, data['message'])
                return redirect('depot_item_list_admin')
            except:
                messages.error(request, response.text)
            return redirect('depot_item_list_admin')
    else:
            if request.method == 'POST':
                taxinvoice = request.session['taxinvoice']
                url = "http://13.235.112.1/ziva/mobile-api/edit-stocktransfer-item.php"
                if displayrole == "UPPAL ZONAL STORES":
                    payload = json.dumps({
                        "accesskey": accesskey,
                        "noofbottles": request.POST.get('nob1'),
                        "sno": request.POST.get('sno'),
                        "quantity": request.POST.get('qty'),
                        "type": "Warehouse",
                        "transitid": taxinvoice
                    })
                else:
                    payload = json.dumps({
                        "accesskey": accesskey,
                        "noofbottles": request.POST.get('nob1'),
                        "sno": request.POST.get('sno'),
                        "quantity": request.POST.get('qty'),
                        "type": "Bus station",
                        "transitid": taxinvoice
                    })
                headers = {
                    'Content-Type': 'application/json'
                }

                response = requests.request("GET", url, headers=headers, data=payload)
                if response.status_code == 200:
                    data = response.json()
                    messages.success(request, data['message'])
                    return redirect('depo_item_list')
                elif response.status_code == 400:
                    data = response.json()
                    if data['message'] == 'Sorry! some details are missing':
                        messages.error(request, data['message'])
                        return redirect('depo_item_list')
                    else:
                        messages.error(request, data['message'])
                        return redirect('/login')
                else:
                    try:
                        data = response.json()
                        messages.error(request, data['message'])
                        return redirect('depo_item_list')
                    except:
                        messages.error(request, response.text)
                    return redirect('depo_item_list')
            else:
                return redirect('stock_transfer')

def complete_businv(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    stocktransferlistto = request.session['stocktransferlistto']
    menuname = request.session['mylist']
    deponame = request.session['name']
    accesskey = request.session['accesskey']
    taxinvoice = request.session['taxinvoice']
    buslist = request.session['buslist']
    if  request.method == 'POST':
        url = "http://13.235.112.1/ziva/mobile-api/complete-stock.php"

        payload = json.dumps({
            "accesskey": accesskey,
            "transid": taxinvoice,
            "remarks": request.POST.get('remarks'),
            "date": request.POST.get('date'),

        })
        headers = {
            'Content-Type': 'application/json'
        }
        response = requests.request("GET", url, headers=headers, data=payload)
        if response.status_code == 200:
            data = response.json()
            del request.session['taxinvoice']
            messages.success(request, data['message'])
            return redirect('stock_transfer')
        elif response.status_code == 400:
            data = response.json()
            messages.error(request, data['message'])
            return render(request,'login1.html')
        else:
            try:
                data = response.json()
                messages.error(request, data['message'])
                return redirect('stock_transfer')
            except:
                messages.error(request,response.text)
            return redirect('stock_transfer')
    else:
        return render(request,'stock_transfer/stock_transfer_home.html',{'buslist':buslist,'data':stocktransferlistto,'wh_item_list':wh_item_list,'deponame':deponame,'menuname':menuname})


def region_status_active(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    accesskey = request.session['accesskey']

    url = "http://13.235.112.1/ziva/mobile-api/status-change.php"

    payload = json.dumps({
        "accesskey": accesskey,
        "sno": request.POST.get('id'),
        "type": "Regionmaster",
        "status": request.POST.get('status')
    })
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    if response.status_code == 200:
        data = response.json()
        messages.success(request, data['message'])
        return redirect('/region_list')
    elif response.status_code == 400:
        data = response.json()
        messages.error(request, data['message'])
        return render(request, 'login1.html')
    else:
        try:
            data = response.json()
            messages.error(request, data['message'])
            return redirect('/region_list')
        except:
            messages.error(request, response.text)
        return redirect('/region_list')
def bus_list(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    try:
        menuname = request.session['mylist']
        accesskey = request.session['accesskey']
        url = "http://13.235.112.1/ziva/mobile-api/depo-list.php"

        payload = json.dumps({"accesskey": accesskey})
        headers = {
            'Content-Type': 'text/plain'
        }

        response = requests.request("GET", url, headers=headers, data=payload)

        data = response.json()
        depolist = data['depolist']

        url = "http://13.235.112.1/ziva/mobile-api/warehousemaster-list.php"

        payload = json.dumps({"accesskey": accesskey})
        headers = {
            'Content-Type': 'text/plain'
        }
        response = requests.request("GET", url, headers=headers, data=payload)

        data = response.json()
        wh_masterlist = data['warehouselist']
        if request.method == 'POST':
                url = "http://13.235.112.1/ziva/mobile-api/bus-list-new.php"
                payload = json.dumps({
                    "accesskey": accesskey,
                    "warehouseid": request.POST.get("warehouseid"),
                    "regionid":request.POST.get("regionid"),
                    "depoid": request.POST.get("depoid")
                })
                headers = {
                    'Content-Type': 'application/json'
                }

                response = requests.request("GET", url, headers=headers, data=payload)
                if response.status_code == 200:
                    data = response.json()
                    bus = data['buslist']
                    return render(request,'busstation/bus_list.html',{'bus':bus,'data':depolist,'menuname':menuname,'wh_masterlist':wh_masterlist})
                else:
                    return render(request, 'busstation/bus_list.html',{'data':depolist,'menuname':menuname,'wh_masterlist':wh_masterlist})
        else:
            url = "http://13.235.112.1/ziva/mobile-api/bus-list.php"
            payload = json.dumps({
                "accesskey": accesskey
            })
            headers = {
                'Content-Type': 'application/json'
            }

            response = requests.request("GET", url, headers=headers, data=payload)
            if response.status_code == 200:
                data = response.json()
                bus = data['buslist']
                return render(request, 'busstation/bus_list.html',
                              {'bus': bus, 'data': depolist, 'menuname': menuname, 'wh_masterlist': wh_masterlist})
            else:
                return render(request, 'busstation/bus_list.html',
                              {'data': depolist, 'menuname': menuname, 'wh_masterlist': wh_masterlist})
    except:
        if response.status_code == 400:
            messages.error(request,data['message'])
            return render(request,'login1.html')
    return render(request, 'busstation/bus_list.html')
def bus_add(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    try:
        menuname = request.session['mylist']
        accesskey = request.session['accesskey']

        url = "http://13.235.112.1/ziva/mobile-api/depo-list.php"

        payload = json.dumps({"accesskey": accesskey})
        headers = {
            'Content-Type': 'text/plain'
        }
        response = requests.request("GET", url, headers=headers, data=payload)
        data = response.json()
        depolist = data['depolist']

        if request.method == 'POST':
            id = request.POST.get("depoid")
            for i in depolist:
                if i['depoid'] == id:
                    regionid = i['regionid']
                    regionname = i['regionname']
                    warehouseid = i['warehouseid']
                    warehousename = i['warehousename']
                    deponame = i['depo_name']
                    payload = json.dumps(
                    {
                        "accesskey": accesskey,
                        "busstationname":request.POST.get('busname'),
                        "depoid": request.POST.get('depoid'),
                        "deponame": deponame,
                        "busstation_contact_no":" ",
                        "busstation_manager": " ",
                        "regionid":  regionid,
                        "regionname": regionname,
                        "warehouseid":  warehouseid,
                        "warehousename": warehousename
                    })
                    headers = {
                        'Content-Type': 'text/plain'
                    }
                    url="http://13.235.112.1/ziva/mobile-api/create-busstation.php"
                    response = requests.request("GET", url, headers=headers, data=payload)
                    if response.status_code == 200:
                        data = response.json()
                        messages.success(request,data['message'])
                        return redirect('/bus_list')
                    else:
                        data = response.json()
                        messages.error(request, data['message'])
                        return redirect('/bus_list')
        return render(request,'busstation/bus_add.html',{'data':depolist,'menuname':menuname})
    except:
        if response.status_code == 400:
            data = response.json()
            messages.error(request, data['message'])
            return render(request,'login1.html')
    return render(request,'busstation/bus_add.html')
def  get_bus(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    accesskey = request.session['accesskey']
    url = "http://13.235.112.1/ziva/mobile-api/bus-search.php"

    payload = json.dumps({
        "accesskey":accesskey ,
        "busid": request.POST.get('id')
    })

    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    if response.status_code == 200:
        data2 = response.json()
        return JsonResponse({'data': data2})
    elif response.status_code == 400:
        data = response.json()
        if data['message'] == 'Sorry! some details are missing':
            messages.error(request, data['message'])
            return JsonResponse({'data': data})
        else:
            messages.error(request, data['message'])
            return redirect('/login')


def bus_edit(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    accesskey = request.session['accesskey']
    if request.method == 'POST':
        payload = json.dumps(
            {
                "accesskey": accesskey,
                "busstation_id":request.POST.get('busid1'),
                "busstationname": request.POST.get('busname1'),
                "depoid": request.POST.get('depoid1'),
                "deponame": request.POST.get('deponame1'),
                "busstation_contact_no": request.POST.get('mobileno1'),
                "busstation_manager": request.POST.get('busmanager1'),
                "regionid": request.POST.get('regionid'),
                "regionname": request.POST.get('regionname'),
                "warehouseid": request.POST.get('warehouseid'),
                "warehousename": request.POST.get('warehousename')
            })
        headers = {
            'Content-Type': 'text/plain'
        }
        url = "http://13.235.112.1/ziva/mobile-api/edit-busstationmaster.php"
        response = requests.request("GET", url, headers=headers, data=payload)
        if response.status_code == 200:
            data = response.json()
            messages.success(request, data['message'])
            return redirect('/bus_list')
        elif response.status_code == 400:
            data = response.json()
            text = data['message']
            if   'some details are missing' in text:
                messages.error(request, data['message'])
                return redirect('/bus_list')
            else:
                messages.error(request, data['message'])
                return redirect('/login')
        else:
            try:
                r = response.json()
                messages.error(request, r['message'])
            except:
                messages.error(request, response.text)
            return redirect('/bus_list')
    return redirect('/bus_list')

def get_ps_stock(request):
    accesskey = request.session['accesskey']
    url = "http://13.235.112.1/ziva/mobile-api/depo-stockpointinventory.php"
    payload = json.dumps(
        {
            "accesskey": accesskey,

        })
    headers = {
        'Content-Type': 'text/plain'
    }
    response = requests.request("GET", url, headers=headers, data=payload)
    if response.status_code == 200:
        data2 = response.json()
        return JsonResponse({'data': data2})
    elif response.status_code == 400:
        data = response.json()
        if data['message'] == 'Sorry! some details are missing':
            return JsonResponse({'data': data})
        else:
            messages.error(request, data['message'])
            return redirect('/login')
    elif response.status_code == 503:
        data = response.json()
        return JsonResponse({'data': data})
    elif response.status_code == 500:
        data = {'error': 'true', 'message': 'Internal server error'}
        return JsonResponse({'data': data})
    else:
        data = {'error': 'true', 'message': 'something went wrong'}
        return JsonResponse({'data': data})

def get_whinventory(request):
    accesskey = request.session['accesskey']
    url = "http://13.235.112.1/ziva/mobile-api/warehouse-inventory-depologin.php"
    payload = json.dumps(
        {
            "accesskey": accesskey,
            "warehouseid":request.POST.get('warehouseid')

        })
    headers = {
        'Content-Type': 'text/plain'
    }
    response = requests.request("GET", url, headers=headers, data=payload)
    if response.status_code == 200:
        data2 = response.json()
        return JsonResponse({'data': data2})
    elif response.status_code == 400:
        data = response.json()
        if data['message'] == 'Sorry! some details are missing':
            return JsonResponse({'data': data})
        else:
            messages.error(request, data['message'])
            return redirect('/login')
    elif response.status_code == 503:
        data = response.json()
        return JsonResponse({'data': data})
    elif response.status_code == 500:
        data = {'error': 'true', 'message': 'Internal server error'}
        return JsonResponse({'data': data})
    else:
        data = {'error': 'true', 'message': 'something went wrong'}
        return JsonResponse({'data': data})

def live_inventory(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    try:
            menuname = request.session['mylist']
            accesskey = request.session['accesskey']
            url = "http://13.235.112.1/ziva/mobile-api/warehousemaster-list.php"

            payload = json.dumps({"accesskey": accesskey})
            headers = {
                'Content-Type': 'text/plain'
            }
            response = requests.request("GET", url, headers=headers, data=payload)

            data = response.json()
            wh_masterlist = data['warehouselist']
            url = "http://13.235.112.1/ziva/mobile-api/inventorylist-new.php"
            payload = json.dumps(
                {
                    "accesskey": accesskey

                })
            headers = {
                'Content-Type': 'text/plain'
            }
            response = requests.request("GET", url, headers=headers, data=payload)
            if response.status_code == 200:
                data = response.json()
                inventorylist = data['inventorylist']
                return render(request,'grn/inventory.html',{'data':inventorylist,'menuname':menuname,'wh_masterlist':wh_masterlist})
            else:
                data = response.json()
                return render(request,'grn/inventory.html',{'menuname':menuname,'wh_masterlist':wh_masterlist})
    except:
        if response.status_code == 400:
            messages.error(request, data['message'])
            return render(request,'login1.html')
    return render(request, 'grn/inventory.html',{'menuname':menuname})


def batch_codeexpry1(request, id):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    menuname = request.session['mylist']
    accesskey = request.session['accesskey']
    role = request.session['role']
    url = "http://13.235.112.1/ziva/mobile-api/batchcode-expdate-inventorylist.php"
    payload = json.dumps(
        {
            "accesskey": accesskey,
            "itemcode": id
        })
    headers = {
        'Content-Type': 'text/plain'
    }
    response = requests.request("GET", url, headers=headers, data=payload)
    if response.status_code == 200:
        data = response.json()
        inventorylist = data['inventorylist']
        messages.success(request, data['message'])
        return render(request, 'grn/batchcode.html', {'data': inventorylist, 'menuname': menuname})
    elif response.status_code == 400:
        data = response.json()
        messages.error(request, data['message'])
        return render(request, 'login1.html')
    else:
        data = response.json()
        messages.error(request, data['message'])
        return render(request, 'grn/batchcode.html', {'menuname': menuname})




def batch_codeexpry(request,id):
            if 'accesskey' not in request.session:
                messages.error(request, 'Access denied!')
                return redirect('/login')
            menuname = request.session['mylist']
            accesskey = request.session['accesskey']
            role = request.session['role']
            url = "http://13.235.112.1/ziva/mobile-api/batchcode-expdate-inventorylist.php"
            payload = json.dumps(
                {
                    "accesskey":accesskey ,
                    "itemcode" : id,
                })
            headers = {
                'Content-Type': 'text/plain'
            }
            response = requests.request("GET", url, headers=headers, data=payload)
            if response.status_code == 200:
                data = response.json()
                inventorylist = data['inventorylist']
                messages.success(request, data['message'])
                return render(request, 'grn/batchcode.html', {'data': inventorylist,'menuname':menuname})
            elif response.status_code == 400:
                data = response.json()
                messages.error(request, data['message'])
                return render(request, 'login1.html')
            else:
                data = response.json()
                messages.error(request, data['message'])
                return render(request, 'grn/batchcode.html',{'menuname':menuname})

def get_storetype(request):
            if 'accesskey' not in request.session:
                messages.error(request, 'Access denied!')
                return redirect('/login')
            accesskey = request.session['accesskey']
            id = request.POST.get('id')
            url = "http://13.235.112.1/ziva/mobile-api/dropdwn-table-list.php"

            payload = json.dumps({"accesskey": accesskey, "name": "Storetype"})
            headers = {
                'Content-Type': 'text/plain'
            }

            response = requests.request("GET", url, headers=headers, data=payload)
            if response.status_code == 200:
                data = response.json()
                storetype_list = data['itemmasterlist']
                for i in storetype_list:
                    if str(i['ddcode']) == id:
                        data = {"ddcode": i["ddcode"], "displayname": i["displayname"], "sno": i["sno"]}
                return JsonResponse({'data': data})
            elif response.status_code == 400:
                data = response.json()
                messages.error(request, data['message'])
                return render(request, 'login1.html')
            else:
                try:
                    data = response.json()
                    messages.error(request, data['message'])
                except:
                    messages.error(request, response.text)
                return redirect('/storetype_list')

def edit_storetype(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    accesskey = request.session['accesskey']
    if request.method == 'POST':
        payload = json.dumps(
            {
                "accesskey": accesskey,
                "type": "Storetype",
                "value": request.POST.get('storetypename'),
                "sno": request.POST.get('txtHdnId2')

            })
        headers = {
            'Content-Type': 'text/plain'
        }
        url = "http://13.235.112.1/ziva/mobile-api/edit-masterdata.php"
        response = requests.request("GET", url, headers=headers, data=payload)
        if response.status_code == 200:
            data = response.json()
            messages.success(request, data['message'])
            return redirect('/storetype_list')
        elif response.status_code == 400:
            data = response.json()
            if data['message'] == 'Sorry! some details are missing':
                messages.error(request, data['message'])
                return redirect('/storetype_list')
            else:
                messages.error(request, data['message'])
                return redirect('/login')
        else:
            try:
                r = response.json()
                messages.error(request, r['message'])
            except:
                messages.error(request, response.text)
            return redirect('/storetype_list')
    return redirect('/storetype_list')


def get_case(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    accesskey = request.session['accesskey']
    id = request.POST.get('id')
    url = "http://13.235.112.1/ziva/mobile-api/dropdwn-table-list.php"

    payload = json.dumps({"accesskey": accesskey, "name": "UOM"})
    headers = {
        'Content-Type': 'text/plain'
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    if response.status_code == 200:
        data = response.json()
        storetype_list = data['itemmasterlist']
        for i in storetype_list:
            if str(i['ddcode']) == id:
                data = {"ddcode": i["ddcode"], "displayname": i["displayname"], "sno": i["sno"]}
        return JsonResponse({'data': data})
    elif response.status_code == 400:
        data = response.json()
        messages.error(request, data['message'])
        return render(request, 'login1.html')
    else:
        try:
            data = response.json()
            messages.error(request, data['message'])
        except:
            messages.error(request, response.text)
        return redirect('/uom_list')



def edit_case(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    accesskey = request.session['accesskey']
    if request.method == 'POST':
        payload = json.dumps(
            {
                "accesskey": accesskey,
                "type": "UOM",
                "value": request.POST.get('case'),
                "sno": request.POST.get('txtHdnId2')

            })
        headers = {
            'Content-Type': 'text/plain'
        }
        url = "http://13.235.112.1/ziva/mobile-api/edit-masterdata.php"
        response = requests.request("GET", url, headers=headers, data=payload)
        if response.status_code == 200:
            data = response.json()
            messages.success(request, data['message'])
            return redirect('/uom_list')
        elif response.status_code == 400:
            data = response.json()
            if data['message'] == 'Sorry! some details are missing':
                messages.error(request, data['message'])
                return redirect('/uom_list')
            else:
                messages.error(request, data['message'])
                return redirect('/login')
        else:
            try:
                r = response.json()
                messages.error(request, r['message'])
            except:
                messages.error(request, response.text)
            return redirect('/uom_list')
    return redirect('/uom_list')

def get_category(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    id = request.POST.get('id')
    accesskey = request.session['accesskey']
    url = "http://13.235.112.1/ziva/mobile-api/dropdwn-table-list.php"

    payload = json.dumps({"accesskey": accesskey, "name": "CATEGORY"})
    headers = {
        'Content-Type': 'text/plain'
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    if response.status_code == 200:
        data = response.json()
        category_list = data['itemmasterlist']
        for i in category_list:
            if str(i['ddcode']) == id:
                data = {"ddcode": i["ddcode"], "displayname": i["displayname"], "sno": i["sno"]}
        return JsonResponse({'data': data})
    elif response.status_code == 400:
        data = response.json()
        messages.error(request, data['message'])
        return render(request, 'login1.html')

def edit_category(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    accesskey = request.session['accesskey']
    if request.method == 'POST':
        payload = json.dumps(
            {
                "accesskey": accesskey,
                "type": "CATEGORY",
                "value": request.POST.get('category'),
                "sno": request.POST.get('txtHdnId2')

            })
        headers = {
            'Content-Type': 'text/plain'
        }
        url = "http://13.235.112.1/ziva/mobile-api/edit-masterdata.php"
        response = requests.request("GET", url, headers=headers, data=payload)
        if response.status_code == 200:
            data = response.json()
            messages.success(request, data['message'])
            return redirect('/category_list')
        elif response.status_code == 400:
            data = response.json()
            if data['message'] == 'Sorry! some details are missing':
                messages.error(request, data['message'])
                return redirect('/category_list')
            else:
                messages.error(request, data['message'])
                return redirect('/login')
        else:
            try:
                r = response.json()
                messages.error(request, r['message'])
            except:
                messages.error(request, response.text)
            return redirect('/category_list')
    return redirect('/category_list')

def edit_gst(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    accesskey = request.session['accesskey']
    if request.method == 'POST':
        payload = json.dumps(
            {
                "accesskey": accesskey,
                "type": "GST",
                "value": request.POST.get('gst'),
                "sno": request.POST.get('txtHdnId2')

            })
        headers = {
            'Content-Type': 'text/plain'
        }
        url = "http://13.235.112.1/ziva/mobile-api/edit-masterdata.php"
        response = requests.request("GET", url, headers=headers, data=payload)
        if response.status_code == 200:
            data = response.json()
            messages.success(request, data['message'])
            return redirect('/gst_list')
        elif response.status_code == 400:
            data = response.json()
            if data['message'] == 'Sorry! some details are missing':
                messages.error(request, data['message'])
                return redirect('/gst_list')
            else:
                messages.error(request, data['message'])
                return redirect('/login')
        else:
            try:
                r = response.json()
                messages.error(request, r['message'])
            except:
                messages.error(request, response.text)
            return redirect('/gst_list')

    return redirect('/gst_list')

def get_gst(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    id = request.POST.get('id')
    accesskey = request.session['accesskey']
    url = "http://13.235.112.1/ziva/mobile-api/dropdwn-table-list.php"

    payload = json.dumps({"accesskey": accesskey, "name": "GST"})
    headers = {
        'Content-Type': 'text/plain'
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    if response.status_code == 200:
        data = response.json()
        category_list = data['itemmasterlist']
        for i in category_list:
            if str(i['ddcode']) == id:
                data = {"ddcode": i["ddcode"], "displayname": i["displayname"], "sno": i["sno"]}
        return JsonResponse({'data': data})
    elif response.status_code == 400:
        data = response.json()
        messages.error(request, data['message'])
        return render(request, 'login1.html')

def get_city(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    id = request.POST.get('id')
    accesskey = request.session['accesskey']
    url = "http://13.235.112.1/ziva/mobile-api/dropdwn-table-list.php"

    payload = json.dumps({"accesskey": accesskey, "name": "CITY"})
    headers = {
        'Content-Type': 'text/plain'
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    if response.status_code == 200:
        data = response.json()
        category_list = data['itemmasterlist']
        for i in category_list:
            if str(i['ddcode']) == id:
                data = {"ddcode": i["ddcode"], "displayname": i["displayname"], "sno": i["sno"]}
        return JsonResponse({'data': data})
    elif response.status_code == 400:
        data = response.json()
        messages.error(request, data['message'])
        return render(request, 'login1.html')

def edit_city(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    accesskey = request.session['accesskey']
    if request.method == 'POST':
        payload = json.dumps(
            {
                "accesskey": accesskey,
                "type": "CITY",
                "value": request.POST.get('city'),
                "sno": request.POST.get('txtHdnId2')

            })
        headers = {
            'Content-Type': 'text/plain'
        }
        url = "http://13.235.112.1/ziva/mobile-api/edit-masterdata.php"
        response = requests.request("GET", url, headers=headers, data=payload)
        if response.status_code == 200:
            data = response.json()
            messages.success(request, data['message'])
            return redirect('/city_list')
        elif response.status_code == 400:
            data = response.json()
            if data['message'] == 'Sorry! some details are missing':
                messages.error(request, data['message'])
                return redirect('/city_list')
            else:
                messages.error(request, data['message'])
                return redirect('/login')
        else:
            try:
                r = response.json()
                messages.error(request, r['message'])
            except:
                messages.error(request, response.text)
            return redirect('/city_list')
    return redirect('/city_list')


def get_level(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    id = request.POST.get('id')
    accesskey = request.session['accesskey']
    url = "http://13.235.112.1/ziva/mobile-api/dropdwn-table-list.php"

    payload = json.dumps({"accesskey": accesskey, "name": "LEVEL"})
    headers = {
        'Content-Type': 'text/plain'
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    if response.status_code == 200:
        data = response.json()
        category_list = data['itemmasterlist']
        for i in category_list:
            if str(i['ddcode']) == id:
                data = {"ddcode": i["ddcode"], "displayname": i["displayname"], "sno": i["sno"]}
        return JsonResponse({'data': data})
    elif response.status_code == 400:
        data = response.json()
        messages.error(request, data['message'])
        return render(request, 'login1.html')



def edit_level(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    accesskey = request.session['accesskey']
    if request.method == 'POST':
        payload = json.dumps(
            {
                "accesskey": accesskey,
                "type": "LEVEL",
                "value": request.POST.get('level'),
                "sno": request.POST.get('txtHdnId2')

            })
        headers = {
            'Content-Type': 'text/plain'
        }
        url = "http://13.235.112.1/ziva/mobile-api/edit-masterdata.php"
        response = requests.request("GET", url, headers=headers, data=payload)
        if response.status_code == 200:
            data = response.json()
            messages.success(request, data['message'])
            return redirect('/level_list')
        elif response.status_code == 400:
            data = response.json()
            if data['message'] == 'Sorry! some details are missing':
                messages.error(request, data['message'])
                return redirect('/level_list')
            else:
                messages.error(request, data['message'])
                return redirect('/login')
        else:
            try:
                r = response.json()
                messages.error(request, r['message'])
            except:
                messages.error(request, response.text)
            return redirect('/level_list')
    return redirect('/level_list')



def get_role(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    id = request.POST.get('id')
    accesskey = request.session['accesskey']
    url = "http://13.235.112.1/ziva/mobile-api/dropdwn-table-list.php"

    payload = json.dumps({"accesskey": accesskey, "name": "ROLE"})
    headers = {
        'Content-Type': 'text/plain'
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    if response.status_code == 200:
        data = response.json()
        category_list = data['itemmasterlist']
        for i in category_list:
            if str(i['ddcode']) == id:
                data = {"ddcode": i["ddcode"], "displayname": i["displayname"], "sno": i["sno"]}
        return JsonResponse({'data': data})
    elif response.status_code == 400:
        data = response.json()
        messages.error(request, data['message'])
        return render(request, 'login1.html')

def edit_role(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    accesskey = request.session['accesskey']
    if request.method == 'POST':
        payload = json.dumps(
            {
                "accesskey": accesskey,
                "type": "ROLE",
                "value": request.POST.get('role'),
                "sno": request.POST.get('txtHdnId2')

            })
        headers = {
            'Content-Type': 'text/plain'
        }
        url = "http://13.235.112.1/ziva/mobile-api/edit-masterdata.php"
        response = requests.request("GET", url, headers=headers, data=payload)
        if response.status_code == 200:
            data = response.json()
            messages.success(request, data['message'])
            return redirect('/role_list')
        elif response.status_code == 400:
            data = response.json()
            if data['message'] == 'Sorry! some details are missing':
                messages.error(request, data['message'])
                return redirect('/role_list')
            else:
                messages.error(request, data['message'])
                return redirect('/login')
        else:
            try:
                r = response.json()
                messages.error(request, r['message'])
            except:
                messages.error(request, response.text)
            return redirect('/role_list')
    return redirect('/role_list')


def get_state(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    id = request.POST.get('id')
    accesskey = request.session['accesskey']
    url = "http://13.235.112.1/ziva/mobile-api/dropdwn-table-list.php"

    payload = json.dumps({"accesskey": accesskey, "name": "STATE"})
    headers = {
        'Content-Type': 'text/plain'
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    if response.status_code == 200:
        data = response.json()
        category_list = data['itemmasterlist']
        for i in category_list:
            if str(i['ddcode']) == id:
                data = {"ddcode": i["ddcode"], "displayname": i["displayname"], "sno": i["sno"]}
        return JsonResponse({'data': data})
    elif response.status_code == 400:
        data = response.json()
        messages.error(request, data['message'])
        return render(request, 'login1.html')

def edit_state(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    accesskey = request.session['accesskey']
    if request.method == 'POST':
        payload = json.dumps(
            {
                "accesskey": accesskey,
                "type": "STATE",
                "value": request.POST.get('state'),
                "sno": request.POST.get('txtHdnId2')

            })
        headers = {
            'Content-Type': 'text/plain'
        }
        url = "http://13.235.112.1/ziva/mobile-api/edit-masterdata.php"
        response = requests.request("GET", url, headers=headers, data=payload)
        if response.status_code == 200:
            data = response.json()
            messages.success(request, data['message'])
            return redirect('/state_list')
        elif response.status_code == 400:
            data = response.json()
            if data['message'] == 'Sorry! some details are missing':
                messages.error(request, data['message'])
                return redirect('/state_list')
            else:
                messages.error(request, data['message'])
                return redirect('/login')
        else:
            try:
                r = response.json()
                messages.error(request, r['message'])
            except:
                messages.error(request, response.text)
            return redirect('/state_list')
    return redirect('/state_list')


def get_pricelist(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    id = request.POST.get('id')
    accesskey = request.session['accesskey']
    url = "http://13.235.112.1/ziva/mobile-api/price-list.php"

    payload = json.dumps({"accesskey": accesskey})
    headers = {
        'Content-Type': 'text/plain'
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    if response.status_code == 200:
        data = response.json()
        category_list = data['pricelist']
        for i in category_list:
            if str(i['price_code']) == id:
                data = {"ddcode": i["price_code"], "mrp": i["mrp"], "sno": i["sno"]}
        return JsonResponse({'data': data})
    elif response.status_code == 400:
        data = response.json()
        messages.error(request, data['message'])
        return render(request, 'login1.html')

def edit_price(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    accesskey = request.session['accesskey']
    if request.method == 'POST':
        payload = json.dumps(
            {
                "accesskey": accesskey,
                "mrp": request.POST.get('price'),
                "sno": request.POST.get('txtHdnId2')
            })
        headers = {
            'Content-Type': 'text/plain'
        }
        url = "http://13.235.112.1/ziva/mobile-api/edit-pricedata.php"
        response = requests.request("GET", url, headers=headers, data=payload)
        if response.status_code == 200:
            data = response.json()
            messages.success(request, data['message'])
            return redirect('/des_list')
        elif response.status_code == 400:
            data = response.json()
            if data['message'] == 'Sorry! some details are missing':
                messages.error(request, data['message'])
                return redirect('/des_list')
            else:
                messages.error(request, data['message'])
                return redirect('/login')
        else:
            try:
                r = response.json()
                messages.error(request, r['message'])
            except:
                messages.error(request, response.text)
            return redirect('/des_list')

    return redirect('/des_list')


def payment_report(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    try:

            menuname=request.session['mylist']
            accesskey = request.session['accesskey']
            url = "http://13.235.112.1/ziva/mobile-api/dates-filter.php"

            payload = json.dumps({"accesskey": accesskey})
            headers = {
                'Content-Type': 'text/plain'
            }
            response = requests.request("GET", url, headers=headers, data=payload)

            data = response.json()
            selectrange = data['timingslist']
            url = "http://13.235.112.1/ziva/mobile-api/warehousemaster-list.php"

            payload = json.dumps({"accesskey": accesskey})
            headers = {
                'Content-Type': 'text/plain'
            }
            response = requests.request("GET", url, headers=headers, data=payload)

            data = response.json()
            wh_masterlist = data['warehouselist']

            if request.method == 'POST':
                range = request.POST.get('from')
                url = "http://13.235.112.1/ziva/mobile-api/warehousewise-total-report.php"
                if range == 'Custom Dates':
                    frdate = request.POST.get('fdate')
                    trdate = request.POST.get('tdate')
                else:
                    frdate =  request.POST.get('from')
                    trdate =  request.POST.get('from')
                payload = json.dumps(
                        {
                            "accesskey": accesskey,
                            "fromdate": frdate,
                            "todate": trdate

                        })

                headers = {
                    'Content-Type': 'text/plain'
                }

                response = requests.request("GET", url, headers=headers, data=payload)
                if response.status_code == 200:
                    data = response.json()
                    item  = data['daywisesaleswarehouselist']

                url = "http://13.235.112.1/ziva/mobile-api/warehousewise-sales-report.php"

                if range == 'Custom Dates':
                        fdate = request.POST.get('fdate')
                        tdate = request.POST.get('tdate')
                else:
                        fdate = request.POST.get('from')
                        tdate = request.POST.get('from')
                payload = json.dumps(
                    {
                        "accesskey": accesskey,
                        "fromdate": fdate,
                        "todate": tdate,
                        "warehouseid": request.POST.get('warehouseid1')

                    })

                headers = {
                    'Content-Type': 'text/plain'
                }

                response = requests.request("GET", url, headers=headers, data=payload)
                if response.status_code == 200:
                    data = response.json()
                    daywisesaleslist = data['daywisesaleswarehouselist']
                    return render(request, 'Reports/payments.html', {'item':item[0],'fdate':fdate,'tdate':tdate,'menuname':menuname,'data': daywisesaleslist,'wh_masterlist':wh_masterlist,'selectrange':selectrange})
                else:
                    data = response.json()
                    messages.error(request, data['message'])
                    return render(request,'Reports/payments.html',{'item':item[0],'menuname':menuname,"wh_masterlist":wh_masterlist,'selectrange':selectrange,'fdate':fdate,'tdate':tdate,})
            else:
                url = "http://13.235.112.1/ziva/mobile-api/warehousewise-total-report.php"

                payload = json.dumps(
                        {
                            "accesskey": accesskey,
                            "fromdate": "Current Month",
                            "todate": "Current Month"
                        })

                headers = {
                    'Content-Type': 'text/plain'
                }

                response = requests.request("GET", url, headers=headers, data=payload)
                if response.status_code == 200:
                    data = response.json()
                    item = data['daywisesaleswarehouselist']

                payload = json.dumps(
                        {

                            "accesskey": accesskey,
                            "fromdate": "Current Month",
                            "todate": "Current Month",
                            "warehouseid": "All"

                    })

                headers = {
                    'Content-Type': 'text/plain'
                }
                url = "http://13.235.112.1/ziva/mobile-api/warehousewise-sales-report.php"
                response = requests.request("GET", url, headers=headers, data=payload)
                if response.status_code == 200:
                    data = response.json()
                    daywisesaleslist = data['daywisesaleswarehouselist']
                    return render(request, 'Reports/payments.html',{'item':item[0],'fdate':"Current Month",'tdate':"Current Month",'menuname':menuname,'data':daywisesaleslist,'wh_masterlist':wh_masterlist,'selectrange':selectrange})
                else:
                    return render(request, 'Reports/payments.html',{'menuname':menuname,'fdate':"Current Month",'tdate':"Current Month",'wh_masterlist':wh_masterlist,'selectrange':selectrange})
    except:
        if response.status_code == 400:
            data = response.json()
            messages.error(request, data['message'])
            return render(request, 'login1.html')
    return render(request, 'Reports/payments.html',{'menuname':menuname})



def warehouse_items(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    accesskey = request.session['accesskey']

    url = "http://13.235.112.1/ziva/mobile-api/warehouse-itemwise-report.php"

    payload = json.dumps(
        {
            "accesskey": accesskey,
            "fromdate": request.GET.get('fdate'),
            "todate": request.GET.get('tdate'),
            "warehouseid": request.GET.get('id'),

        })

    headers = {
        'Content-Type': 'text/plain'
    }
    response = requests.request("GET", url, headers=headers, data=payload)
    if response.status_code == 200:
        response = response.json()
        return JsonResponse({'response': response})
    elif response.status_code == 400:
        data = response.json()
        messages.error(request, data['message'])
        return render(request, 'login1.html')
    if response.status_code == 503:
        response = response.json()
        return JsonResponse({'response': response})
def bus_items(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    accesskey = request.session['accesskey']

    url = "http://13.235.112.1/ziva/mobile-api/busstation-itemwise-report.php"

    payload = json.dumps(
        {
            "accesskey": accesskey,
            "fromdate": request.GET.get('fdate'),
            "todate": request.GET.get('tdate'),
            "busstationid": request.GET.get('id'),

        })

    headers = {
        'Content-Type': 'text/plain'
    }
    response = requests.request("GET", url, headers=headers, data=payload)
    if response.status_code == 200:
        response = response.json()
        # daywisesaleslist = data['daywisesaleswarehouselist']
        return JsonResponse({'response': response})
    elif response.status_code == 400:
        data = response.json()
        messages.error(request, data['message'])
        return render(request, 'login1.html')
    elif response.status_code == 503:
        response = response.json()
        return JsonResponse({'response': response})

def region_items(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    accesskey = request.session['accesskey']

    url = "http://13.235.112.1/ziva/mobile-api/region-itemwise-report.php"

    payload = json.dumps(
        {
            "accesskey": accesskey,
            "fromdate": request.GET.get('fdate'),
            "todate": request.GET.get('tdate'),
            "regionid": request.GET.get('id'),

        })

    headers = {
        'Content-Type': 'text/plain'
    }
    response = requests.request("GET", url, headers=headers, data=payload)
    if response.status_code == 200:
        response = response.json()
        return JsonResponse({'response': response})
    elif response.status_code == 400:
        data = response.json()
        messages.error(request, data['message'])
        return render(request, 'login1.html')
    if response.status_code == 503:
        response = response.json()
        return JsonResponse({'response': response})
def depo_items(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    accesskey = request.session['accesskey']

    url = "http://13.235.112.1/ziva/mobile-api/depo-itemwise-report.php"

    payload = json.dumps(
        {
            "accesskey": accesskey,
            "fromdate": request.GET.get('fdate'),
            "todate": request.GET.get('tdate'),
            "depoid": request.GET.get('id'),

        })

    headers = {
        'Content-Type': 'text/plain'
    }
    response = requests.request("GET", url, headers=headers, data=payload)
    if response.status_code == 200:
        response = response.json()
        return JsonResponse({'response': response})
    elif response.status_code == 400:
        data = response.json()
        messages.error(request, data['message'])
        return render(request, 'login1.html')
    elif response.status_code == 503:
        response = response.json()
        return JsonResponse({'response': response})

def region_payment(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    accesskey = request.session['accesskey']


    url = "http://13.235.112.1/ziva/mobile-api/regionwise-total-report.php"

    payload = json.dumps(
                    {
                        "accesskey": accesskey,
                        "fromdate": request.GET.get('fdate'),
                        "todate": request.GET.get('tdate'),
                        "warehouseid": request.GET.get('id'),

    })


    headers = {
                'Content-Type': 'text/plain'
        }
    response = requests.request("GET", url, headers=headers, data=payload)
    if response.status_code == 200:
            response = response.json()
            return JsonResponse({'response':response})
    elif response.status_code == 400:
        data = response.json()
        messages.error(request, data['message'])
        return render(request, 'login1.html')
    elif response.status_code == 503:
        response = response.json()
        return JsonResponse({'response': response})
    else:
        data = response.json()
        messages.error(request, data['message'])
        return JsonResponse({'response': response})
def region_payment_new(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    try:
            menuname = request.session['mylist']
            accesskey = request.session['accesskey']
            if request.method == 'POST':
                range = request.POST.get('range')

                url = "http://13.235.112.1/ziva/mobile-api/regionwise-total-report-new.php"

                if range == 'Custom Dates':
                        fdate = request.POST.get('fdate')
                        tdate = request.POST.get('tdate')
                else:
                        fdate = request.POST.get('range')
                        tdate = request.POST.get('range')
                payload = json.dumps(
                    {
                        "accesskey": accesskey,
                        "fromdate": fdate,
                        "todate": tdate,
                        "region_id": request.POST.get('regionid')

                    })

                headers = {
                    'Content-Type': 'text/plain'
                }

                response = requests.request("GET", url, headers=headers, data=payload)
                if response.status_code == 200:
                    data = response.json()
                    data['fdate'] = fdate
                    data['tdate'] = tdate
                    return JsonResponse({"response":data})
                elif response.status_code == 400:
                    data = response.json()
                    messages.error(request, data['message'])
                    return render(request, 'login1.html')
                else:
                    data = response.json()

                    messages.error(request, data['message'])
                    return JsonResponse({"data": data})
    except:
            if response.status_code == 400:
                data = response.json()
                messages.error(request, data['message'])
                return render(request, 'login1.html')
            return render(request, 'Reports/payments.html',{'menuname':menuname})

def bust_payment_new(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    try:
            menuname = request.session['mylist']
            accesskey = request.session['accesskey']
            if request.method == 'POST':
                range = request.POST.get('range')

                url = "http://13.235.112.1/ziva/mobile-api/busstationwise-total-report-new.php"

                if range == 'Custom Dates':
                        fdate = request.POST.get('fdate')
                        tdate = request.POST.get('tdate')
                else:
                        fdate = request.POST.get('range')
                        tdate = request.POST.get('range')
                payload = json.dumps(
                    {
                        "accesskey": accesskey,
                        "fromdate": fdate,
                        "todate": tdate,
                        "busatation_id": request.POST.get('busatationid')

                    })

                headers = {
                    'Content-Type': 'text/plain'
                }

                response = requests.request("GET", url, headers=headers, data=payload)
                if response.status_code == 200:
                    data = response.json()
                    data['fdate'] = fdate
                    data['tdate'] = tdate
                    return JsonResponse({"response":data})
                elif response.status_code == 400:
                    data = response.json()
                    messages.error(request, data['message'])
                    return render(request, 'login1.html')
                else:
                    data = response.json()

                    messages.error(request, data['message'])
                    return JsonResponse({"data": data})
    except:
            if response.status_code == 400:
                data = response.json()
                messages.error(request, data['message'])
                return render(request, 'login1.html')
            return render(request, 'Reports/payments.html',{'menuname':menuname})

def depot_payment_new(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    try:
        menuname = request.session['mylist']
        accesskey = request.session['accesskey']
        if request.method == 'POST':
            range = request.POST.get('range')

            url = "http://13.235.112.1/ziva/mobile-api/depo-total-report-new.php"

            if range == 'Custom Dates':
                fdate = request.POST.get('fdate')
                tdate = request.POST.get('tdate')
            else:
                fdate = request.POST.get('range')
                tdate = request.POST.get('range')
            payload = json.dumps(
                {
                    "accesskey": accesskey,
                    "fromdate": fdate,
                    "todate": tdate,
                    "depoid": request.POST.get('depoid')

                })

            headers = {
                'Content-Type': 'text/plain'
            }

            response = requests.request("GET", url, headers=headers, data=payload)
            if response.status_code == 200:
                data = response.json()
                data['fdate'] = fdate
                data['tdate'] = tdate
                return JsonResponse({"response": data})
            elif response.status_code == 400:
                data = response.json()
                messages.error(request, data['message'])
                return render(request, 'login1.html')
            else:
                data = response.json()

                messages.error(request, data['message'])
                return JsonResponse({"data": data})
    except:
        if response.status_code == 400:
            data = response.json()
            messages.error(request, data['message'])
            return render(request, 'login1.html')
        return render(request, 'Reports/payments.html', {'menuname': menuname})

def bus_payment(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    accesskey = request.session['accesskey']

    url = "http://13.235.112.1/ziva/mobile-api/busstationwise-total-report.php"

    payload = json.dumps(
        {
            "accesskey": accesskey,
            "fromdate": request.GET.get('fdate'),
            "todate": request.GET.get('tdate'),
            "depoid": request.GET.get('id'),

        })

    headers = {
        'Content-Type': 'text/plain'
    }
    response = requests.request("GET", url, headers=headers, data=payload)
    if response.status_code == 200:
        response = response.json()
        return JsonResponse({'response': response})
    elif response.status_code == 503:
        response = response.json()
        return JsonResponse({'response': response})
    elif response.status_code == 400:
        data = response.json()
        if data['message'] == 'Sorry! some details are missing':
            messages.error(request, data['message'])
            return redirect('/internal_consumption')
        else:
            messages.error(request, data['message'])
            return redirect('/login')



def depo_payment(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    accesskey = request.session['accesskey']


    url = "http://13.235.112.1/ziva/mobile-api/depowise-total-report.php"

    payload = json.dumps(
                    {
                        "accesskey": accesskey,
                        "fromdate": request.GET.get('fdate'),
                        "todate": request.GET.get('tdate'),
                        "regionid": request.GET.get('id'),

    })


    headers = {
                'Content-Type': 'text/plain'
        }
    response = requests.request("GET", url, headers=headers, data=payload)
    if response.status_code == 200:
            response = response.json()
            return JsonResponse({'response':response})

    elif response.status_code == 400:
        data = response.json()
        if data['message'] == 'Sorry! some details are missing':
            messages.error(request, data['message'])
            return redirect('/internal_consumption')
        else:
            messages.error(request, data['message'])
            return redirect('/login')
    else:
        response = response.json()
        return JsonResponse({'response': response})

def depot_stock(request,id):
        if 'accesskey' not in request.session:
            messages.error(request, 'Access denied!')
            return redirect('/login')
        try:
            accesskey = request.session['accesskey']
            menuname = request.session['mylist']
            payload = json.dumps({"accesskey": accesskey})
            headers = {
                'Content-Type': 'application/json'
            }
            url = "http://13.235.112.1/ziva/mobile-api/region-list.php"
            response = requests.request("POST", url, headers=headers, data=payload)

            data = response.json()
            regionlist = data['regionlist']

            url = "http://13.235.112.1/ziva/mobile-api/warehousemaster-list.php"
            payload = json.dumps({"accesskey": accesskey})
            headers = {
                'Content-Type': 'text/plain'
            }
            response = requests.request("GET", url, headers=headers, data=payload)
            data = response.json()
            wh_masterlist = data['warehouselist']

            url = "http://13.235.112.1/ziva/mobile-api/depo-list.php"

            payload = json.dumps({"accesskey": accesskey,
                                  "warehouseid": request.POST.get('warehouseid'),
                                  "regionid": request.POST.get('regionid')})

            headers = {
                'Content-Type': 'text/plain'
            }
            response = requests.request("GET", url, headers=headers, data=payload)

            data = response.json()
            depolist = data['depolist']

            url = "http://13.235.112.1/ziva/mobile-api/bus-list.php"
            payload = json.dumps({
                "accesskey": accesskey
            })
            headers = {
                'Content-Type': 'application/json'
            }

            response = requests.request("GET", url, headers=headers, data=payload)

            data = response.json()
            bus = data['buslist']

            url = "http://13.235.112.1/ziva/mobile-api/regionwise-report.php"
            payload = json.dumps({
                "accesskey": accesskey,"regionid":id
            })
            headers = {
                'Content-Type': 'application/json'
            }

            response = requests.request("GET", url, headers=headers, data=payload)
            if response.status_code == 200:
                data = response.json()
                item_quantities = data['regioninventorylist']
                return render(request, 'Reports/depo_stockreport.html',
                              {"regionlist":regionlist,'bus':bus,'depolist':depolist,"wh_masterlist":wh_masterlist,"menuname": menuname,'item_quantities': item_quantities})
            elif response.status_code == 500:
                messages.error(request,'Internal server  error')
                return render(request, 'Reports/depo_stockreport.html',
                              {"regionlist": regionlist, 'bus': bus, 'depolist': depolist,
                               "wh_masterlist": wh_masterlist, "menuname": menuname})
            else:
                data = response.json()
                messages.error(request, data['message'])
                return render(request, 'Reports/depo_stockreport.html',
                              {"regionlist": regionlist, 'bus': bus, 'depolist': depolist,
                               "wh_masterlist": wh_masterlist, "menuname": menuname})
        except:
            if response.status_code == 400:
                data = response.json()
                messages.error(request, data['message'])
                return render(request, 'login1.html')
        return render(request, 'Reports/depo_stockreport.html',{'menuname':menuname})


def depot_stock_new(request, id):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    try:
        accesskey = request.session['accesskey']
        menuname = request.session['mylist']
        payload = json.dumps({"accesskey": accesskey})
        headers = {
            'Content-Type': 'application/json'
        }
        url = "http://13.235.112.1/ziva/mobile-api/region-list.php"
        response = requests.request("POST", url, headers=headers, data=payload)

        data = response.json()
        regionlist = data['regionlist']

        url = "http://13.235.112.1/ziva/mobile-api/warehousemaster-list.php"
        payload = json.dumps({"accesskey": accesskey})
        headers = {
            'Content-Type': 'text/plain'
        }
        response = requests.request("GET", url, headers=headers, data=payload)
        data = response.json()
        wh_masterlist = data['warehouselist']

        url = "http://13.235.112.1/ziva/mobile-api/depo-list.php"

        payload = json.dumps({"accesskey": accesskey,
                              "warehouseid": request.POST.get('warehouseid'),
                              "regionid": request.POST.get('regionid')})

        headers = {
            'Content-Type': 'text/plain'
        }
        response = requests.request("GET", url, headers=headers, data=payload)

        data = response.json()
        depolist = data['depolist']

        url = "http://13.235.112.1/ziva/mobile-api/bus-list.php"
        payload = json.dumps({
            "accesskey": accesskey
        })
        headers = {
            'Content-Type': 'application/json'
        }

        response = requests.request("GET", url, headers=headers, data=payload)

        data = response.json()
        bus = data['buslist']
        url = "http://13.235.112.1/ziva/mobile-api/depo-inventory-report.php"
        payload = json.dumps({
            "accesskey": accesskey, "depoid": id
        })
        headers = {
            'Content-Type': 'application/json'
        }

        response = requests.request("GET", url, headers=headers, data=payload)
        if response.status_code == 200:
            data = response.json()
            item_quantities = data['depoinventorylist']
            return render(request, 'Reports/depo_stockreport.html',
                          {"regionlist": regionlist, 'bus': bus, 'depolist': depolist, "wh_masterlist": wh_masterlist,
                           "menuname": menuname, 'item_quantities': item_quantities})
        elif response.status_code == 500:
            messages.error(request, 'Internal server  error')
            return render(request, 'Reports/depo_stockreport.html',
                          {"regionlist": regionlist, 'bus': bus, 'depolist': depolist,
                           "wh_masterlist": wh_masterlist, "menuname": menuname})
        else:
            data = response.json()
            messages.error(request, data['message'])
            return render(request, 'Reports/depo_stockreport.html',
                          {"regionlist": regionlist, 'bus': bus, 'depolist': depolist,
                           "wh_masterlist": wh_masterlist, "menuname": menuname})

    except:
        if response.status_code == 400:
            data = response.json()
            messages.error(request, data['message'])
            return render(request, 'login1.html')
    return render(request, 'Reports/depo_stockreport.html',{'menuname':menuname})


def depot_indent_report(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    try:
        menuname = request.session['mylist']
        accesskey = request.session['accesskey']

        url = "http://13.235.112.1/ziva/mobile-api/warehousemaster-list.php"

        payload = json.dumps({"accesskey": accesskey})
        headers = {
            'Content-Type': 'text/plain'
        }
        response = requests.request("GET", url, headers=headers, data=payload)

        data = response.json()
        wh_masterlist = data['warehouselist']

        url = "http://13.235.112.1/ziva/mobile-api/dates-filter.php"

        payload = json.dumps({"accesskey": accesskey})
        headers = {
            'Content-Type': 'text/plain'
        }
        response = requests.request("GET", url, headers=headers, data=payload)

        data = response.json()
        selectrange = data['timingslist']
        if request.method == 'POST':
            menuname = request.session['mylist']
            accesskey = request.session['accesskey']

            range = request.POST.get('from')
            if range:
                if range == 'Custom Dates':
                    fdate = request.POST.get('fdate')
                    tdate = request.POST.get('ldate')
                else:
                    fdate = request.POST.get('from')
                    tdate = request.POST.get('from')
            else:
                fdate = "Current Month"
                tdate = "Current Month"

            url = "http://13.235.112.1/ziva/mobile-api/depowise-qty-accepted-report.php"

            payload = json.dumps({
                "accesskey": accesskey,
                "fromdate": fdate,
                "todate":tdate,
                "depot_id": request.POST.get('depoid1'),
                "region_id": request.POST.get('regionid1'),
                "warehouse_id": request.POST.get('warehouseid1')
            })


            headers = {
                'Content-Type': 'text/plain'
            }
            response = requests.request("GET", url, headers=headers, data=payload)
            if response.status_code == 200:
                data = response.json()
                depowiseqty_list = data['depowiseqty_list']
                return render(request, 'Reports/depotwise_indent.html',
                              {'menuname': menuname, 'entry': depowiseqty_list, 'wh_masterlist': wh_masterlist,
                               'selectrange': selectrange})
            elif response.status_code == 503:
                data = response.json()
                messages.error(request, data['message'])
                return render(request, 'Reports/depotwise_indent.html',
                              {'wh_masterlist': wh_masterlist, 'selectrange': selectrange,'menuname':menuname})
            else:
                return render(request, 'Reports/depotwise_indent.html',
                              {'wh_masterlist': wh_masterlist, 'selectrange': selectrange, 'menuname': menuname})
        else:
            url = "http://13.235.112.1/ziva/mobile-api/depowise-qty-accepted-report.php"


            headers = {
                'Content-Type': 'text/plain'
            }

            payload = json.dumps({
                "accesskey": accesskey,
                "fromdate": "Current Month",
                "todate": "Current Month",
                "depot_id": "All",
                "region_id": "All",
                "warehouse_id": "All"
            })

            response = requests.request("GET", url, headers=headers, data=payload)

            if response.status_code == 200:
                data = response.json()
                depowiseqty_list = data['depowiseqty_list']
                return render(request, 'Reports/depotwise_indent.html',
                              {'menuname': menuname, 'entry': depowiseqty_list, 'wh_masterlist': wh_masterlist,
                               'selectrange': selectrange})
            elif response.status_code == 503:
                data = response.json()
                messages.error(request, data['message'])
                return render(request, 'Reports/depotwise_indent.html',
                              {'menuname': menuname,  'wh_masterlist': wh_masterlist,
                               'selectrange': selectrange})
            else:
                return render(request, 'Reports/depotwise_indent.html',
                              {'menuname': menuname,'wh_masterlist': wh_masterlist,
                               'selectrange': selectrange})
    except:
        if response.status_code == 400:
            data = response.json()
            messages.error(request, data['message'])
            return render(request, 'login1.html')
    return render(request, 'Reports/depotwise_indent.html',{'menuname': menuname})
def depot_qtyissued1(request):
    pass

def depot_qtyissued(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    try:
        menuname = request.session['mylist']
        accesskey = request.session['accesskey']
        url = "http://13.235.112.1/ziva/mobile-api/dates-filter.php"

        payload = json.dumps({"accesskey": accesskey})
        headers = {
            'Content-Type': 'text/plain'
        }
        response = requests.request("GET", url, headers=headers, data=payload)

        data = response.json()
        selectrange = data['timingslist']
        url = "http://13.235.112.1/ziva/mobile-api/warehousemaster-list.php"

        payload = json.dumps({"accesskey": accesskey})
        headers = {
            'Content-Type': 'text/plain'
        }
        response = requests.request("GET", url, headers=headers, data=payload)

        data = response.json()
        wh_masterlist = data['warehouselist']

        if request.method == 'POST':
            option = request.POST.get('from')
            warehouseid1 = request.POST.get('warehousename1')
            regionname1 = request.POST.get('regionname1')
            deponame1 = request.POST.get('deponame1')
            where = [
                'indent_item.indent_no = outpass_item.indent_no',
                'indent_item.indent_no = generate_indent.indent_no',
                'depo_master.depoid =generate_indent.to_id',
            ]

            if option == 'Today':
                tdate = datetime.date.today()
                where.append(f"DATE_FORMAT(indent_item.createdon, '%%Y-%%m-%%d') = '{tdate}'")
            elif option == 'Yesterday':
                Previous_Date = datetime.datetime.today() - datetime.timedelta(days=1)
                Previous_Date = Previous_Date.date()
                where.append(f"DATE(indent_item.createdon) = '{Previous_Date}'")
            elif option == 'Current Month':
                current_month = datetime.date.today().month
                where.append(f"MONTH(indent_item.createdon) = '{current_month}'")
            elif option == 'Current Week':
                today = datetime.date.today()
                current_week = today.isocalendar().week
                where.append(f"WEEK(indent_item.createdon) = '{current_week}'")
            elif option == 'Last 7 days':
                current_date = datetime.date.today()
                start_date = current_date - timedelta(days=current_date.weekday() + 7)
                end_date = current_date - timedelta(days=current_date.weekday() + 1)
                where.append("indent_item.createdon >= '%s' AND indent_item.createdon <= '%s'" % (start_date, end_date))
            elif option == 'Custom Dates':
                fdate = request.POST.get('fdate')
                ldate = request.POST.get('ldate')
                where.append("indent_item.createdon >= '%s' AND indent_item.createdon <= '%s'" % (fdate, ldate))
            elif option == '':
                where.append(f"DATE_FORMAT(indent_item.createdon, '%%Y-%%m-%%d')")
            if warehouseid1 != '' and warehouseid1 != 'All':
                where.append(f"depo_master.warehouse = '{warehouseid1}'")
            if deponame1 != '' and deponame1 != 'All':
                where.append(f"depo_master.deponame = '{deponame1}'")
            if regionname1 != '' and regionname1 != 'All':
                where.append(f"depo_master.regionname = '{regionname1}'")

            queryset = IndentItem.objects.using('auth').extra(
                tables=['outpass_item', 'generate_indent', 'depo_master'],
                where=where,
                select={
                    'indent_item_indent_no': 'indent_item.indent_no',
                    'indent_item_item_name': 'indent_item.item_name',
                    'indent_item_createdon': "DATE_FORMAT(indent_item.createdon, '%%d-%%b-%%Y')",
                    'indent_item_qty': 'indent_item.qty',
                    'depo_master_deponame': 'depo_master.deponame',
                    'depo_master_regionname': 'depo_master.regionname',
                    'outpass_item_qty': 'outpass_item.qty',
                    'depo_master_warehouse': 'depo_master.warehouse',
                    'generate_indent_fromname':'generate_indent.from_name',

                }
            ).values(
                'indent_item_indent_no', 'indent_item_item_name', 'indent_item_createdon',
                'depo_master_deponame', 'depo_master_regionname',
                'indent_item_qty', 'outpass_item_qty', 'depo_master_warehouse','generate_indent_fromname'
            )
            where = [
                'indent_item.indent_no = outpass_item.indent_no',

                'indent_item.indent_no = generate_indent.indent_no',
                'depo_master.depoid =generate_indent.to_id',

            ]
            if option == 'Today':
                tdate = datetime.date.today()
                where.append(f"DATE_FORMAT(indent_item.createdon, '%%Y-%%m-%%d') = '{tdate}'")
            elif option == 'Yesterday':
                Previous_Date = datetime.datetime.today() - datetime.timedelta(days=1)
                Previous_Date = Previous_Date.date()
                where.append(f"DATE(indent_item.createdon) = '{Previous_Date}'")
            elif option == 'Current Month':
                current_month = datetime.date.today().month
                where.append(f"MONTH(indent_item.createdon) = '{current_month}'")
            elif option == 'Current Week':
                today = datetime.date.today()
                current_week = today.isocalendar().week
                where.append(f"WEEK(indent_item.createdon) = '{current_week}'")
            elif option == 'Last 7 days':
                current_date = datetime.date.today()
                start_date = current_date - timedelta(days=current_date.weekday() + 7)
                end_date = current_date - timedelta(days=current_date.weekday() + 1)
                where.append("indent_item.createdon >= '%s' AND indent_item.createdon <= '%s'" % (start_date, end_date))
            elif option == 'Custom Dates':
                fdate = request.POST.get('fdate')
                ldate = request.POST.get('ldate')
                where.append("indent_item.createdon >= '%s' AND indent_item.createdon <= '%s'" % (fdate, ldate))
            elif option == '':
                where.append(f"DATE_FORMAT(indent_item.createdon, '%%Y-%%m-%%d')")
            if warehouseid1 != '' and warehouseid1 != 'All':
                where.append(f"depo_master.warehouse = '{warehouseid1}'")
            if deponame1 != '' and deponame1 != 'All':
                where.append(f"depo_master.deponame = '{deponame1}'")
            if regionname1 != '' and regionname1 != 'All':
                where.append(f"depo_master.regionname = '{regionname1}'")


            queryset2 = OutpassItem.objects.using('auth').extra(
                tables=['indent_item', 'depo_master', 'generate_indent'],
                where=where,
                select={
                    'indent_item_item_name': 'indent_item.item_name',
                    'indent_item_createdon': "DATE_FORMAT(indent_item.createdon, '%%d-%%b-%%Y')",
                    'outpass_item_qty': 'outpass_item.qty',


                }
            ).values('outpass_item_qty', 'indent_item_item_name', 'indent_item_createdon')
            if queryset and queryset2:
                outpass_sum = queryset2.values('indent_item_createdon', 'indent_item_item_name').annotate(
                    outpass_sum_item=Sum(Case(When(qty__isnull=False, then=F('qty')))),
                )
                queryset1 = queryset.values('indent_item_createdon', 'indent_item_item_name').annotate(
                    indent_sum_item=Sum(Case(When(qty__isnull=False, then=F('qty')))),
                )
                merged_data = []
                for data1 in queryset1:
                    for data2 in outpass_sum:
                        if data1['indent_item_createdon'] == data2['indent_item_createdon'] \
                                and data1['indent_item_item_name'] == data2['indent_item_item_name']:
                            merged_data.append({
                                'indent_item_createdon': data1['indent_item_createdon'],
                                'indent_item_item_name': data1['indent_item_item_name'],
                                'outpass_sum_item': data2['outpass_sum_item'],
                                'indent_sum_item': data1['indent_sum_item'],

                            })
                            break
                result = []
                for data1 in merged_data:
                    for data2 in queryset:
                        if data1['indent_item_createdon'] == data2['indent_item_createdon'] \
                                and data1['indent_item_item_name'] == data2['indent_item_item_name']:
                            result.append({
                                'indent_item_createdon': data1['indent_item_createdon'],
                                'indent_item_item_name': data1['indent_item_item_name'],
                                'outpass_sum_item': data1['outpass_sum_item'],
                                'indent_sum_item': data1['indent_sum_item'],
                                'depo_master_deponame': data2['depo_master_deponame'],
                                'depo_master_regionname': data2['depo_master_regionname'],
                                'indent_item_indent_no': data2['indent_item_indent_no'],
                                'depo_master_warehouse': data2['depo_master_warehouse'],
                                'generate_indent_fromname': data2['generate_indent_fromname']
                            })
                            break

                result = sorted(result, key=lambda x: datetime.datetime.strptime(x['indent_item_createdon'], '%d-%b-%Y'),
                                     reverse=True)

                return render(request, 'Reports/depot_qtyissued.html',
                              {'entry': result, 'wh_masterlist': wh_masterlist, 'selectrange': selectrange,'menuname':menuname})
            else:
                return render(request, 'Reports/depot_qtyissued.html',
                              {'wh_masterlist': wh_masterlist, 'selectrange': selectrange,
                               'menuname': menuname})
        else:
            queryset = IndentItem.objects.using('auth').extra(
                tables=['outpass_item', 'generate_indent', 'depo_master'],
                where=[
                    'indent_item.indent_no = outpass_item.indent_no',
                    'indent_item.indent_no = generate_indent.indent_no',
                    'depo_master.depoid = generate_indent.to_id',
                ],
                select={
                    'generate_indent_to_name': 'generate_indent.to_name',
                    'generate_indent_fromname': 'generate_indent.from_name',
                    'indent_item_indent_no': 'indent_item.indent_no',
                    'indent_item_item_name': 'indent_item.item_name',
                    'indent_item_createdon': "DATE_FORMAT(indent_item.createdon, '%%d-%%b-%%Y')",
                    # Extract the date portion only
                    'indent_item_qty': 'indent_item.qty',
                    'depo_master_deponame': 'depo_master.deponame',
                    'depo_master_warehouse': 'depo_master.warehouse',
                    'depo_master_regionname': 'depo_master.regionname',
                }
            ).values('indent_item_indent_no', 'indent_item_item_name', 'indent_item_createdon', 'generate_indent_to_name',
                     'depo_master_deponame', 'depo_master_regionname', 'indent_item_qty', 'depo_master_warehouse','generate_indent_fromname')
            queryset2 = OutpassItem.objects.using('auth').extra(
                tables=['indent_item', 'generate_indent', 'depo_master'],
                where=[
                    'indent_item.indent_no = outpass_item.indent_no',
                    'indent_item.indent_no = generate_indent.indent_no',
                    'depo_master.depoid =generate_indent.to_id',

                ],
                select={

                    'indent_item_item_name': 'indent_item.item_name',
                    'indent_item_createdon': "DATE_FORMAT(indent_item.createdon, '%%d-%%b-%%Y')",
                    'outpass_item_qty': 'outpass_item.qty',
                    'indent_item_indent_no': 'indent_item.indent_no',
                }
            ).values('outpass_item_qty', 'indent_item_item_name', 'indent_item_createdon', 'indent_item_indent_no')
            if queryset and queryset2:
                outpass_sum = queryset2.values('indent_item_createdon', 'indent_item_item_name').annotate(
                    outpass_sum_item=Sum(Case(When(qty__isnull=False, then=F('qty')))),
                )
                queryset1 = queryset.values('indent_item_createdon', 'indent_item_item_name').annotate(
                    indent_sum_item=Sum(Case(When(qty__isnull=False, then=F('qty')))),
                )
                merged_data = []
                for data1 in queryset1:
                    for data2 in outpass_sum:
                        if data1['indent_item_createdon'] == data2['indent_item_createdon'] \
                                and data1['indent_item_item_name'] == data2['indent_item_item_name']:
                            merged_data.append({
                                'indent_item_createdon': data1['indent_item_createdon'],
                                'indent_item_item_name': data1['indent_item_item_name'],
                                'outpass_sum_item': data2['outpass_sum_item'],
                                'indent_sum_item': data1['indent_sum_item'],
                            })
                            break
                result = []
                for data1 in merged_data:
                    for data2 in queryset:
                        if data1['indent_item_createdon'] == data2['indent_item_createdon'] \
                                and data1['indent_item_item_name'] == data2['indent_item_item_name']:
                            result.append({
                                'indent_item_createdon': data1['indent_item_createdon'],
                                'indent_item_item_name': data1['indent_item_item_name'],
                                'outpass_sum_item': data1['outpass_sum_item'],
                                'indent_sum_item': data1['indent_sum_item'],
                                'depo_master_deponame': data2['depo_master_deponame'],
                                'depo_master_regionname': data2['depo_master_regionname'],
                                'indent_item_indent_no': data2['indent_item_indent_no'],
                                'depo_master_warehouse': data2['depo_master_warehouse'],
                                'generate_indent_fromname':data2['generate_indent_fromname']
                            })
                            break
                result = sorted(result, key=lambda x: datetime.datetime.strptime(x['indent_item_createdon'], '%d-%b-%Y'),
                                reverse=True)
                return render(request, 'Reports/depot_qtyissued.html',
                              {'entry': result, 'wh_masterlist': wh_masterlist, 'selectrange': selectrange,'menuname':menuname})
            else:
                return render(request, 'Reports/depot_qtyissued.html',
                              {'wh_masterlist': wh_masterlist, 'selectrange': selectrange,
                               'menuname': menuname})
    except:
        if response.status_code == 400:
            data = response.json()
            messages.error(request, data['message'])
            return render(request, 'login1.html')
    return render(request, 'Reports/depot_qtyissued.html',{'menuname':menuname})



def Vendor_itemsply(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    try:
        accesskey = request.session['accesskey']
        menuname = request.session['mylist']
        url = "http://13.235.112.1/ziva/mobile-api/dates-filter.php"

        payload = json.dumps({"accesskey": accesskey})
        headers = {
            'Content-Type': 'text/plain'
        }
        response = requests.request("GET", url, headers=headers, data=payload)
        data = response.json()
        selectrange = data['timingslist']
        url = "http://13.235.112.1/ziva/mobile-api/warehousemaster-list.php"

        payload = json.dumps({"accesskey": accesskey})
        headers = {
            'Content-Type': 'text/plain'
        }
        response = requests.request("GET", url, headers=headers, data=payload)

        data = response.json()
        wh_masterlist = data['warehouselist']

        url = "http://13.235.112.1/ziva/mobile-api/vendormasterlist.php"

        payload = json.dumps({"accesskey": accesskey})
        headers = {
            'Content-Type': 'application/json'
        }

        response = requests.request("GET", url, headers=headers, data=payload)
        data1 = response.json()
        vendor_masterlist = data1['vendormasterlist']

        if request.method == 'POST':
            option = request.POST.get('from')
            warehouseid1= request.POST.get('warehouseid1')
            vendorid =  request.POST.get('vendorname')
            where = [
                'grn.grn = grn_item.grn',
                'grn.warehouse_id = warehouse_master.warehouseid',
                "grn.status = 'Verified'"
            ]
            if warehouseid1:
                where.append( f"grn.warehouse_id = '{warehouseid1}'")
            if vendorid:
                where.append(f"grn.vendorname = '{vendorid}'")
            if option == 'All':
                where.append(f"DATE_FORMAT(grn.created_on,'%%Y-%%m-%%d')")
            if option == 'Today':
                today = datetime.date.today()
                where.append(f"DATE_FORMAT(grn.created_on, '%%Y-%%m-%%d') = '{today}'")
            elif option == 'Current Month':
                today = datetime.date.today().month
                where.append("MONTH(grn.created_on) = %s" % today)
            elif option == 'Current Week':
                today = datetime.date.today()
                current_week = today.isocalendar().week
                where.append(f"WEEK(grn.created_on, '%%Y-%%m-%%d') = '{current_week}'")
            elif option == 'Last 7 days':
                current_date = datetime.date.today()
                start_date = current_date - timedelta(days=current_date.weekday() + 7)
                end_date = current_date - timedelta(days=current_date.weekday() + 1)
                where.append("grn.created_on >= '%s' AND grn.created_on <= '%s'" % (start_date, end_date))
            elif option == 'Custom Dates':
                fdate = request.POST.get('fdate')
                ldate = request.POST.get('ldate')
                where.append("grn.created_on >= '%s' AND grn.created_on <= '%s'" % (fdate, ldate))
            elif option == 'Yesterday':
                Previous_Date = datetime.datetime.today() - datetime.timedelta(days=1)
                formatted_date = Previous_Date.date().strftime('%Y-%m-%d')
                where.append(f"DATE_FORMAT(grn.created_on, '%%Y-%%m-%%d') = '{formatted_date}'")

            queryset = GrnItem.objects.using('auth').extra(
                tables=['grn', 'grn_item', 'warehouse_master'],
                where=where,
                select={
                    'grn_grn': 'grn.grn',
                    'grn_warehouse_id': 'grn.warehouse_id',
                    'grn_vendorname': 'grn.vendorname',
                    'grn_item_created_on': "DATE_FORMAT(grn.created_on, '%%d-%%b-%%Y')",
                    'grn_item_item_name': 'grn_item.item_name',
                    'grn_item_quantity': 'CAST(grn_item.quantity AS CHAR)',
                    'warehouse_master_warehousename': 'warehouse_master.warehousename',
                }
            ).values(
                'grn_warehouse_id', 'grn_grn', 'grn_vendorname',
                'grn_item_created_on', 'grn_item_item_name', 'grn_item_quantity', 'warehouse_master_warehousename',
            )

            queryset2 = queryset.values('grn_vendorname', 'warehouse_master_warehousename', 'grn_item_created_on',
                                        'grn_item_item_name')
            queryset1 = queryset.values('grn_item_created_on','grn_vendorname','warehouse_master_warehousename', 'grn_item_item_name').annotate(
                total_quantity=Cast(Sum('quantity'), CharField()))
            grouped_data = groupby(queryset1, key=lambda x: (x['grn_item_created_on'], x['grn_vendorname']))
            merged_data = []

            for (date, vendor), group in grouped_data:
                merged_dict = {
                    'grn_item_created_on': date,
                    'grn_vendorname': vendor,
                    'items': []
                }

                for item in group:
                    merged_dict['warehouse_master_warehousename'] = item['warehouse_master_warehousename']
                    merged_dict['items'].append({
                        'itemname': item['grn_item_item_name'],
                        'quantity': item['total_quantity']
                    })

                merged_data.append(merged_dict)
                merged_data = sorted(merged_data,
                                     key=lambda x: datetime.datetime.strptime(x['grn_item_created_on'], '%d-%b-%Y'),
                                     reverse=True)
            return render(request, 'Reports/vendor_itemsupply.html', {"vendor_masterlist":vendor_masterlist,"wh_masterlist":wh_masterlist,"entry": merged_data,'menuname':menuname,'selectrange':selectrange})

        else:
            queryset = GrnItem.objects.using('auth').extra(
                tables=['grn', 'grn_item', 'warehouse_master'],
                where=[
                    'grn.grn = grn_item.grn',
                    'grn.warehouse_id = warehouse_master.warehouseid',
                    "grn.status = 'Verified'"
                ],
                select={
                    'grn_grn': 'grn.grn',
                    'grn_warehouse_id': 'grn.warehouse_id',
                    'grn_vendorname': 'grn.vendorname',
                    'grn_item_created_on': "DATE_FORMAT(grn.created_on, '%%d-%%b-%%Y')",
                    'grn_item_item_name': 'grn_item.item_name',
                    'grn_item_quantity': 'CAST(grn_item.quantity AS CHAR)',
                    'warehouse_master_warehousename': 'warehouse_master.warehousename',
                    'grn_status':'grn.status'
                }

            ).values(
                'grn_warehouse_id', 'grn_grn', 'grn_vendorname',
                'grn_item_created_on', 'grn_item_item_name', 'grn_item_quantity', 'warehouse_master_warehousename'
            )

            queryset2 = queryset.values('grn_vendorname', 'warehouse_master_warehousename', 'grn_item_created_on','grn_item_item_name')
            queryset1 = queryset.values('grn_item_created_on', 'grn_vendorname','warehouse_master_warehousename','grn_item_item_name').annotate(
                total_quantity=Cast(Sum('quantity'), CharField()))
            grouped_data = groupby(queryset1, key=lambda x: (x['grn_item_created_on'], x['grn_vendorname']))
            merged_data = []

            for (date, vendor), group in grouped_data:
                merged_dict = {
                    'grn_item_created_on': date,
                    'grn_vendorname': vendor,
                    'items': []
                }

                for item in group:
                    merged_dict['warehouse_master_warehousename'] = item['warehouse_master_warehousename']
                    merged_dict['items'].append({
                        'itemname': item['grn_item_item_name'],
                        'quantity': item['total_quantity']
                    })

                merged_data.append(merged_dict)
                merged_data = sorted(merged_data,
                                     key=lambda x: datetime.datetime.strptime(x['grn_item_created_on'], '%d-%b-%Y'),
                                     reverse=True)
            return render(request,'Reports/vendor_itemsupply.html',{"vendor_masterlist":vendor_masterlist,"wh_masterlist":wh_masterlist,"entry":merged_data,'menuname':menuname,'selectrange':selectrange})
    except:
        if response.status_code == 400:
            data = response.json()
            messages.error(request, data['message'])
            return render(request, 'login1.html')
    return render(request, 'Reports/vendor_itemsupply.html',{"menuname":menuname})

def busstation_stalls(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    accesskey = request.session['accesskey']
    payload = json.dumps(
        {

            "accesskey": accesskey,
            "warehouseid": "All",
            "regionid": "All",
            "depoid": "All",
            "busstationid": "All",
            "fromdate": "Current Month",
            "todate": "Current Month"

        })

    headers = {
        'Content-Type': 'text/plain'
    }
    url = "http://13.235.112.1/ziva/mobile-api/daywise-sales-report.php"
    response = requests.request("GET", url, headers=headers, data=payload)
    data = response.json()
    data = data['daywisesaleslist']
    item_count = Sales.objects.using('auth').values('created_on', 'from_name').annotate(total_items=Count('item_count'))
    # Get stall count for all dates and bus stations
    stall_count = Sales.objects.using('auth').values('created_on', 'from_name', 'from_id').distinct().annotate(
        total_stalls=Count('from_id'))

    return HttpResponse({'data':data})

def busstation_stock(request,id):
        if 'accesskey' not in request.session:
            messages.error(request, 'Access denied!')
            return redirect('/login')

        try:
            menuname = request.session['mylist']
            accesskey = request.session['accesskey']

            payload = json.dumps({"accesskey": accesskey})
            headers = {
                'Content-Type': 'application/json'
            }
            url = "http://13.235.112.1/ziva/mobile-api/region-list.php"
            response = requests.request("POST", url, headers=headers, data=payload)

            data = response.json()
            regionlist = data['regionlist']

            url = "http://13.235.112.1/ziva/mobile-api/warehousemaster-list.php"
            payload = json.dumps({"accesskey": accesskey})
            headers = {
                'Content-Type': 'text/plain'
            }
            response = requests.request("GET", url, headers=headers, data=payload)
            data = response.json()
            wh_masterlist = data['warehouselist']

            url = "http://13.235.112.1/ziva/mobile-api/depo-list.php"

            payload = json.dumps({"accesskey": accesskey,
                                  "warehouseid": request.POST.get('warehouseid'),
                                  "regionid": request.POST.get('regionid')})

            headers = {
                'Content-Type': 'text/plain'
            }
            response = requests.request("GET", url, headers=headers, data=payload)

            data = response.json()
            depolist = data['depolist']

            url = "http://13.235.112.1/ziva/mobile-api/bus-list.php"
            payload = json.dumps({
                "accesskey": accesskey
            })
            headers = {
                'Content-Type': 'application/json'
            }

            response = requests.request("GET", url, headers=headers, data=payload)

            data = response.json()
            buslist = data['buslist']

            url = "http://13.235.112.1/ziva/mobile-api/depowise-inventory-report.php"
            payload = json.dumps({
                "accesskey": accesskey,"depoid":id
            })
            headers = {
                'Content-Type': 'application/json'
            }

            response = requests.request("GET", url, headers=headers, data=payload)
            if response.status_code == 200:
                data = response.json()
                item_quantities = data['list']
                return render(request, 'Reports/busstation_stock.html',
                              {"regionlist": regionlist, 'bus': buslist, 'depolist': depolist, "menuname": menuname,
                               'wh_masterlist': wh_masterlist, 'item_quantities': item_quantities})
            elif response.status_code == 500:
                messages.error(request,'Internal server error')
                return render(request, 'Reports/busstation_stock.html',
                              {"regionlist": regionlist, 'bus': buslist, 'depolist': depolist, "menuname": menuname,
                               'wh_masterlist': wh_masterlist})
            else:
                data = response.json()
                messages.error(request,data['message'])
                return render(request, 'Reports/busstation_stock.html',
                              {"regionlist": regionlist, 'bus': buslist, 'depolist': depolist, "menuname": menuname,
                               'wh_masterlist': wh_masterlist})
        except:
            if response.status_code == 400:
                data = response.json()
                messages.error(request, data['message'])
                return render(request, 'login1.html')
        return render(request, 'Reports/busstation_stock.html',{'menuname':menuname})

def busstation_stock1(request,id):
    if 'accesskey' not in request.session:
            messages.error(request, 'Access denied!')
            return redirect('/login')
    try:
            menuname = request.session['mylist']
            accesskey = request.session['accesskey']

            payload = json.dumps({"accesskey": accesskey})
            headers = {
                'Content-Type': 'application/json'
            }
            url = "http://13.235.112.1/ziva/mobile-api/region-list.php"
            response = requests.request("POST", url, headers=headers, data=payload)

            data = response.json()
            regionlist = data['regionlist']

            url = "http://13.235.112.1/ziva/mobile-api/warehousemaster-list.php"
            payload = json.dumps({"accesskey": accesskey})
            headers = {
                'Content-Type': 'text/plain'
            }
            response = requests.request("GET", url, headers=headers, data=payload)
            data = response.json()
            wh_masterlist = data['warehouselist']

            url = "http://13.235.112.1/ziva/mobile-api/depo-list.php"

            payload = json.dumps({"accesskey": accesskey,
                                  "warehouseid": request.POST.get('warehouseid'),
                                  "regionid": request.POST.get('regionid')})

            headers = {
                'Content-Type': 'text/plain'
            }
            response = requests.request("GET", url, headers=headers, data=payload)

            data = response.json()
            depolist = data['depolist']

            url = "http://13.235.112.1/ziva/mobile-api/bus-list.php"
            payload = json.dumps({
                "accesskey": accesskey
            })
            headers = {
                'Content-Type': 'application/json'
            }

            response = requests.request("GET", url, headers=headers, data=payload)

            data = response.json()
            buslist = data['buslist']
            url = "http://13.235.112.1/ziva/mobile-api/busstation-inventory-report.php"

            payload = json.dumps({"accesskey": accesskey, "busatation_id": id})
            headers = {
                'Content-Type': 'text/plain'
            }
            response = requests.request("GET", url, headers=headers, data=payload)
            if response.status_code == 200:
                data = response.json()
                busdata = data['busstationinventorylist']
                return render(request, 'Reports/busstation_stock.html',
                              {"regionlist": regionlist, 'bus': buslist, 'depolist': depolist, "menuname": menuname,
                               'wh_masterlist': wh_masterlist,'item_quantities':busdata})

            elif response.status_code == 500:
                messages.error(request, 'Internal server  error')
                return render(request, 'Reports/busstation_stock.html',
                              {"regionlist": regionlist, 'bus': buslist, 'depolist': depolist, "menuname": menuname,
                               'wh_masterlist': wh_masterlist})

            else:
                data = response.json()
                messages.error(request, data['message'])
                return render(request, 'Reports/busstation_stock.html',
                              {"regionlist": regionlist, 'bus': buslist, 'depolist': depolist, "menuname": menuname,
                               'wh_masterlist': wh_masterlist})

    except:
        if response.status_code == 400:
            data = response.json()
            messages.error(request, data['message'])
            return render(request, 'login1.html')
    return render(request, 'Reports/busstation_stock.html',{'menuname':menuname})


def depot_stock1(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    try:
        menuname = request.session['mylist']
        accesskey = request.session['accesskey']
        url = "http://13.235.112.1/ziva/mobile-api/warehousemaster-list.php"
        payload = json.dumps({"accesskey": accesskey})
        headers = {
            'Content-Type': 'text/plain'
        }
        response = requests.request("GET", url, headers=headers, data=payload)
        data = response.json()
        wh_masterlist = data['warehouselist']

        url = "http://13.235.112.1/ziva/mobile-api/dates-filter.php"

        payload = json.dumps({"accesskey": accesskey})
        headers = {
            'Content-Type': 'text/plain'
        }
        response = requests.request("GET", url, headers=headers, data=payload)

        data = response.json()
        selectrange = data['timingslist']

        if request.method == 'POST':
          pass
        else:
            current_date = datetime.date.today()
            queryset = OutpassItem.objects.using('auth').extra(
                tables=['outpass_item', 'outpass_generate','busstation_master'],
                where=[
                    'outpass_item.outpass_number = outpass_generate.outpass_number',
                    "outpass_generate.status = 'Accepted'",
                    "(outpass_generate.warehouseid = busstation_master.busatation_id OR outpass_generate.regionid = busstation_master.busatation_id)"
                ],

                select={
                    'busstation_id': 'outpass_generate.regionid',
                    'outpass_generate_regionid': 'outpass_generate.warehouseid',
                    'item_code': 'outpass_item.item_code',
                    'quantity': 'outpass_item.qty',
                    'busstation_id1': 'busstation_master.busatation_id',
                    'busstationname': 'outpass_generate.region_name',
                }

                ).values(
                    'busstation_id', 'outpass_generate_regionid', 'item_code',
                    'quantity', 'busstationname','busstation_id1'
                )
            filtered_itemcodes = ['PHA0004', 'PHA0002', 'PHA0001']
            queryset1 = queryset.filter(
                modifiedon__lte=current_date, item_code__in=filtered_itemcodes,
            ).values('outpass_generate_regionid',
                     'item_code').annotate(total_qty=Sum('qty'))
            queryset2 = queryset.filter(
                modifiedon__lte=current_date, item_code__in=filtered_itemcodes,
            ).values('busstation_id', 'busstationname','item_code').annotate(total_sum=Sum('qty'))
            merged_list = []
            for item1 in queryset1:
                for item2 in queryset2:
                    if item1['outpass_generate_regionid'] == item2['busstation_id'] and item1['item_code'] == item2[
                        'item_code']:
                        total_qty = item1['total_qty']+item2['total_sum']
                        merged_item = {
                            'busstation_id': item2['busstation_id'],
                            'item_code': item2['item_code'],
                            'total_qty': total_qty,
                            'busstationname':item2['busstationname']
                        }
                        merged_list.append(merged_item)
                        break
                    else:
                        merged_item = {
                            'busstation_id': item2['busstation_id'],
                            'item_code': item2['item_code'],
                            'total_qty': item2['total_sum'],
                            'busstationname': item2['busstationname']

                        }
                        merged_list.append(merged_item)
            print(merged_list)
            sorted_data = sorted(merged_list, key=lambda x: x['busstation_id'])
            grouped_data1 = []
            for (busstation_id, busstationname), group in groupby(sorted_data,
                                                                 key=lambda x: (x['busstation_id'], x['busstationname'])):
                items1 = [{'itemcode': item['item_code'], 'total_sum': item['total_qty']} for item in group]
                grouped_data1.append({'busstation_id': busstation_id, 'busstationname': busstationname, 'items1': items1})

            item_sum_qty = BusstationInventory.objects.using('auth').filter(
                createdon__lte=current_date, itemcode__in=filtered_itemcodes,is_active=1,  # Include the is_active condition
                expiry_date__gte=current_date,
            ).values('itemcode', 'busstation_id').annotate(total_qty=Sum('sale_qty'))

            bus_info = BusstationMaster.objects.using('auth').all().values('busstationname', 'busatation_id')
            grouped_data = []
            sorted_data1 = sorted(item_sum_qty, key=lambda x: x['busstation_id'])

            for busatation_id, group in groupby(sorted_data1, key=lambda x: x['busstation_id']):
                items = [{'itemcode': item['itemcode'], 'total_qty': int(item['total_qty'])} for item in group]
                grouped_data.append({'busstation_id': busatation_id, 'items': items})

            merged_data1 = []
            for d in grouped_data:
                busstation_id = d['busstation_id']
                createdon__date = current_date
                date_createdon = createdon__date.strftime("%d-%b-%Y")
                items = d['items']

                for bus in bus_info:
                    if bus['busatation_id'] == busstation_id:
                        busstationname = bus['busstationname']
                        break
                    else:
                        busstationname = None

                merged_dict = {
                    'busatation_id': busstation_id,
                    'busstationname': busstationname,
                    'createdon__date': date_createdon,
                    'items': items,

                }

                merged_data1.append(merged_dict)

            merged_data2 = []
            for item1 in grouped_data1:
                match_found = False
                for item2 in merged_data1:
                    if item1['busstation_id'] == item2['busatation_id'] and item1['busstationname'] == item2[
                        'busstationname']:
                        item2['items'].extend(item1['items1'])
                        merged_data2.append(item2)
                        match_found = True
                        break
                if not match_found:
                    merged_data2.append(item1)

            # Add remaining items from list2 (if any) to the combined list
            for item2 in merged_data1:
                match_found = False
                for item1 in merged_data2:
                    if item2['busatation_id'] == item1['busatation_id'] and item2['busstationname'] == item1['busstationname']:
                        match_found = True
                        break
                if not match_found:
                    merged_data2.append(item2)

            print(merged_data2)
            return render(request, 'Reports/busstation_stock.html',
                          {"menuname": menuname, 'wh_masterlist': wh_masterlist, 'item_quantities': merged_data2})
    except:
        if response.status_code == 400:
            data = response.json()
            messages.error(request, data['message'])
            return render(request, 'login1.html')
    return render(request, 'Reports/busstation_stock.html',{'menuname':menuname})

def warehouse_stock1(request,id):
        if 'accesskey' not in request.session:
            messages.error(request, 'Access denied!')
            return redirect('/login')
        try:
            menuname = request.session['mylist']
            accesskey = request.session['accesskey']

            payload = json.dumps({"accesskey": accesskey})
            headers = {
                'Content-Type': 'application/json'
            }
            url = "http://13.235.112.1/ziva/mobile-api/region-list.php"
            response = requests.request("POST", url, headers=headers, data=payload)

            data = response.json()
            regionlist = data['regionlist']

            url = "http://13.235.112.1/ziva/mobile-api/warehousemaster-list.php"
            payload = json.dumps({"accesskey": accesskey})
            headers = {
                'Content-Type': 'text/plain'
            }
            response = requests.request("GET", url, headers=headers, data=payload)
            data = response.json()
            wh_masterlist = data['warehouselist']

            url = "http://13.235.112.1/ziva/mobile-api/depo-list.php"

            payload = json.dumps({"accesskey": accesskey,
                                  "warehouseid": request.POST.get('warehouseid'),
                                  "regionid": request.POST.get('regionid')})

            headers = {
                'Content-Type': 'text/plain'
            }
            response = requests.request("GET", url, headers=headers, data=payload)

            data = response.json()
            depolist = data['depolist']

            url = "http://13.235.112.1/ziva/mobile-api/bus-list.php"
            payload = json.dumps({
                "accesskey": accesskey
            })
            headers = {
                'Content-Type': 'application/json'
            }

            response = requests.request("GET", url, headers=headers, data=payload)

            data = response.json()
            bus = data['buslist']

            url = "http://13.235.112.1/ziva/mobile-api/warehouse-inventory-report.php"

            payload = json.dumps({"accesskey": accesskey, "warehouseid": id})
            headers = {
                'Content-Type': 'text/plain'
            }
            response = requests.request("GET", url, headers=headers, data=payload)
            if response.status_code == 200:
                data = response.json()
                warehouseinventorylist = data['warehouseinventorylist']
                return render(request, 'Reports/warehouse_stock.html',
                              {"bus": bus, "depolist": depolist, "regionlist": regionlist, "menuname": menuname,
                               'wh_masterlist': wh_masterlist, 'inventorylist': warehouseinventorylist})

            elif response.status_code == 500:
                messages.error(request, 'Internal server  error')
                return render(request, 'Reports/warehouse_stock.html',
                              {"bus": bus, "depolist": depolist, "regionlist": regionlist, "menuname": menuname,
                               'wh_masterlist': wh_masterlist})

            else:
                data = response.json()
                messages.error(request, data['message'])
                return render(request, 'Reports/warehouse_stock.html',
                              {"bus": bus, "depolist": depolist, "regionlist": regionlist, "menuname": menuname,
                               'wh_masterlist': wh_masterlist})

        except:
            if response.status_code == 400:
                data = response.json()
                messages.error(request, data['message'])
                return render(request, 'login1.html')
        return render(request, 'Reports/warehouse_stock.html',{'menuname':menuname})

def warehouse_stock(request):
        if 'accesskey' not in request.session:
            messages.error(request, 'Access denied!')
            return redirect('/login')
        try:
            accesskey = request.session['accesskey']
            payload = json.dumps({"accesskey": accesskey})
            headers = {
                'Content-Type': 'application/json'
            }
            url = "http://13.235.112.1/ziva/mobile-api/region-list.php"
            response = requests.request("POST", url, headers=headers, data=payload)

            data = response.json()
            regionlist = data['regionlist']

            url = "http://13.235.112.1/ziva/mobile-api/warehousemaster-list.php"
            payload = json.dumps({"accesskey": accesskey})
            headers = {
                'Content-Type': 'text/plain'
            }
            response = requests.request("GET", url, headers=headers, data=payload)
            data = response.json()
            wh_masterlist = data['warehouselist']

            url = "http://13.235.112.1/ziva/mobile-api/depo-list.php"

            payload = json.dumps({"accesskey": accesskey,
                                  "warehouseid": request.POST.get('warehouseid'),
                                  "regionid": request.POST.get('regionid')})

            headers = {
                'Content-Type': 'text/plain'
            }
            response = requests.request("GET", url, headers=headers, data=payload)

            data = response.json()
            depolist = data['depolist']

            url = "http://13.235.112.1/ziva/mobile-api/bus-list.php"
            payload = json.dumps({
                "accesskey": accesskey
            })
            headers = {
                'Content-Type': 'application/json'
            }

            response = requests.request("GET", url, headers=headers, data=payload)

            data = response.json()
            bus = data['buslist']
            menuname = request.session['mylist']


            url = "http://13.235.112.1/ziva/mobile-api/warehouse-inventory-report.php"

            payload = json.dumps({"accesskey": accesskey, "warehouseid":"All"})
            headers = {
                'Content-Type': 'text/plain'
            }
            response = requests.request("GET", url, headers=headers, data=payload)
            if response.status_code == 200:
                    data = response.json()
                    warehouseinventorylist = data['warehouseinventorylist']

                    return render(request, 'Reports/warehouse_stock.html',
                                  {"bus":bus,"depolist":depolist,"regionlist":regionlist,"menuname": menuname,'inventorylist':warehouseinventorylist,
                                   "wh_masterlist": wh_masterlist})
            elif response.status_code == 500:
                    messages.error(request, 'Internal server  error')
                    return render(request, 'Reports/warehouse_stock.html',
                                  {"regionlist": regionlist, 'bus': bus, 'depolist': depolist,
                                   "wh_masterlist": wh_masterlist, "menuname": menuname})
            else:
                data = response.json()
                messages.error(request, data['message'])
                return render(request, 'Reports/warehouse_stock.html',
                              {"regionlist": regionlist, 'bus': bus, 'depolist': depolist,
                               "wh_masterlist": wh_masterlist, "menuname": menuname})
        except:
            if response.status_code == 400:
                data = response.json()
                messages.error(request, data['message'])
                return render(request, 'login1.html')
        return render(request, 'Reports/warehouse_stock.html',{'menuname':menuname})

def region_stock1(request,id):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    try:
        accesskey = request.session['accesskey']
        menuname = request.session['mylist']
        payload = json.dumps({"accesskey": accesskey})
        headers = {
            'Content-Type': 'application/json'
        }
        url = "http://13.235.112.1/ziva/mobile-api/region-list.php"
        response = requests.request("POST", url, headers=headers, data=payload)

        data = response.json()
        regionlist = data['regionlist']

        url = "http://13.235.112.1/ziva/mobile-api/warehousemaster-list.php"
        payload = json.dumps({"accesskey": accesskey})
        headers = {
            'Content-Type': 'text/plain'
        }
        response = requests.request("GET", url, headers=headers, data=payload)
        data = response.json()
        wh_masterlist = data['warehouselist']

        url = "http://13.235.112.1/ziva/mobile-api/depo-list.php"

        payload = json.dumps({"accesskey": accesskey,
                              "warehouseid": request.POST.get('warehouseid'),
                              "regionid": request.POST.get('regionid')})

        headers = {
            'Content-Type': 'text/plain'
        }
        response = requests.request("GET", url, headers=headers, data=payload)

        data = response.json()
        depolist = data['depolist']

        url = "http://13.235.112.1/ziva/mobile-api/bus-list.php"
        payload = json.dumps({
            "accesskey": accesskey
        })
        headers = {
            'Content-Type': 'application/json'
        }

        response = requests.request("GET", url, headers=headers, data=payload)

        data = response.json()
        bus = data['buslist']

        url = "http://13.235.112.1/ziva/mobile-api/region-inventory-report.php"
        payload = json.dumps({
            "accesskey": accesskey,"regionid":id
        })
        headers = {
            'Content-Type': 'application/json'
        }

        response = requests.request("GET", url, headers=headers, data=payload)
        if response.status_code == 200:
            data = response.json()
            data1 = data['regioninventorylist']
            return render(request, 'Reports/region_stockreport.html',
                          {"regionlist":regionlist,'bus':bus,'depolist':depolist,"wh_masterlist":wh_masterlist,"menuname": menuname,'item_quantities':data1})
        elif response.status_code == 500:
            messages.error(request, 'Internal server  error')
            return render(request, 'Reports/region_stockreport.html',
                          {"regionlist": regionlist, 'bus': bus, 'depolist': depolist,
                           "wh_masterlist": wh_masterlist, "menuname": menuname})
        else:
            data = response.json()
            messages.error(request, data['message'])
            return render(request, 'Reports/region_stockreport.html',
                          {"regionlist": regionlist, 'bus': bus, 'depolist': depolist,
                           "wh_masterlist": wh_masterlist, "menuname": menuname})
    except:
        if response.status_code == 400:
            data = response.json()
            messages.error(request, data['message'])
            return render(request, 'login1.html')
    return render(request, 'Reports/region_stockreport.html',{'menuname':menuname})
def region_stock(request,id):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    try:
        accesskey = request.session['accesskey']
        menuname = request.session['mylist']
        payload = json.dumps({"accesskey": accesskey})
        headers = {
            'Content-Type': 'application/json'
        }
        url = "http://13.235.112.1/ziva/mobile-api/region-list.php"
        response = requests.request("POST", url, headers=headers, data=payload)

        data = response.json()
        regionlist = data['regionlist']

        url = "http://13.235.112.1/ziva/mobile-api/warehousemaster-list.php"
        payload = json.dumps({"accesskey": accesskey})
        headers = {
            'Content-Type': 'text/plain'
        }
        response = requests.request("GET", url, headers=headers, data=payload)
        data = response.json()
        wh_masterlist = data['warehouselist']

        url = "http://13.235.112.1/ziva/mobile-api/depo-list.php"

        payload = json.dumps({"accesskey": accesskey,
                              "warehouseid": request.POST.get('warehouseid'),
                              "regionid": request.POST.get('regionid')})

        headers = {
            'Content-Type': 'text/plain'
        }
        response = requests.request("GET", url, headers=headers, data=payload)

        data = response.json()
        depolist = data['depolist']

        url = "http://13.235.112.1/ziva/mobile-api/bus-list.php"
        payload = json.dumps({
            "accesskey": accesskey
        })
        headers = {
            'Content-Type': 'application/json'
        }

        response = requests.request("GET", url, headers=headers, data=payload)

        data = response.json()
        bus = data['buslist']

        url = "http://13.235.112.1/ziva/mobile-api/warehousewise-inventory-report.php"
        payload = json.dumps({
            "accesskey": accesskey,  "warehouseid":id
        })
        headers = {
            'Content-Type': 'application/json'
        }

        response = requests.request("GET", url, headers=headers, data=payload)
        if response.status_code == 200:
            data = response.json()
            regiondata = data['warehouseinventorylist']

            return render(request, 'Reports/region_stockreport.html',
                          {"regionlist":regionlist,'bus':bus,'depolist':depolist,"wh_masterlist":wh_masterlist,"menuname": menuname, 'item_quantities': regiondata})
        elif response.status_code == 500:
            messages.error(request, 'Internal server  error')
            return render(request, 'Reports/region_stockreport.html',
                          {"regionlist": regionlist, 'bus': bus, 'depolist': depolist,
                           "wh_masterlist": wh_masterlist, "menuname": menuname})
        else:
            data = response.json()
            messages.error(request, data['message'])
            return render(request, 'Reports/region_stockreport.html',
                          {"regionlist": regionlist, 'bus': bus, 'depolist': depolist,
                           "wh_masterlist": wh_masterlist, "menuname": menuname})
    except:
        if response.status_code == 400:
            data = response.json()
            messages.error(request, data['message'])
            return render(request, 'login1.html')
    return render(request,'Reports/region_stockreport.html',{'menuname':menuname})

def __id_generator__(size=6, chars=string.ascii_uppercase + string.digits + string.ascii_lowercase):
    return ''.join(random.choice(chars) for _ in range(size))

def qr_code(request):

    # import checksum generation utility
    # You can get this utility from https://developer.paytm.com/docs/checksum/
    amount = request.POST.get('amount')
    paytmParams = dict()
    order_id = __id_generator__()
    paytmParams["body"] = {
        "mid": "TSRTCP03244016260030",
        "orderId": order_id,
        "amount": amount,
        "businessType": "UPI_QR_CODE",
        "posId": "S12_123"
    }

    # Generate checksum by parameters we have in body
    # Find your Merchant Key in your Paytm Dashboard at https://dashboard.paytm.com/next/apikeys
    checksum = paytmchecksum.generateSignature(json.dumps(paytmParams["body"]), "jXXQfmzmqD3PpchQ")

    paytmParams["head"] = {
        "clientId"	: "C11",
        "version"	        : "v1",
        "signature"         : checksum
    }

    post_data = json.dumps(paytmParams)

    # for Staging
    url = "https://securegw-stage.paytm.in/paymentservices/qr/create"

    # for Production
    # url = "https://securegw.paytm.in/paymentservices/qr/create"
    response = requests.post(url, data = post_data, headers = {"Content-type": "application/json"}).json()
    result=response['body']
    result['id'] = order_id
    image=result['image']
    return JsonResponse({'data':result})
    #return render(request,'sales/sales_new.html',{'image':image,'result':result})


def qr_response(request):
    paytmParams = dict()
    order_id = request.POST.get('order_id')
    # body parameters
    paytmParams["body"] = {

        # Find your MID in your Paytm Dashboard at https://dashboard.paytm.com/next/apikeys
        "mid": "TSRTCP03244016260030",

        # Enter your order id which needs to be check status for
        "orderId": order_id,
    }

    # Generate checksum by parameters we have in body
    # Find your Merchant Key in your Paytm Dashboard at https://dashboard.paytm.com/next/apikeys
    checksum = paytmchecksum.generateSignature(json.dumps(paytmParams["body"]), "jXXQfmzmqD3PpchQ")

    # head parameters
    paytmParams["head"] = {

        # put generated checksum value here
        "signature": checksum
    }

    # prepare JSON string for request
    post_data = json.dumps(paytmParams)

    # for Staging
    url = "https://securegw-stage.paytm.in/v3/order/status"

    # for Production
    # url = "https://securegw.paytm.in/v3/order/status"

    response = requests.post(url, data=post_data, headers={"Content-type": "application/json"}).json()
    resultMsg = response['body']
    response = resultMsg['resultInfo']
    if response['resultCode'] == '01':
        response = resultMsg['resultInfo']
        response['txnId'] = resultMsg['txnId']
        return JsonResponse(response)
    else:
        return JsonResponse(response)

@csrf_exempt
def payment(request):
    if request.method == 'POST':
            amount = request.POST.get('netvalue')
            sonumber =  request.POST.get('txtHdnId')
            paymentmode =request.POST.get('paymenttype')
            remarks = request.POST.get('remarks')
            date = request.POST.get('date')
            spelloftheday =request.POST.get('spell1')
            order_id = __id_generator__()
            context = {
                'order_id':order_id,'sonumber':sonumber,'paymentmode':paymentmode,'remarks':remarks,'date':date,'spelloftheday':spelloftheday

            }
            paytmParams = dict()
            url = reverse('response',  kwargs=context)
            #url = "https://tsrtcziva.com/response/{}/".format(order_id)
            paytmParams['body'] = {
                "requestType": "Payment",
                "mid": "TSRTCP03244016260030",
                "websiteName": "WEBSTAGING",
                "orderId": order_id,
                "callbackUrl":url,
                "txnAmount": amount,
                "currency": "INR",
                "userInfo": {
                    "custId": "CUST_001",
                },
            }

            # Generate checksum by parameters we have in body
            # Find your Merchant Key in your Paytm Dashboard at https://dashboard.paytm.com/next/apikeys
            checksum = paytmchecksum.generateSignature(json.dumps(paytmParams["body"]), "jXXQfmzmqD3PpchQ")
            #checksum = paytmchecksum.generateSignature(json.dumps(paytmParams, "jXXQfmzmqD3PpchQ"))
            paytmParams["head"] = {
                "signature": checksum
            }

            post_data = json.dumps(paytmParams)

            # for Staging
            url = "https://securegw-stage.paytm.in/theia/api/v1/initiateTransaction?mid=TSRTCP03244016260030&orderId={}".format(order_id)

            # for Production
            #url = "https://securegw.paytm.in/theia/api/v1/initiateTransaction?mid=TSRTCP03244016260030&orderId={}".format(order_id)
            response = requests.post(url, data=post_data, headers={"Content-type": "application/json"}).json()
            print(response)
            data = response['body']
            data1=paytmParams['body']
            result = data['resultInfo']
            status = result['resultMsg']
            if status == 'Success':
                txnToken = data['txnToken']
                context = {
                    'data_dict': data1,
                    'txnToken':txnToken,
                    'sonumber':sonumber
                }
                return render(request, 'payment.html', context)
            else:
                return redirect(proformainvoice)
    else:
        return redirect('/sale_item_list')
@csrf_exempt
def response(request, order_id, paymentmode, sonumber,date,spelloftheday,remarks):
    accesskey = request.session['accesskey']
    #status = request.POST.get('STATUS')
    txn_id =  request.POST.get('TXNID')
    paytmParams = dict()
    paytmParams['body'] = {
        "mid": "TSRTCP03244016260030",
        "orderId": order_id,
    }
    checksum = paytmchecksum.generateSignature(json.dumps(paytmParams["body"]), "jXXQfmzmqD3PpchQ")

    # head parameters
    paytmParams["head"] = {

        # put generated checksum value here
        "signature": checksum
    }

    # prepare JSON string for request
    post_data = json.dumps(paytmParams)

    # for Staging
    url = "https://securegw-stage.paytm.in/v3/order/status"

    # for Production
    #url = "https://securegw.paytm.in/v3/order/status"

    response = requests.post(url, data=post_data, headers={"Content-type": "application/json"}).json()
    print(response)
    data = response['body']
    resultInfo = data['resultInfo']
    txn_id = data['txnId']
    data1 = paytmParams['body']
    context = {
        'data_dict': data1,
        'data':data,
    }
    if resultInfo['resultCode'] == '01':
        #url = reverse('complete_sale', args=[json.dumps(context)])
        url = "http://13.235.112.1/ziva/mobile-api/dc-pending.php"

        payload = json.dumps({
            "accesskey": accesskey,
            "sonumber": sonumber,
            "paymentmode":paymentmode,
            "remarks": remarks,
            "date":date,
            "spelloftheday": spelloftheday,
            "transaction_status":"success",
            "transaction_id": txn_id,
        })
        headers = {
            'Content-Type': 'application/json'
        }
        response = requests.request("GET", url, headers=headers, data=payload)
        data = response.json()
        if response.status_code == 200:
            messages.success(request, data['message'])
            return redirect('proformainvoice')
        if response.status_code == 400:
            messages.success(request, data['message'])
            return render(request,'login1.html')
        else:
            messages.error(request, data['message'])
            return redirect('proformainvoice')
    else:
        messages.error(request, data['message'])
        return redirect('proformainvoice')


def pending_indent_admin(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    try:
        menuname = request.session['mylist']
        accesskey = request.session['accesskey']
        url = "http://13.235.112.1/ziva/mobile-api/warehousemaster-list.php"
        payload = json.dumps({"accesskey": accesskey})
        headers = {
            'Content-Type': 'text/plain'
        }
        response = requests.request("GET", url, headers=headers, data=payload)
        data = response.json()
        wh_masterlist = data['warehouselist']

        url = "http://13.235.112.1/ziva/mobile-api/depo-list.php"

        payload = json.dumps({"accesskey": accesskey})
        headers = {
            'Content-Type': 'text/plain'
        }
        response = requests.request("GET", url, headers=headers, data=payload)
        data = response.json()
        depolist = data['depolist']

        if request.method == 'POST':
            tdate = request.POST.get('fdate')
            ldate = request.POST.get('ldate')
            if tdate:
                tdate=tdate
            else:
                tdate='All'
            if ldate:
                ldate=ldate
            else:
                ldate ='All'


            url="http://13.235.112.1/ziva/mobile-api/indent-pendinglist-admin.php"
            payload = json.dumps({
                "depoid":request.POST.get('depoid1'),
                "tdate": ldate,
                "accesskey": accesskey,
                "warehouseid": request.POST.get('warehouseid1'),
                "status": "Pending",
                "fdate": tdate,
            })

            headers = {
                'Content-Type': 'application/json'
            }

            response = requests.request("GET", url, headers=headers, data=payload)
            if response.status_code == 200:
                data = response.json()
                list = data['indentlist']
                return render(request,'create_indent/pending_indent_admin.html',{'data1':"Pending","depolist":depolist,'menuname':menuname,'wh_masterlist':wh_masterlist,'list':list})
            else:
                return render(request, 'create_indent/pending_indent_admin.html',
                              {'menuname': menuname, 'wh_masterlist': wh_masterlist,"depolist":depolist,'data1':"Pending"})
        else:
            url = "http://13.235.112.1/ziva/mobile-api/indent-pendinglist-admin.php"
            payload = json.dumps({
                "depoid": "All",
                "tdate": "All",
                "accesskey": accesskey,
                "warehouseid": "All",
                "status": "Pending",
                "fdate": "All"
            })

            headers = {
                'Content-Type': 'application/json'
            }

            response = requests.request("GET", url, headers=headers, data=payload)
            if response.status_code == 200:
                data = response.json()
                list = data['indentlist']
                return render(request, 'create_indent/pending_indent_admin.html',
                              {'menuname': menuname, 'wh_masterlist': wh_masterlist,'list':list,'data1':"Pending","depolist":depolist})
            else:
                    return render(request, 'create_indent/pending_indent_admin.html',
                                  {'menuname': menuname, 'wh_masterlist': wh_masterlist,"depolist":depolist,'data1':"Pending"})
    except:
        if response.status_code == 400:
            data = response.json()
            messages.error(request, data['message'])
            return render(request, 'login1.html')
    return render(request, 'create_indent/pending_indent_admin.html')



def taxinvoice_list_admin(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    try:
        menuname = request.session['mylist']
        accesskey = request.session['accesskey']
        url = "http://13.235.112.1/ziva/mobile-api/warehousemaster-list.php"
        payload = json.dumps({"accesskey": accesskey})
        headers = {
            'Content-Type': 'text/plain'
        }
        response = requests.request("GET", url, headers=headers, data=payload)
        data = response.json()
        wh_masterlist = data['warehouselist']

        url = "http://13.235.112.1/ziva/mobile-api/dates-filter.php"

        payload = json.dumps({"accesskey": accesskey})
        headers = {
            'Content-Type': 'text/plain'
        }
        response = requests.request("GET", url, headers=headers, data=payload)

        data = response.json()
        selectrange = data['timingslist']
        if request.method == 'POST':
            fdate = request.POST.get('fdate')
            ldate = request.POST.get('ldate')
            warehouseid1 = request.POST.get('warehouseid1')
            if fdate:
                fdate = fdate
            else:
                fdate = 'All'
            if ldate:
                ldate = ldate
            else:
                ldate = fdate
            if warehouseid1:
                warehouseid1=warehouseid1
            else:
                warehouseid1='All'

            url ="http://13.235.112.1/ziva/mobile-api/tax-invoicelist-new.php"
            payload = json.dumps(
                {"depoid":request.POST.get('depoid1'),
                                  "tdate":ldate,
                                  "accesskey":accesskey,
                                  "warehouseid":warehouseid1,
                                  "regionid":request.POST.get('regionid1'),
                                  "fdate":fdate,
                                  "busstationid":request.POST.get('busstationid1'),"status":"Approved"
                })
            headers = {
                'Content-Type': 'text/plain'
            }
            response2 = requests.request("GET", url, headers=headers, data=payload)
            if response2.status_code == 200:
                data = response2.json()
                deliverypendinglist = data['deliverypendinglist']
                return render(request, 'sales/taxinvoice_list_admin.html',
                              {'menuname': menuname, 'wh_masterlist': wh_masterlist, "selectrange": selectrange,'deliverypendinglist':deliverypendinglist})
            else:
                return render(request, 'sales/taxinvoice_list_admin.html',
                              {'menuname': menuname, 'wh_masterlist': wh_masterlist, "selectrange": selectrange})

        else:
            url = "http://13.235.112.1/ziva/mobile-api/tax-invoicelist-new.php"
            payload = json.dumps({"depoid": "All",
                                  "tdate": "All",
                                  "accesskey": accesskey,
                                  "warehouseid": "All",
                                  "regionid": "All",
                                  "fdate": "All",
                                  "busstationid":"All", "status":"Approved"})
            headers = {
                'Content-Type': 'text/plain'
            }
            response = requests.request("GET", url, headers=headers, data=payload)
            if response.status_code == 200:
                data = response.json()
                deliverypendinglist = data['deliverypendinglist']
                return render(request, 'sales/taxinvoice_list_admin.html',
                              {'menuname': menuname, 'wh_masterlist': wh_masterlist, "selectrange": selectrange,'deliverypendinglist':deliverypendinglist})
            else:
                return render(request, 'sales/taxinvoice_list_admin.html',
                  {'menuname': menuname, 'wh_masterlist': wh_masterlist, "selectrange": selectrange})
    except:
        if response.status_code == 400:
            data = response.json()
            messages.error(request, data['message'])
            return render(request, 'login1.html')
    return render(request,'sales/taxinvoice_list_admin.html',{'menuname':menuname})

def vehcals_list(request):
    accesskey = request.session['accesskey']
    toid = request.POST.get('toid')
    url = "http://13.235.112.1/ziva/mobile-api/vehicle-dropdownlist-admin.php"
    payload = json.dumps({
        "accesskey": accesskey, "toid": toid
    })
    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.request("GET", url, headers=headers, data=payload)
    if response.status_code == 200:
        data2 = response.json()
        return JsonResponse({'data': data2})
    elif response.status_code == 400:
        data = response.json()
        if data['message'] == 'Sorry! some details are missing':
            return JsonResponse({'data': data})
        else:
            messages.error(request, data['message'])
            return redirect('/login')
    elif response.status_code == 503:
        data = response.json()
        return JsonResponse({'data': data})
    elif response.status_code == 500:
        data = {'error': 'true', 'message': 'Internal server error'}
        return JsonResponse({'data': data})
    else:
        data = {'error': 'true', 'message': 'something went wrong'}
        return JsonResponse({'data': data})


def ready_toship_admin(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    try:
        menuname = request.session['mylist']
        accesskey = request.session['accesskey']
        #toid = request.session['toid']

        url = "http://13.235.112.1/ziva/mobile-api/warehousemaster-list.php"
        payload = json.dumps({"accesskey": accesskey})
        headers = {
            'Content-Type': 'text/plain'
        }
        response = requests.request("GET", url, headers=headers, data=payload)
        data = response.json()
        wh_masterlist = data['warehouselist']

        url = "http://13.235.112.1/ziva/mobile-api/dates-filter.php"

        payload = json.dumps({"accesskey": accesskey})
        headers = {
            'Content-Type': 'text/plain'
        }
        response = requests.request("GET", url, headers=headers, data=payload)

        data = response.json()
        selectrange = data['timingslist']

        if request.method == 'POST':
            fdate = request.POST.get('fdate')
            ldate = request.POST.get('ldate')
            if fdate:
                fdate = fdate
            else:
                fdate = 'All'
            if ldate:
                ldate = ldate
            else:
                ldate = 'All'
            url = "http://13.235.112.1/ziva/mobile-api/readytoship-admin-list.php"
            payload = json.dumps({"depoid": request.POST.get('depoid1'),
                                  "tdate": ldate,
                                  "accesskey": accesskey,
                                  "warehouseid": request.POST.get('warehouseid1'),
                                  "busstationid":request.POST.get('busstationid1'),
                                  "status": "Pending",
                                  "fdate":fdate})
            headers = {
                'Content-Type': 'text/plain'
            }
            response = requests.request("GET", url, headers=headers, data=payload)
            if response.status_code == 200:
                data = response.json()
                indentlist = data['indentlist']

                return render(request, 'create_indent/ready_toship_admin.html',
                                  {'menuname': menuname, 'wh_masterlist': wh_masterlist, "selectrange": selectrange,
                                   'indentlist': indentlist})

            else:

                    return render(request, 'create_indent/ready_toship_admin.html',
                                  {'menuname': menuname, 'wh_masterlist': wh_masterlist, "selectrange": selectrange,
                                   })


        else:
            url = "http://13.235.112.1/ziva/mobile-api/readytoship-admin-list.php"
            payload = json.dumps({"depoid": "All",
                                  "tdate": "All",
                                  "accesskey": accesskey,
                                  "warehouseid": "All",
                                  "busstationid": "All",
                                  "status": "Pending",
                                  "fdate":"All"
            })
            headers = {
                'Content-Type': 'text/plain'
            }
            response = requests.request("GET", url, headers=headers, data=payload)
            if response.status_code == 200:
                data = response.json()
                indentlist = data['indentlist']

                return render(request, 'create_indent/ready_toship_admin.html',
                                  {'menuname': menuname, 'wh_masterlist': wh_masterlist, "selectrange": selectrange,
                                   'indentlist': indentlist})

            else:

                    return render(request, 'create_indent/ready_toship_admin.html',
                                  {'menuname': menuname, 'wh_masterlist': wh_masterlist, "selectrange": selectrange,
                                   })

    except:
         if response.status_code == 400:
            data = response.json()
            messages.error(request, data['message'])
            return render(request, 'login1.html')
    return render(request, 'create_indent/ready_toship_admin.html',{'menuname':menuname})

def outpass_list_admin(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    try:
        menuname = request.session['mylist']
        accesskey = request.session['accesskey']
        url = "http://13.235.112.1/ziva/mobile-api/warehousemaster-list.php"
        payload = json.dumps({"accesskey": accesskey})
        headers = {
            'Content-Type': 'text/plain'
        }
        response = requests.request("GET", url, headers=headers, data=payload)
        data = response.json()
        wh_masterlist = data['warehouselist']

        url = "http://13.235.112.1/ziva/mobile-api/dates-filter.php"

        payload = json.dumps({"accesskey": accesskey})
        headers = {
            'Content-Type': 'text/plain'
        }
        response = requests.request("GET", url, headers=headers, data=payload)

        data = response.json()
        selectrange = data['timingslist']

        if request.method == 'POST':
            fdate = request.POST.get('fdate')
            ldate = request.POST.get('ldate')
            if fdate:
                fdate = fdate
            else:
                fdate = 'All'
            if ldate:
                ldate = ldate
            else:
                ldate = 'All'
            url = "http://13.235.112.1/ziva/mobile-api/outpassgenerate-list-admin.php"
            payload = json.dumps({"depoid": request.POST.get('depoid1'),
                                  "tdate": ldate,
                                  "busstationid": request.POST.get('busstationid1'),
                                  "accesskey": accesskey,
                                  "warehouseid": request.POST.get('warehouseid1'),
                                  "status": "Pending",
                                  "fdate": fdate})
            headers = {
                'Content-Type': 'text/plain'
            }
            response = requests.request("GET", url, headers=headers, data=payload)
            if response.status_code == 200:
                data = response.json()
                indentlist = data['indentlist']
                return render(request, 'create_indent/outpass_listadmin.html',
                              {'menuname': menuname, 'wh_masterlist': wh_masterlist, "selectrange": selectrange,
                               'indentlist': indentlist})
            else:
                return render(request, 'create_indent/outpass_listadmin.html',
                              {'menuname': menuname, 'wh_masterlist': wh_masterlist, "selectrange": selectrange})

        else:
            url = "http://13.235.112.1/ziva/mobile-api/outpassgenerate-list-admin.php"
            payload = json.dumps({"depoid": "All",
                                  "tdate": "All",
                                  "busstationid": "All",
                                  "accesskey": accesskey,
                                  "warehouseid": "All",
                                  "status": "Pending",
                                  "fdate": "All"
                                  })
            headers = {
                'Content-Type': 'text/plain'
            }
            response = requests.request("GET", url, headers=headers, data=payload)
            if response.status_code == 200:
                data = response.json()
                indentlist = data['indentlist']
                return render(request, 'create_indent/outpass_listadmin.html',
                              {'menuname': menuname, 'wh_masterlist': wh_masterlist, "selectrange": selectrange,
                               'indentlist': indentlist})
            else:
                return render(request, 'create_indent/outpass_listadmin.html',
                              {'menuname': menuname, 'wh_masterlist': wh_masterlist, "selectrange": selectrange})
    except:
        if response.status_code == 400:
            data = response.json()
            messages.error(request, data['message'])
            return render(request, 'login1.html')
    return render(request, 'create_indent/ready_toship_admin.html')

def approve_list_admin(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    try:
        menuname = request.session['mylist']
        accesskey = request.session['accesskey']
        url = "http://13.235.112.1/ziva/mobile-api/warehousemaster-list.php"
        payload = json.dumps({"accesskey": accesskey})
        headers = {
            'Content-Type': 'text/plain'
        }
        response = requests.request("GET", url, headers=headers, data=payload)
        data = response.json()
        wh_masterlist = data['warehouselist']

        url = "http://13.235.112.1/ziva/mobile-api/dates-filter.php"

        payload = json.dumps({"accesskey": accesskey})
        headers = {
            'Content-Type': 'text/plain'
        }
        response = requests.request("GET", url, headers=headers, data=payload)

        data = response.json()
        selectrange = data['timingslist']

        if request.method == 'POST':
            fdate = request.POST.get('fdate')
            ldate = request.POST.get('ldate')
            if fdate:
                fdate = fdate
            else:
                fdate = 'All'
            if ldate:
                ldate = ldate
            else:
                ldate = 'All'
            url = "http://13.235.112.1/ziva/mobile-api/departmentstock-list-admin.php"
            payload = json.dumps({"depoid": request.POST.get('depoid1'),
                                  "tdate": ldate,
                                  "busstationid": request.POST.get('busstationid1'),
                                  "accesskey": accesskey,
                                  "warehouseid": request.POST.get('warehouseid1'),
                                  "status": "Out For Delivery",
                                  "fdate": fdate})
            headers = {
                'Content-Type': 'text/plain'
            }
            response = requests.request("GET", url, headers=headers, data=payload)
            if response.status_code == 200:
                data = response.json()
                stocklist = data['stocklist']
                return render(request, 'create_indent/approved_list_admin.html',
                              {'menuname': menuname, 'wh_masterlist': wh_masterlist, "selectrange": selectrange,
                               'stocklist': stocklist})
            else:
                return render(request, 'create_indent/approved_list_admin.html',
                              {'menuname': menuname, 'wh_masterlist': wh_masterlist, "selectrange": selectrange})

        else:
            url = "http://13.235.112.1/ziva/mobile-api/departmentstock-list-admin.php"
            payload = json.dumps({"depoid": "All",
                                  "tdate": "All",
                                  "busstationid": "All",
                                  "accesskey": accesskey,
                                  "warehouseid": "All",
                                  "status": "Out For Delivery",
                                  "fdate": "All"
                                  })
            headers = {
                'Content-Type': 'text/plain'
            }
            response = requests.request("GET", url, headers=headers, data=payload)
            if response.status_code == 200:
                data = response.json()
                stocklist = data['stocklist']
                return render(request, 'create_indent/approved_list_admin.html',
                              {'menuname': menuname, 'wh_masterlist': wh_masterlist, "selectrange": selectrange,
                               'stocklist': stocklist})
            else:
                return render(request, 'create_indent/approved_list_admin.html',
                              {'menuname': menuname, 'wh_masterlist': wh_masterlist, "selectrange": selectrange})
    except:
        if response.status_code == 400:
            data = response.json()
            messages.error(request, data['message'])
            return render(request, 'login1.html')
    return render(request, 'create_indent/approved_list_admin.html')

def approve_list_admin1(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    try:
        menuname = request.session['mylist']
        accesskey = request.session['accesskey']
        url = "http://13.235.112.1/ziva/mobile-api/warehousemaster-list.php"
        payload = json.dumps({"accesskey": accesskey})
        headers = {
            'Content-Type': 'text/plain'
        }
        response = requests.request("GET", url, headers=headers, data=payload)
        data = response.json()
        wh_masterlist = data['warehouselist']

        url = "http://13.235.112.1/ziva/mobile-api/dates-filter.php"

        payload = json.dumps({"accesskey": accesskey})
        headers = {
            'Content-Type': 'text/plain'
        }
        response = requests.request("GET", url, headers=headers, data=payload)

        data = response.json()
        selectrange = data['timingslist']

        if request.method == 'POST':
            fdate = request.POST.get('fdate')
            ldate = request.POST.get('ldate')
            if fdate:
                fdate = fdate
            else:
                fdate = 'All'
            if ldate:
                ldate = ldate
            else:
                ldate = 'All'
            url = "http://13.235.112.1/ziva/mobile-api/departmentstock-list-admin.php"
            payload = json.dumps({"depoid": request.POST.get('depoid1'),
                                  "tdate": ldate,
                                  "busstationid": request.POST.get('busstationid1'),
                                  "accesskey": accesskey,
                                  "warehouseid": request.POST.get('warehouseid1'),
                                  "status": "Accepted",
                                  "fdate": fdate})
            headers = {
                'Content-Type': 'text/plain'
            }
            response = requests.request("GET", url, headers=headers, data=payload)
            if response.status_code == 200:
                data = response.json()
                stocklist = data['stocklist']
                return render(request, 'create_indent/approved_list_admin.html',
                              {'menuname': menuname, 'wh_masterlist': wh_masterlist, "selectrange": selectrange,
                               'stocklist': stocklist,'data':'Accepted'})
            else:
                return render(request, 'create_indent/approved_list_admin.html',
                              {'menuname': menuname, 'wh_masterlist': wh_masterlist, "selectrange": selectrange,'data':'Accepted'})

        else:
            url = "http://13.235.112.1/ziva/mobile-api/departmentstock-list-admin.php"
            payload = json.dumps({"depoid": "All",
                                  "tdate": "All",
                                  "busstationid": "All",
                                  "accesskey": accesskey,
                                  "warehouseid": "All",
                                  "status": "Accepted",
                                  "fdate": "All"
                                  })
            headers = {
                'Content-Type': 'text/plain'
            }
            response = requests.request("GET", url, headers=headers, data=payload)
            if response.status_code == 200:
                data = response.json()
                stocklist = data['stocklist']
                return render(request, 'create_indent/approved_list_admin.html',
                              {'menuname': menuname, 'wh_masterlist': wh_masterlist, "selectrange": selectrange,
                               'stocklist': stocklist,'data': 'Accepted'})
            else:
                return render(request, 'create_indent/approved_list_admin.html',
                              {'menuname': menuname, 'wh_masterlist': wh_masterlist, "selectrange": selectrange,'data': 'Accepted'})
    except:
        if response.status_code == 400:
            data = response.json()
            messages.error(request, data['message'])
            return render(request, 'login1.html')
    return render(request, 'create_indent/approved_list_admin.html')

def dashboard(request):

    if 'mylist' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    menuname = request.session['mylist']
    return render(request,'index4.html',{"menuname":menuname})

def sales_dashboard(request):
    if 'mylist' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    menuname = request.session['mylist']
    return render(request, 'index5.html', {"menuname": menuname})

def internal_consumption(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    try:
        accesskey = request.session['accesskey']
        menuname = request.session['mylist']
        role = request.session['role']
        url = "http://13.235.112.1/ziva/mobile-api/depo-list.php"

        payload = json.dumps({"accesskey": accesskey})
        headers = {
            'Content-Type': 'text/plain'
        }
        response = requests.request("GET", url, headers=headers, data=payload)
        data = response.json()
        depolist = data['depolist']

        url = "http://13.235.112.1/ziva/mobile-api/warehousemaster-list.php"
        payload = json.dumps({"accesskey": accesskey})
        headers = {
            'Content-Type': 'text/plain'
        }
        response = requests.request("GET", url, headers=headers, data=payload)
        data = response.json()
        wh_masterlist = data['warehouselist']

        url = "http://13.235.112.1/ziva/mobile-api/noofbottleslist.php"

        payload = json.dumps({"accesskey": accesskey})
        headers = {
            'Content-Type': 'text/plain'
        }
        response = requests.request("GET", url, headers=headers, data=payload)
        data = response.json()
        nobot = data['noofbottleslist']
        if request.method == 'POST':
                        fdate = request.POST.get('fdate')
                        tdate = request.POST.get('tdate')
                        url = "http://13.235.112.1/ziva/mobile-api/busservicesupplylist.php"
                        if role == 'Admin':
                            payload = json.dumps({"accesskey": accesskey,
                                                  "fdate":fdate,
                                                  "tdate":tdate,
                                                  "depot_id": request.POST.get('depoid11'),
                                                   "region_id": request.POST.get('regionid1'),
                                                  "warehouse_id": request.POST.get('warehouseid1')
                                                  })
                        else:
                            payload = json.dumps({"accesskey": accesskey,
                                                  "fdate": fdate,
                                                  "tdate": tdate,
                                                  "depot_id": "",
                                                  "warehouse_id": "",
                                                  "region_id": ""
                                                  })
                        headers = {
                            'Content-Type': 'text/plain'
                        }
                        response = requests.request("GET", url, headers=headers, data=payload)
                        if response.status_code == 200:
                            data = response.json()
                            busservicesupplylist = data['busservicesupplylist']
                            return render(request,'intconsumption/internal_consumption.html',{'nobot':nobot,'busservicesupplylist':busservicesupplylist,"depolist":depolist,'menuname':menuname,'fdate':fdate,'tdate':tdate,'wh_masterlist':wh_masterlist})
                        elif response.status_code == 400:
                            data = response.json()
                            if data['message'] == 'Sorry! some details are missing':
                                messages.error(request, data['message'])
                                return render(request, 'intconsumption/internal_consumption.html',
                                              {'nobot': nobot, "depolist": depolist, 'menuname': menuname,
                                               'fdate': fdate, 'tdate': tdate, 'wh_masterlist': wh_masterlist})
                            else:
                                messages.error(request, data['message'])
                                return redirect('/login')
                        if response.status_code == 503:
                            data = response.json()
                            messages.error(request, data['message'])
                            return render(request, 'intconsumption/internal_consumption.html',
                                          {'nobot': nobot, "depolist": depolist, 'menuname': menuname, 'fdate': fdate,
                                           'tdate': tdate, 'wh_masterlist': wh_masterlist})
                        elif response.status_code == 500:
                            messages.error(request, 'Internal server error')
                            return render(request, 'intconsumption/internal_consumption.html',{'nobot':nobot,"depolist":depolist,'menuname':menuname,'fdate':fdate,'tdate':tdate,'wh_masterlist':wh_masterlist})
                        else:
                            data = response.json()
                            return render(request, 'intconsumption/internal_consumption.html',{'nobot':nobot,"depolist":depolist,'menuname':menuname,'fdate':fdate,'tdate':tdate,'wh_masterlist':wh_masterlist})
        else:
                        current_date = datetime.date.today()
                        fdate = current_date - timedelta(days=current_date.weekday() + 7)
                        fdate = fdate.strftime("%Y-%m-%d")
                        tdate = datetime.date.today()
                        tdate = tdate.strftime("%Y-%m-%d")

                        url = "http://13.235.112.1/ziva/mobile-api/busservicesupplylist.php"
                        if role == 'Admin':
                            payload = json.dumps(
                                {"accesskey": accesskey,
                                 "fdate":fdate,
                                 "tdate":tdate,
                                 "warehouse_id": "All",
                                 "depot_id":"All",
                                "region_id":"All"
                                 })
                        else:
                            payload = json.dumps(
                                {"accesskey": accesskey,
                                 "fdate": fdate,
                                 "tdate": tdate,
                                 "warehouse_id": "",
                                 "depot_id": "",
                                 "region_id": ""
                                 })
                        headers = {
                            'Content-Type': 'text/plain'
                        }
                        response = requests.request("GET", url, headers=headers, data=payload)
                        if response.status_code == 200:
                            data = response.json()
                            busservicesupplylist = data['busservicesupplylist']
                            return render(request, 'intconsumption/internal_consumption.html',
                                          {'nobot': nobot, 'busservicesupplylist': busservicesupplylist, "depolist": depolist,
                                           'wh_masterlist':wh_masterlist,'menuname': menuname,'fdate':fdate,'tdate':tdate})
                        elif response.status_code == 400:
                            data = response.json()
                            messages.error(request, data['message'])
                            return redirect('/login')
                        elif response.status_code == 500:
                            messages.error(request, 'Internal server error')
                            return render(request, 'intconsumption/internal_consumption.html',
                                          {'wh_masterlist':wh_masterlist,'nobot': nobot, "depolist": depolist, 'menuname': menuname,'fdate':fdate,'tdate':tdate})
                        else:
                            data = response.json()
                            return render(request, 'intconsumption/internal_consumption.html',
                                          {'wh_masterlist':wh_masterlist,'nobot': nobot, "depolist": depolist, 'menuname':menuname,'fdate':fdate,'tdate':tdate})

    except:
        if response.status_code == 400:
            data = response.json()
            messages.error(request,data['message'])
            return redirect('/login')
        return render(request, 'intconsumption/internal_consumption.html',{'menuname':menuname})



def get_consumption(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    accesskey = request.session['accesskey']
    url = "http://13.235.112.1/ziva/mobile-api/busservicesearchlist.php"

    payload = json.dumps({
        "accesskey": accesskey,
        "service_id": request.POST.get('id')
    })

    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    if response.status_code == 200:
        data2 = response.json()
        return JsonResponse({'data': data2})
    elif response.status_code == 400:
        data = response.json()
        if data['message'] == 'Sorry! some details are missing':
            messages.error(request, data['message'])
            return redirect('/add_bussupply')
        else:
            messages.error(request, data['message'])
            return redirect('/login')
    else:
        return redirect('/add_bussupply')

def get_dclist(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    accesskey = request.session['accesskey']
    url = "http://13.235.112.1/ziva/mobile-api/dc-controller-list.php"

    payload = json.dumps({
        "accesskey": accesskey,
        "depoid": request.POST.get('depoid1')
    })

    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    if response.status_code == 200:
        data2 = response.json()
        return JsonResponse({'data': data2})
    elif response.status_code == 400:
        data = response.json()
        if data['message'] == 'Sorry! some details are missing':
            messages.error(request, data['message'])
            return redirect('/add_bussupply')
        else:
            messages.error(request, data['message'])
            return redirect('/login')
    else:
        return redirect('/add_bussupply')


def edit_consumption(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    accesskey = request.session['accesskey']
    url = "http://13.235.112.1/ziva/mobile-api/edit-internal-consumption-admin.php"
    payload = json.dumps({"accesskey": accesskey,
                             "service_id":request.POST.get('serviceid'),
                              "deponame": request.POST.get('deponame2'),
                              "bus_service_no": request.POST.get('service1'),
                              "oprs": request.POST.get('oprs1'),
                              "departure_time": request.POST.get('departure1'),
                              "staffnumber": request.POST.get('staffnumbone'),
                              "staffname": request.POST.get('staffnameone'),
                              "vehicleno": request.POST.get('vehicalnumb1'),
                              "product_type": request.POST.get('product1'),
                              "staffnumbertwo": request.POST.get('staffnumb2'),
                              "staffnametwo": request.POST.get('staffname2'),
                              "route": request.POST.get('route1'),
                              "noofbottles": request.POST.get('nobt1')})
    headers = {
            'Content-Type': 'text/plain'
        }
    response = requests.request("POST", url, headers=headers, data=payload)
    if response.status_code == 200:
            data = response.json()
            messages.success(request, data['message'])
            return redirect('/internal_consumption')
    elif response.status_code == 400:
        data = response.json()
        if data['message'] == 'Sorry! some details are missing':
                messages.error(request, data['message'])
                return redirect('/internal_consumption')
        else:
                messages.error(request, data['message'])
                return redirect('/login')
    else:
        data = response.json()
        messages.error(request, data['message'])
        return redirect('/internal_consumption')



def add_bussupply(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    try:
        role = request.session['role']
        displayrole = request.session['displayrole']
        accesskey = request.session['accesskey']
        menuname = request.session['mylist']
        url = "http://13.235.112.1/ziva/mobile-api/depo-list.php"

        payload = json.dumps({"accesskey": accesskey})
        headers = {
            'Content-Type': 'text/plain'
        }
        response = requests.request("GET", url, headers=headers, data=payload)
        data = response.json()
        depolist = data['depolist']

        url = "http://13.235.112.1/ziva/mobile-api/noofbottleslist.php"

        payload = json.dumps({"accesskey": accesskey})
        headers = {
            'Content-Type': 'text/plain'
        }
        response = requests.request("GET", url, headers=headers, data=payload)
        data = response.json()
        nobot = data['noofbottleslist']
        service = request.POST.get('service')
        if service == 'Extra service':
            service = request.POST.get('exservice')
        else:
            service = request.POST.get('service')
        deponame = request.POST.get('deponame1')
        if deponame:
            deponame = request.POST.get('deponame1')
        else:
            deponame = request.POST.get('depo_name1')

        if role == 'Admin' or role == "Depo":
                if request.method == 'POST':
                    supervisorname = request.POST.get('supervisorid')
                    request.session['supervisorname'] = supervisorname

                    url = "http://13.235.112.1/ziva/mobile-api/internal-consumption-submit-admin.php"
                    payload = json.dumps({"accesskey": accesskey,
                            "deponame":deponame,
                            "busstationid":request.POST.get('supervisorid'),
                            "bus_service_no":service,
                            "oprs":request.POST.get('oprs'),
                            "departure_time":request.POST.get('departure'),
                            "staffnumber":request.POST.get('staffnumb'),
                            "staffname":request.POST.get('staffname'),
                            "vehicleno": request.POST.get('vehicalnumb'),
                            "product_type": request.POST.get('product'),
                            "staffnumbertwo": request.POST.get('staffnumb1'),
                            "staffnametwo": request.POST.get('staffname1'),
                            "route": request.POST.get('route'),
                            "noofbottles":request.POST.get('nobt')})
                    headers = {
                        'Content-Type': 'text/plain'
                    }
                    response = requests.request("POST", url, headers=headers, data=payload)
                    if response.status_code == 200:
                        data = response.json()
                        messages.success(request,data['message'])
                        return redirect('/internal_consumption')
                    elif response.status_code == 400:
                        data = response.json()
                        if data['message'] == 'Sorry! some details are missing':
                            messages.error(request, data['message'])
                            return redirect('/internal_consumption')
                        else:
                            messages.error(request, data['message'])
                            return redirect('/login')
                    else:
                        data = response.json()
                        messages.error(request, data['message'])
                        return redirect('/internal_consumption')
        else:
            if request.method == 'POST':
                url = "http://13.235.112.1/ziva/mobile-api/internal-consumption-submit.php"
                payload = json.dumps({"accesskey": accesskey,
                                      "deponame": request.POST.get('depo_name1'),
                                      "bus_service_no": service,
                                      "oprs": request.POST.get('oprs'),
                                      "departure_time": request.POST.get('departure'),
                                      "staffnumber": request.POST.get('staffnumb'),
                                      "staffname": request.POST.get('staffname'),
                                      "vehicleno": request.POST.get('vehicalnumb'),
                                      "product_type": request.POST.get('product'),
                                      "staffnumbertwo": request.POST.get('staffnumb1'),
                                      "staffnametwo": request.POST.get('staffname1'),
                                      "route": request.POST.get('route'),
                                      "noofbottles": request.POST.get('nobt')})
                headers = {
                    'Content-Type': 'text/plain'
                }
                response = requests.request("POST", url, headers=headers, data=payload)
                if response.status_code == 200:
                    data = response.json()
                    messages.success(request, data['message'])
                    return redirect('/internal_consumption')
                elif response.status_code == 400:
                    data = response.json()
                    if data['message'] == 'Sorry! some details are missing':
                        messages.error(request, data['message'])
                        return redirect('/internal_consumption')
                    else:
                        messages.error(request, data['message'])
                        return redirect('/login')
                else:
                    data = response.json()
                    messages.error(request, data['message'])
                    return redirect('/internal_consumption')
    except:
        return render(request, 'intconsumption/internal_consumption.html', {'menuname': menuname})

def return_bussupply(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    try:
        accesskey = request.session['accesskey']
        menuname = request.session['mylist']
        ticketattach = request.FILES.get("ticketsimg")

        if ticketattach:
            ticketattach_data = base64.b64encode(ticketattach.read())
            ticketattach_name = request.FILES.get("ticketsimg").name

        else:
            ticketattach_data = None
            ticketattach_name = None
        role = request.session['role']
        #displayrole = request.session['displayrole']
        if role == 'Admin' or role == 'Depo':
            busatation_id = request.POST.get('busatation_id1')
            if busatation_id:
                supervisorname = busatation_id
            else:
                supervisorname = request.session['supervisorname']
            url = "http://13.235.112.1/ziva/mobile-api/busservice-supply-logs-return-admin.php"
            payload = {
                "accesskey": accesskey,
                "no_of_tickets": request.POST.get('tickets'),
                "busstationid":supervisorname,
                "return_no_of_bottles": request.POST.get('actbottlesreturn'),
                "return_drivername": request.POST.get('staffname3'),
                "return_drivername_two": request.POST.get('staffname4'),
                "return_staffno": request.POST.get('staffnumret1'),
                "return_staffno_two": request.POST.get('staffnumret2'),
                "service_id": request.POST.get('service_id'),
                "ticketattach": ticketattach_data,
                "ticketattachfilename": ticketattach_name,
            }
        else:
            url = "http://13.235.112.1/ziva/mobile-api/busservice-supply-logs-return.php"
            payload = {
                "accesskey": accesskey,
                "no_of_tickets":request.POST.get('tickets'),
                "return_no_of_bottles":request.POST.get('actbottlesreturn'),
                "return_drivername":request.POST.get('staffname3'),
                "return_drivername_two":request.POST.get('staffname4'),
                "return_staffno": request.POST.get('staffnumret1'),
                "return_staffno_two":request.POST.get('staffnumret2'),
                "service_id":request.POST.get('service_id'),
                "ticketattach":ticketattach_data,
                "ticketattachfilename":ticketattach_name,
            }
        payload = json.dumps(payload, cls=BytesEncoder)
        headers = {
            'Content-Type': 'text/plain'
        }
        response = requests.request("GET", url, headers=headers, data=payload)
        if response.status_code == 200:
            data = response.json()
            response = response.status_code
            data['status'] = response
            return JsonResponse({'response': data})
        elif response.status_code == 400:
            data = response.json()
            if data['message']  == 'Sorry! some details are missing':
                response = response.status_code
                data['status'] = response
                return JsonResponse({'response': data})
            else:
                messages.error(request, data['message'])
                return redirect('/login')
        else:
            data = {'error':'true','message': 'something went wrong'}
            messages.error(request,data['message'])
            return JsonResponse({'response': data})
    except Exception as e:
        data = {'error': 'true', 'message': str(e)}
        messages.error(request, data['message'])
        return JsonResponse({'response': data})


def depo_servicenum(request):

    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')

    accesskey = request.session['accesskey']
    url = "http://13.235.112.1/ziva/mobile-api/depot-service-masterlist.php"

    payload = json.dumps({"depotname": request.POST.get('depo'),
                          "accesskey": accesskey})
    headers = {
        'Content-Type': 'text/plain'
    }
    response = requests.request("GET", url, headers=headers, data=payload)
    if response.status_code == 200:
        data = response.json()
        return JsonResponse({'data':data})
    elif response.status_code == 400:
        data = response.json()
        if data['message'] == 'Sorry! some details are missing':
            return JsonResponse({'data': data})
        else:
            messages.error(request, data['message'])
            return redirect('/login')
    elif response.status_code == 503:
        data = response.json()
        return JsonResponse({'data': data})
    else:
        return redirect('/internal_consumption')


def service_details(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')

    accesskey = request.session['accesskey']
    url = "http://13.235.112.1/ziva/mobile-api/depot-service-dependentlist.php"

    payload = json.dumps({"depotname": request.POST.get('depo'),
                          "serno": request.POST.get('service'),
                          "accesskey": accesskey})
    headers = {
        'Content-Type': 'text/plain'
    }
    response = requests.request("GET", url, headers=headers, data=payload)
    if response.status_code == 200:
        data = response.json()
        servicedependentlist = data['servicedependentlist']
        return JsonResponse({'data':servicedependentlist})
    elif response.status_code == 400:
        data = response.json()
        if data['message'] == 'Sorry! some details are missing':
            return JsonResponse({'data': data})
        else:
            messages.error(request, data['message'])
            return redirect('/login')

    elif response.status_code == 503:
        data = response.json()
        return JsonResponse({'data': data})
    else:
        return redirect('/internal_consumption')


def staffname(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')

    accesskey = request.session['accesskey']
    url = "http://13.235.112.1/ziva/mobile-api/depot-staff-master-name-list.php"

    payload = json.dumps({"depot_name": request.POST.get('depo'),
                          "st_no": request.POST.get('staffnumb'),
                          "accesskey": accesskey})
    headers = {
        'Content-Type': 'text/plain'
    }
    response = requests.request("GET", url, headers=headers, data=payload)
    if response.status_code == 200:
        data = response.json()
        return JsonResponse({'data': data})
    elif response.status_code == 400:
        data = response.json()
        if data['message'] == 'Sorry! some details are missing':
            return JsonResponse({'data': data})
        else:
            messages.error(request, data['message'])
            return redirect('/login')


def staffnumber(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')

    accesskey = request.session['accesskey']
    url = "http://13.235.112.1/ziva/mobile-api/depot-staff-master-staffno-list.php"

    payload = json.dumps({"depot_name":request.POST.get('depo'),
                          "accesskey":accesskey})
    headers = {
        'Content-Type': 'text/plain'
    }
    response = requests.request("GET", url, headers=headers, data=payload)
    if response.status_code == 200:
        data = response.json()
        staffnumberlist = data['staffnumberlist']
        return JsonResponse({'data': staffnumberlist})
    elif response.status_code == 400:
        data = response.json()
        messages.error(request,data['message'])
        return redirect('/login')
    else:
        return redirect('/internal_consumption')


def returnsconsumption(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    try:
        menuname = request.session['mylist']
        accesskey = request.session['accesskey']
        role = request.session['role']
        url = "http://13.235.112.1/ziva/mobile-api/warehousemaster-list.php"
        payload = json.dumps({"accesskey": accesskey})
        headers = {
            'Content-Type': 'text/plain'
        }
        response = requests.request("GET", url, headers=headers, data=payload)
        data = response.json()
        wh_masterlist = data['warehouselist']
        if request.method == 'POST':
            fdate = request.POST.get('fdate')
            tdate = request.POST.get('tdate')
            url = "http://13.235.112.1/ziva/mobile-api/busservices-returnlist.php"
            if role == 'Admin' or role == "Depo":
                payload = json.dumps({
                            "accesskey":accesskey,
                            "depot_id": request.POST.get('depoid1'),
                            "region_id": request.POST.get('regionid1'),
                            "warehouse_id": request.POST.get('warehouseid1'),
                            "fdate":fdate,
                            "tdate":tdate
                })
            else:
                payload = json.dumps({
                    "accesskey": accesskey,
                    "depot_id": "",
                    "region_id": "",
                    "fdate": fdate,
                    "tdate": tdate
                })

            headers = {
                'Content-Type': 'text/plain'
            }
            response = requests.request("GET", url, headers=headers, data=payload)
            if response.status_code == 200:
                data = response.json()
                busservicesupplylist = data['busservicesupplylist']
                return render(request,'intconsumption/return_consumption.html', {'wh_masterlist':wh_masterlist,'menuname': menuname,'data':busservicesupplylist,'fdate':fdate,'tdate':tdate})
            elif response.status_code == 400:
                data = response.json()
                if data['message'] == 'Sorry! some details are missing':
                    response = response.status_code
                    data['status'] = response
                    return render(request, 'intconsumption/return_consumption.html',
                                  {'menuname': menuname, 'fdate': fdate, 'tdate': tdate,'wh_masterlist':wh_masterlist})
                else:
                    messages.error(request, data['message'])
                    return redirect('/login')

            else:
                return render(request, 'intconsumption/return_consumption.html', {'menuname': menuname,'wh_masterlist':wh_masterlist})
        else:
            current_date = datetime.date.today()
            fdate = current_date - timedelta(days=current_date.weekday() + 7)
            fdate = fdate.strftime("%Y-%m-%d")
            tdate = datetime.date.today()
            tdate = tdate.strftime("%Y-%m-%d")
            menuname = request.session['mylist']
            accesskey = request.session['accesskey']
            url = "http://13.235.112.1/ziva/mobile-api/busservices-returnlist.php"

            if role == 'Admin' or role == "Depo":
                payload = json.dumps({
                    "accesskey": accesskey,
                    "depot_id": 'All',
                    "region_id": 'All',
                    "warehouse_id": "All",
                    "fdate": fdate,
                    "tdate": tdate
                })
            else:
                payload = json.dumps({
                    "accesskey": accesskey,
                    "depot_id": "",
                    "region_id": "",
                    "warehouse_id":"",
                    "fdate": fdate,
                    "tdate": tdate
                })
            headers = {
                'Content-Type': 'text/plain'
            }
            response = requests.request("GET", url, headers=headers, data=payload)
            if response.status_code == 200:
                data = response.json()
                busservicesupplylist = data['busservicesupplylist']
                return render(request, 'intconsumption/return_consumption.html',
                              {'wh_masterlist':wh_masterlist,'menuname': menuname, 'data': busservicesupplylist,'fdate':fdate,'tdate':tdate})
            elif response.status_code == 400:
                data = response.json()
                if data['message'] == 'Sorry! some details are missing':
                    response = response.status_code
                    data['status'] = response
                    return render(request, 'intconsumption/return_consumption.html',
                                  {'wh_masterlist':wh_masterlist,'menuname': menuname,'fdate': fdate, 'tdate': tdate})
                else:
                    messages.error(request, data['message'])
                    return redirect('/login')
            elif response.status_code == 503:
                data = response.json()
                messages.error(request, data['message'])
                return render(request, 'intconsumption/return_consumption.html', {'wh_masterlist':wh_masterlist,'menuname': menuname,'fdate':fdate,'tdate':tdate})
            else:
                return render(request, 'intconsumption/return_consumption.html', {'menuname': menuname,'wh_masterlist':wh_masterlist,})
    except:
        if response.status_code == 400:
            data = response.json()
            messages.error(request, data['message'])
            return redirect('/login')
    return render(request, 'intconsumption/intconsump_report.html', {'menuname': menuname})


def intconsump_report(request):
    try:
        if 'accesskey' not in request.session:
            messages.error(request, 'Access denied!')
            return redirect('/login')
        accesskey = request.session['accesskey']
        role = request.session['role']
        depoid = request.session['depoid']
        regionid = request.session['regionid']
        displayrole = request.session['displayrole']
        url = "http://13.235.112.1/ziva/mobile-api/warehousemaster-list.php"
        payload = json.dumps({"accesskey": accesskey})
        headers = {
            'Content-Type': 'text/plain'
        }
        response = requests.request("GET", url, headers=headers, data=payload)
        data = response.json()
        wh_masterlist = data['warehouselist']


        if request.method == 'POST':
            menuname = request.session['mylist']
            accesskey = request.session['accesskey']
            fdate = request.POST.get('fdate')
            tdate = request.POST.get('tdate')
            url = "http://13.235.112.1/ziva/mobile-api/busservices-returnlist-report.php"

            if role == 'Admin':
                payload = json.dumps({
                        "accesskey": accesskey, "fdate": fdate,
                        "depot_id": request.POST.get('depoid1'),
                        "region_id": request.POST.get('regionid1'),
                        "warehouse_id": request.POST.get('warehouseid1'),
                        "tdate": tdate,
                 })
            if displayrole == 'DC CONTROLLER':
                payload = json.dumps({
                        "accesskey": accesskey, "fdate": fdate,
                        "depot_id":depoid,
                        "region_id": 'All',
                        "warehouse_id":'All',
                        "tdate": tdate,
                 })
            if displayrole == 'REGIONAL MANAGER':
                payload = json.dumps({
                    "accesskey": accesskey, "fdate": fdate,
                    "depot_id": request.POST.get('depoid1'),
                    "region_id": regionid,
                    "warehouse_id": "All",
                    "tdate": tdate,
                })
            headers = {
                'Content-Type': 'text/plain'
            }
            response = requests.request("GET", url, headers=headers, data=payload)
            if response.status_code == 200:
                data = response.json()
                busservicesupplylist = data['busservicesupplylist']
                return render(request, 'intconsumption/intconsump_report.html',
                              {'menuname': menuname, 'data': busservicesupplylist, 'fdate': fdate, 'tdate': tdate,'wh_masterlist':wh_masterlist})
            elif response.status_code == 400:
                data = response.json()
                messages.error(request, data['message'])
                return redirect('/login')
            else:
                return render(request, 'intconsumption/intconsump_report.html', {'menuname': menuname,'wh_masterlist':wh_masterlist,'fdate': fdate, 'tdate': tdate})
        else:
            current_date = datetime.date.today()
            fdate = current_date - timedelta(days=current_date.weekday() + 7)
            fdate = fdate.strftime("%Y-%m-%d")
            tdate = datetime.date.today()
            tdate = tdate.strftime("%Y-%m-%d")
            menuname = request.session['mylist']
            accesskey = request.session['accesskey']
            url = "http://13.235.112.1/ziva/mobile-api/busservices-returnlist-report.php"
            if role == 'depo' or displayrole == 'DC CONTROLLER':

                payload = json.dumps({
                    "accesskey": accesskey, "fdate": fdate,
                    "depot_id": depoid,
                    "region_id": "All",
                    "warehouse_id": "All",
                    "tdate": tdate,
                })
            elif displayrole == 'REGIONAL MANAGER':

                payload = json.dumps({
                    "accesskey": accesskey, "fdate": fdate,
                    "depot_id": "All",
                    "region_id":regionid ,
                    "warehouse_id": "All",
                    "tdate": tdate,
                })
            else:
                payload = json.dumps({
                    "accesskey": accesskey,
                    "fdate": fdate,
                    "tdate": tdate,
                    "depot_id": "All",
                    "region_id": "All",
                    "warehouse_id": "All",
                })
            headers = {
                'Content-Type': 'text/plain'
            }
            response = requests.request("GET", url, headers=headers, data=payload)
            if response.status_code == 200:
                data = response.json()
                busservicesupplylist = data['busservicesupplylist']
                return render(request, 'intconsumption/intconsump_report.html',
                              {'menuname': menuname, 'data': busservicesupplylist, 'fdate': fdate, 'tdate': tdate,'wh_masterlist':wh_masterlist})
            elif response.status_code == 400:
                data = response.json()
                messages.error(request, data['message'])
                return redirect('/login')
            elif response.status_code == 503:
                data = response.json()
                messages.error(request, data['message'])
                return render(request, 'intconsumption/intconsump_report.html',
                              {'menuname': menuname, 'fdate': fdate, 'tdate': tdate,'wh_masterlist':wh_masterlist})
            else:
                return render(request, 'intconsumption/intconsump_report.html', {'menuname': menuname,'wh_masterlist':wh_masterlist})
    except:
        if response.status_code == 400:
            data = response.json()
            messages.error(request, data['message'])
            return redirect('/login')
    return render(request, 'intconsumption/intconsump_report.html', {'menuname': menuname})


def vehicallist(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')

    accesskey = request.session['accesskey']
    url = "http://13.235.112.1/ziva/mobile-api/depot_vehicle_masterlist.php"

    payload = json.dumps({"depotname":request.POST.get('depo'),
                          "accesskey":accesskey})
    headers = {
        'Content-Type': 'text/plain'
    }
    response = requests.request("GET", url, headers=headers, data=payload)
    if response.status_code == 200:
        data = response.json()
        return JsonResponse({'data': data})
    elif response.status_code == 400:
        data = response.json()
        if data['message'] == 'Sorry! some details are missing':
            return JsonResponse({'data': data})
        else:
            messages.error(request, data['message'])
            return redirect('/login')
    elif response.status_code == 503:
        data = response.json()
        return JsonResponse({'data': data})
    elif response.status_code == 500:
        data = {'error': 'true', 'message': 'Internal server error'}
        return JsonResponse({'data': data})
    else:
        data = {'error': 'true', 'message': 'something went wrong'}
        return JsonResponse({'data': data})

def producttype(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')

    accesskey = request.session['accesskey']
    url = "http://13.235.112.1/ziva/mobile-api/depot_vehicle_masterlist1.php"

    payload = json.dumps({"depotname": request.POST.get('depo'),
                          "vehicleno":request.POST.get('vehicalnumb'),
                          "accesskey": accesskey})
    headers = {
        'Content-Type': 'text/plain'
    }
    response = requests.request("GET", url, headers=headers, data=payload)
    if response.status_code == 200:
        data = response.json()
        depotvechilemaster = data['depotvechilemaster']
        return JsonResponse({'data': depotvechilemaster})
    elif response.status_code == 400:
        data = response.json()
        messages.error(request, data['message'])
        return redirect('/login')


def create_indent_admin(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    try:
        accesskey = request.session['accesskey']
        menuname = request.session['mylist']

        url = "http://13.235.112.1/ziva/mobile-api/itemmaster-list-new.php"

        payload = json.dumps({"accesskey": accesskey})
        headers = {
            'Content-Type': 'application/json'
        }
        response = requests.request("GET", url, headers=headers, data=payload)
        data = response.json()
        item_masterlist = data['itemmasterlist']

        url = "http://13.235.112.1/ziva/mobile-api/warehousemaster-list.php"

        payload = json.dumps({"accesskey": accesskey})
        headers = {
            'Content-Type': 'text/plain'
        }
        response = requests.request("GET", url, headers=headers, data=payload)

        data = response.json()
        wh_masterlist = data['warehouselist']

        url = "http://13.235.112.1/ziva/mobile-api/depo-list.php"

        payload = json.dumps({"accesskey": accesskey})
        headers = {
            'Content-Type': 'text/plain'
        }
        response = requests.request("GET", url, headers=headers, data=payload)
        data = response.json()
        depolist = data['depolist']
        url = "http://13.235.112.1/ziva/mobile-api/bus-list.php"
        payload = json.dumps({
            "accesskey": accesskey
        })
        headers = {
            'Content-Type': 'application/json'
        }

        response = requests.request("GET", url, headers=headers, data=payload)

        data = response.json()
        bus = data['buslist']
        return render(request,'create_indent/create_indent_admin.html',{'item_masterlist':item_masterlist,'bus':bus,'menuname':menuname,'warehouse':wh_masterlist,'depo':depolist})
    except:
        if response.status_code == '400':
            return redirect('login')
    return render(request, 'create_indent/create_indent_admin.html',{ 'menuname': menuname})

def create_depoindent(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')

    accesskey = request.session['accesskey']
    menuname = request.session['mylist']
    if request.method == 'POST':
        toid = request.POST.get('wh1')
        request.session['toid'] = toid
        url = "http://13.235.112.1/ziva/mobile-api/create-indent-item-admin.php"

        payload = json.dumps({
            "accesskey": accesskey,
            "indentno": "",
            "itemname": request.POST.get('itemname1'),
            "itemcode": request.POST.get('itemcode1'),
            "to_id": request.POST.get('wh1') ,
            "to_name":request.POST.get('whname1'),
            "date ": request.POST.get('getdate1'),
            "qty": request.POST.get('quantity'),
            "mrp": request.POST.get('price'),
            "from_name": request.POST.get('deponame1'),
            "from_id": request.POST.get('depocode1'),
        })
        headers = {
            'Content-Type': 'text/plain'
        }
        response = requests.request("GET", url, headers=headers, data=payload)
        if response.status_code == 200:
            data = response.json()
            id = data['indentno']
            messages.success(request, data['message'])
            url = reverse('indent_item_list', args=[id])
            return redirect(url)
        elif response.status_code == 400:
            data = response.json()
            messages.success(request, data['message'])
            return redirect('/login')
        else:
            try:
                data = response.json()
                messages.error(request, data['message'])
                return redirect('/create_indent_admin')
            except:
                messages.error(request, response.text)
            return redirect('/create_indent_admin')
    else:
        return redirect('/create_indent_admin')

def create_busindent(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')

    accesskey = request.session['accesskey']
    menuname = request.session['mylist']
    if request.method == 'POST':
        toid = request.POST.get('depocode'),
        url = "http://13.235.112.1/ziva/mobile-api/create-indent-item-admin.php"

        payload = json.dumps({
            "accesskey": accesskey,
            "indentno": "",
            "itemname": request.POST.get('itemname2'),
            "itemcode": request.POST.get('itemcode'),
            "to_id": request.POST.get('depocode'),
            "to_name": request.POST.get('deponame'),
            "date ": request.POST.get('date'),
            "qty": request.POST.get('quantity1'),
            "mrp": request.POST.get('mrp2'),
            "from_id": request.POST.get('buscode'),
            "from_name": request.POST.get('busname'),
        })
        headers = {
            'Content-Type': 'text/plain'
        }
        response = requests.request("GET", url, headers=headers, data=payload)
        if response.status_code == 200:
            data = response.json()
            id = data['indentno']
            messages.success(request, data['message'])
            url = reverse('indent_item_list', args=[id])
            return redirect(url)
        elif response.status_code == 400:
            data = response.json()
            messages.error(request, data['message'])
            return redirect('/login')
        else:
            try:
                data = response.json()
                messages.error(request, data['message'])
                return redirect('/create_indent_admin')
            except:
                messages.error(request, response.text)
            return redirect('/create_indent_admin')
    else:
        return redirect('/create_indent_admin')



def get_sms(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    try:
        accesskey = request.session['accesskey']
        url = "http://13.235.112.1/ziva/mobile-api/ziva-sms-new.php"
        mobile = request.POST.get('mobile')
        payload = {"accesskey": accesskey,
                   "service_id": request.POST.get('serviceid1'),
                   "mobile": mobile
                   }
        payload = json.dumps(payload, cls=BytesEncoder)
        headers = {
            'Content-Type': 'application/json'
        }
        response = requests.request("GET", url, headers=headers, data=payload)

        if response.status_code == 200:
            data = response.json()
            response = response.status_code
            data['status'] = response
            return JsonResponse({'response': data})
        elif response.status_code == 400:
            data = response.json()
            if data['message'] == 'Sorry! some details are missing':
                response = response.status_code
                data['status'] = response
                return JsonResponse({'response': data})
            else:
                messages.error(request, data['message'])
                return redirect('/login')
        elif response.status_code == 503:
            data = response.json()
            response = response.status_code
            data['status'] = response
            return JsonResponse({'response': data})
        elif response.status_code == 500:
            response = response.status_code
            response = response.status_code
            messages.error(request, "Internal Server Error")
            return JsonResponse({'response': response})
        else:
            return redirect('/internal_consumption')
    except:
        if response.status_code == 400:
            return redirect('/login')
    return redirect('/internal_consumption')



def return_otp(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    try:
        accesskey = request.session['accesskey']
        url = "http://13.235.112.1/ziva/mobile-api/ziva-sms-return.php"
        mobile = request.POST.get('mobile')
        payload = {"accesskey": accesskey,
                   "service_id": request.POST.get('serviceid1'),
                   "mobile": mobile
                   }
        payload = json.dumps(payload, cls=BytesEncoder)
        headers = {
            'Content-Type': 'application/json'
        }
        response = requests.request("GET", url, headers=headers, data=payload)

        if response.status_code == 200:
            data = response.json()
            response = response.status_code
            data['status'] = response
            return JsonResponse({'response': data})
        elif response.status_code == 400:
            data = response.json()
            if data['message'] == 'Sorry! some details are missing':
                response = response.status_code
                data['status'] = response
                return JsonResponse({'response': data})
            else:
                messages.error(request, data['message'])
                return redirect('/login')
        elif response.status_code == 503:
            data = response.json()
            response = response.status_code
            data['status'] = response
            return JsonResponse({'response': data})
        elif response.status_code == 500:
            response = response.status_code
            response = response.status_code
            messages.error(request, "Internal Server Error")
            return JsonResponse({'response': response})
        else:
            return redirect('/internal_consumption')
    except:
        if response.status_code == 400:
            return redirect('/login')
    return redirect('/internal_consumption')



def submitreturn_sms(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    try:
        accesskey = request.session['accesskey']
        url = "http://13.235.112.1/ziva/mobile-api/driver-return-authorization-otp.php"
        staffno = request.POST.get('auth')
        payload = {"accesskey": accesskey,
                   "service_id": request.POST.get('serviceid1'),
                   "otp": request.POST.get('otp'),
                   "staffno": staffno
                   }
        payload = json.dumps(payload, cls=BytesEncoder)
        headers = {
            'Content-Type': 'application/json'
        }
        response = requests.request("GET", url, headers=headers, data=payload)

        if response.status_code == 200:
            data = response.json()
            response = response.status_code
            data['status'] = response
            return JsonResponse({'response': data})
        elif response.status_code == 400:
            data = response.json()
            if data['message'] == 'Sorry! some details are missing':
                response = response.status_code
                data['status'] = response
                return JsonResponse({'response': data})
            else:
                messages.error(request, data['message'])
                return redirect('/login')
        elif response.status_code == 503:
            data = response.json()
            response = response.status_code
            data['status'] = response
            return JsonResponse({'response': data})
        elif response.status_code == 500:
            response = response.status_code

            messages.error(request, "Internal Server Error")
            return JsonResponse({'response': response})
        else:
            return redirect('/internal_consumption')
    except:
        if response.status_code == 400:
            return redirect('/login')
    return redirect('/internal_consumption')


def submit_sms(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    try:
        accesskey = request.session['accesskey']
        role = request.session['role']
        staffno = request.POST.get('auth')
        busatation_id = request.POST.get('busatation_id')
        displayrole = request.session['displayrole']
        if role == 'Admin' or displayrole == 'DEPO MANAGER':
            if busatation_id:
                supervisorname = busatation_id
            else:
                supervisorname = request.session['supervisorname']

            url = "http://13.235.112.1/ziva/mobile-api/driver-authorization-otp-admin.php"

            payload = {"accesskey": accesskey,
                       "busstationid": supervisorname,
                       "service_id": request.POST.get('serviceid1'),
                       "otp": request.POST.get('otp'),
                       "staffno": staffno
                       }
        else:
            url = "http://13.235.112.1/ziva/mobile-api/driver-authorization-otp.php"

            payload = {"accesskey": accesskey,
                       "service_id": request.POST.get('serviceid1'),
                       "otp": request.POST.get('otp'),
                       "staffno": staffno
                       }
        payload = json.dumps(payload, cls=BytesEncoder)
        headers = {
            'Content-Type': 'application/json'
        }
        response = requests.request("GET", url, headers=headers, data=payload)

        if response.status_code == 200:
            data = response.json()
            response = response.status_code
            data['status'] = response
            return JsonResponse({'response': data})
        elif response.status_code == 400:
            data = response.json()
            if data['message'] == 'Sorry! some details are missing':
                response = response.status_code
                data['status'] = response
                return JsonResponse({'response': data})
            else:
                messages.error(request, data['message'])
                return redirect('/login')
        elif response.status_code == 503:
            data = response.json()
            response = response.status_code
            data['status'] = response
            return JsonResponse({'response': data})
        elif response.status_code == 500:
            response = response.status_code
            messages.error(request, "Internal Server Error")
            return JsonResponse({'response': response})
        else:
            return redirect('/internal_consumption')
    except:
        if response.status_code == 400:
            return redirect('/login')
    return redirect('/internal_consumption')


def authorize_staffid(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    try:
            accesskey = request.session['accesskey']
            url = "http://13.235.112.1/ziva/mobile-api/driver-authorization.php"
            staffno = request.POST.get('auth')
            staffno = base64.b64encode(staffno.encode('utf-8'))
            payload = {"accesskey": accesskey,
                                  "service_id":request.POST.get('serviceid1'),
                                  "staffno": staffno
                                  }
            payload = json.dumps(payload, cls=BytesEncoder)
            headers = {
                'Content-Type': 'application/json'
            }
            response = requests.request("GET", url, headers=headers, data=payload)

            if response.status_code == 200:
                data = response.json()
                response = response.status_code
                data['status'] = response
                return JsonResponse({'response':data})
            elif response.status_code == 400:
                data = response.json()
                if data['message'] == 'Sorry! some details are missing':
                    response = response.status_code
                    data['status'] = response
                    return JsonResponse({'response': data})
                else:
                    messages.error(request, data['message'])
                    return redirect('/login')
            elif response.status_code == 503:
                    data = response.json()
                    response = response.status_code
                    data['status'] = response
                    return JsonResponse({'response': data})
            elif response.status_code == 500:
                response = response.status_code
                response = response.status_code
                messages.error(request,"Internal Server Error")
                return JsonResponse({'response': response})
            else:
                return redirect('/internal_consumption')
    except:
        if response.status_code == 400:
            return redirect('/login')
    return redirect('/internal_consumption')

def depot_dashboard(request):

    try:

        if 'accesskey' not in request.session:
            messages.error(request, 'Access denied!')
            return redirect('/login')
        accesskey = request.session['accesskey']
        role = request.session['role']
        url = "http://13.235.112.1/ziva/mobile-api/itemmaster-list-new.php"

        payload = json.dumps({"accesskey": accesskey})
        headers = {
            'Content-Type': 'application/json'
        }
        response = requests.request("GET", url, headers=headers, data=payload)
        data = response.json()
        item_masterlist = data['itemmasterlist']

        url = "http://13.235.112.1/ziva/mobile-api/depo-list.php"

        payload = json.dumps({"accesskey": accesskey})

        headers = {
            'Content-Type': 'text/plain'
        }
        response = requests.request("GET", url, headers=headers, data=payload)

        data = response.json()
        depolist = data['depolist']

        menuname = request.session['mylist']

        url = "http://13.235.112.1/ziva/mobile-api/warehousemaster-list.php"

        payload = json.dumps({"accesskey": accesskey})
        headers = {
            'Content-Type': 'text/plain'
        }
        response = requests.request("GET", url, headers=headers, data=payload)
        if response.status_code == 200:
            data = response.json()
            wh_masterlist = data['warehouselist']
            if role == 'Admin':
                    return render(request, 'dashboard/depot_admin_dashboard.html', {'depolist':depolist,"menuname": menuname,'wh_masterlist':wh_masterlist,'item_masterlist':item_masterlist})
            else:
                return render(request, 'dashboard/depot_dashboard.html',
                              {"menuname": menuname, 'wh_masterlist': wh_masterlist,
                               'item_masterlist': item_masterlist})
        elif response.status_code == 400:
            data = response.json()
            messages.error(request,data['message'])
            return redirect('login')
    except:
        if response.status_code == 400:
            data = response.json()
            messages.error(request, data['message'])
            return redirect('/login')
    return render(request, 'dashboard/depot_admin_dashboard.html', {"menuname": menuname})



def depot_dashboard_data(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    accesskey = request.session['accesskey']
    role = request.session['role']
    if role == 'Admin':
            url = "http://13.235.112.1/ziva/mobile-api/stock-available-admin-report-new.php"
            payload = {"accesskey": accesskey, "itemcode":request.POST.get('itemcode'), "depoid":request.POST.get('depoid')}
            payload = json.dumps(payload, cls=BytesEncoder)
            headers = {
                'Content-Type': 'application/json'
            }
            response = requests.request("GET", url, headers=headers, data=payload)
            if response.status_code == 200:
                data = response.json()
                return JsonResponse({'data':data})
            elif response.status_code == 400:
                data = response.json()
                if data['message'] == 'Sorry! some details are missing':
                    messages.error(request, data['message'])
                    return JsonResponse({'data':data})
                else:
                    messages.error(request, data['message'])
                    return redirect('\login')
            elif response.status_code == 503:
                data = response.json()
                messages.error(request, data['message'])
                return JsonResponse({'data':data})
            elif response.status_code == 500:
                messages.error(request, "Internal Server Error")
                return JsonResponse({'data':"Internal Server Error"})
    else:
        url = "http://13.235.112.1/ziva/mobile-api/stock-available-report-new.php"
        payload = {"accesskey": accesskey, "itemcode": request.POST.get('itemcode')
                   }
        payload = json.dumps(payload, cls=BytesEncoder)
        headers = {
            'Content-Type': 'application/json'
        }
        response = requests.request("GET", url, headers=headers, data=payload)

        if response.status_code == 200:
            data = response.json()
            return JsonResponse({'data': data})
        elif response.status_code == 400:
            data = response.json()
            if data['message'] == 'Sorry! some details are missing':
                messages.error(request, data['message'])
                return JsonResponse({'data': data})
            else:
                messages.error(request, data['message'])
                return redirect('\login')
        elif response.status_code == 503:
            data = response.json()
            messages.error(request, data['message'])
            return JsonResponse({'data': data})
        elif response.status_code == 500:
            messages.error(request, "Internal Server Error")
            return JsonResponse({'data': "Internal Server Error"})


def internal_consump_stock(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    accesskey = request.session['accesskey']
    depoid = request.session['depoid']
    role = request.session['role']
    diplayrole = request.session['displayrole']
    depot_id = request.POST.get('depoid')
    wh_id = request.POST.get('warehouseid1')
    region_id = request.POST.get('regionid1')
    if role == 'Admin'  or role == 'Depo ' or role == 'Bus Station' or  diplayrole == 'REGIONAL MANAGER':
        url = "http://13.235.112.1/ziva/mobile-api/dc-stock-report.php"
        if role == 'Depo ' or role == 'Bus Station':
            url = "http://13.235.112.1/ziva/mobile-api/dc-stock-report.php"
            payload = { "accesskey": accesskey, 'depoid':depoid }

        elif diplayrole == 'REGIONAL MANAGER':
            regionid = request.session['regionid']
            if depot_id and depot_id !='All':
                url = "http://13.235.112.1/ziva/mobile-api/dc-stock-report.php"
                payload = {"accesskey": accesskey, 'depoid': request.POST.get('depoid')
                           }
            else:
                url = "http://13.235.112.1/ziva/mobile-api/regionwise-deporeport.php"
                payload = {"accesskey": accesskey, 'regionid': regionid
                           }
        else:
            if depot_id :
                url = "http://13.235.112.1/ziva/mobile-api/dc-stock-report.php"
                payload = {"accesskey": accesskey, 'depoid': request.POST.get('depoid')
                   }
            if region_id:
                url = "http://13.235.112.1/ziva/mobile-api/regionwise-deporeport.php"
                payload = {"accesskey": accesskey, 'regionid': request.POST.get('regionid1')
                           }
            if wh_id:
                url = "http://13.235.112.1/ziva/mobile-api/warehousewise-deporeport.php"
                payload = {"accesskey": accesskey, 'warehouseid': request.POST.get('warehouseid1')}

        payload = json.dumps(payload, cls=BytesEncoder)
        headers = {
            'Content-Type': 'application/json'
        }
        response = requests.request("GET", url, headers=headers, data=payload)

        if response.status_code == 200:
            data = response.json()
            return JsonResponse({'data': data})
        elif response.status_code == 400:
            data = response.json()
            if data['message'] == 'Sorry! some details are missing':
                return JsonResponse({'data': data})
            else:
                messages.error(request, data['message'])
                return redirect('\login')
        elif response.status_code == 503:
            data = response.json()
            return JsonResponse({'data': data})
        elif response.status_code == 500:
            messages.error(request, "Internal Server Error")
            return JsonResponse({'data': "Internal Server Error"})

    else:
        url = "http://13.235.112.1/ziva/mobile-api/stock-available-report.php"
        payload = {"accesskey": accesskey
                   }
        payload = json.dumps(payload, cls=BytesEncoder)
        headers = {
            'Content-Type': 'application/json'
        }
        response = requests.request("GET", url, headers=headers, data=payload)

        if response.status_code == 200:
            data = response.json()
            return JsonResponse({'data': data})
        elif response.status_code == 400:
            data = response.json()
            if data['message'] == 'Sorry! some details are missing':
                messages.error(request, data['message'])
                return JsonResponse({'data': data})
            else:
                messages.error(request, data['message'])
                return redirect('\login')
        elif response.status_code == 503:
            data = response.json()
            messages.error(request, data['message'])
            return JsonResponse({'data': data})
        elif response.status_code == 500:
            messages.error(request, "Internal Server Error")
            return JsonResponse({'data': "Internal Server Error"})


def depot_dashboard_data1(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    accesskey = request.session['accesskey']
    role = request.session['role']
    if role == 'Admin':
        url = "http://13.235.112.1/ziva/mobile-api/stock-available-admin-report.php"
        payload = {"accesskey": accesskey,'depoid':request.POST.get('depoid')
                   }
        payload = json.dumps(payload, cls=BytesEncoder)
        headers = {
            'Content-Type': 'applic'
                            'ation/json'
        }
        response = requests.request("GET", url, headers=headers, data=payload)

        if response.status_code == 200:
            data = response.json()
            return JsonResponse({'data': data})
        elif response.status_code == 400:
            data = response.json()
            if data['message'] == 'Sorry! some details are missing':
                messages.error(request, data['message'])
                return JsonResponse({'data': data})
            else:
                messages.error(request, data['message'])
                return redirect('\login')
        elif response.status_code == 503:
            data = response.json()
            messages.error(request, data['message'])
            return JsonResponse({'data': data})
        elif response.status_code == 500:
            messages.error(request, "Internal Server Error")
            return JsonResponse({'data': "Internal Server Error"})

    else:
            url = "http://13.235.112.1/ziva/mobile-api/stock-available-report.php"
            payload = {"accesskey": accesskey

                       }
            payload = json.dumps(payload, cls=BytesEncoder)
            headers = {
                'Content-Type': 'application/json'
            }
            response = requests.request("GET", url, headers=headers, data=payload)


            if response.status_code == 200:
                data = response.json()
                return JsonResponse({'data':data})
            elif response.status_code == 400:
                data = response.json()
                if data['message'] == 'Sorry! some details are missing':
                    messages.error(request, data['message'])
                    return JsonResponse({'data':data})
                else:
                    messages.error(request, data['message'])
                    return redirect('\login')
            elif response.status_code == 503:
                data = response.json()
                messages.error(request, data['message'])
                return JsonResponse({'data':data})
            elif response.status_code == 500:
                messages.error(request, "Internal Server Error")
                return JsonResponse({'data':"Internal Server Error"})

def depot_pendin_sales(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    accesskey = request.session['accesskey']
    role = request.session['role']
    if role == 'Admin':
            url = "http://13.235.112.1/ziva/mobile-api/pending-sales-admin-report.php"
            fdate = request.POST.get('fdate')
            tdate = datetime.date.today()
            tdate = tdate.strftime("%Y-%m-%d")
            if fdate:
                date=fdate
            else:
                date = tdate
            payload = {"accesskey": accesskey,"date":date,"depoid":request.POST.get('depoid')
             }
            payload = json.dumps(payload, cls=BytesEncoder)
            headers = {
                'Content-Type': 'application/json'
            }
            response = requests.request("GET", url, headers=headers, data=payload)

            if response.status_code == 200:
                data = response.json()
                return JsonResponse({'data': data})
            elif response.status_code == 400:
                data = response.json()
                if data['message'] == 'Sorry! some details are missing':
                    messages.error(request, data['message'])
                    return JsonResponse({'data': data})
                else:
                    messages.error(request, data['message'])
                    return redirect('\login')
            elif response.status_code == 503:
                data = response.json()
                messages.error(request, data['message'])
                return JsonResponse({'data': data})
            elif response.status_code == 500:
                messages.error(request, "Internal Server Error")
                return JsonResponse({'data': "Internal Server Error"})
    else:
        url = "http://13.235.112.1/ziva/mobile-api/pending-sales-report.php"
        fdate = request.POST.get('fdate')
        tdate = datetime.date.today()
        tdate = tdate.strftime("%Y-%m-%d")
        if fdate:
            date = fdate
        else:
            date = tdate
        payload = {"accesskey": accesskey, "date": date

                   }
        payload = json.dumps(payload, cls=BytesEncoder)
        headers = {
            'Content-Type': 'application/json'
        }
        response = requests.request("GET", url, headers=headers, data=payload)

        if response.status_code == 200:
            data = response.json()
            return JsonResponse({'data': data})
        elif response.status_code == 400:
            data = response.json()
            if data['message'] == 'Sorry! some details are missing':
                messages.error(request, data['message'])
                return JsonResponse({'data': data})
            else:
                messages.error(request, data['message'])
                return redirect('\login')
        elif response.status_code == 503:
            data = response.json()
            messages.error(request, data['message'])
            return JsonResponse({'data': data})
        elif response.status_code == 500:
            messages.error(request, "Internal Server Error")
            return JsonResponse({'data': "Internal Server Error"})

def complete_sale_report(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    accesskey = request.session['accesskey']
    role = request.session['role']
    if role == 'Admin':
            url = "http://13.235.112.1/ziva/mobile-api/complete-sales-report-admin.php"
            fdate = request.POST.get('cdate')
            tdate = datetime.date.today()
            tdate = tdate.strftime("%Y-%m-%d")
            if fdate:
                date = fdate
            else:
                date = tdate
            payload = {"accesskey": accesskey,"date":date,"depoid":request.POST.get('depoid')
                       }
            payload = json.dumps(payload, cls=BytesEncoder)
            headers = {
                'Content-Type': 'application/json'
            }
            response = requests.request("GET", url, headers=headers, data=payload)

            if response.status_code == 200:
                data = response.json()
                return JsonResponse({'data': data})
            elif response.status_code == 400:
                data = response.json()
                if data['message'] == 'Sorry! some details are missing':
                    messages.error(request, data['message'])
                    return JsonResponse({'data': data})
                else:
                    messages.error(request, data['message'])
                    return redirect('\login')
            elif response.status_code == 503:
                data = response.json()
                messages.error(request, data['message'])
                return JsonResponse({'data': data})
            elif response.status_code == 500:
                messages.error(request, "Internal Server Error")
                return JsonResponse({'data': "Internal Server Error"})
    else:
        url = "http://13.235.112.1/ziva/mobile-api/complete-sales-report.php"
        fdate = request.POST.get('cdate')
        tdate = datetime.date.today()
        tdate = tdate.strftime("%Y-%m-%d")
        if fdate:
            date = fdate
        else:
            date = tdate
        payload = {"accesskey": accesskey, "date": date
                   }
        payload = json.dumps(payload, cls=BytesEncoder)
        headers = {
            'Content-Type': 'application/json'
        }
        response = requests.request("GET", url, headers=headers, data=payload)

        if response.status_code == 200:
            data = response.json()
            return JsonResponse({'data': data})
        elif response.status_code == 400:
            data = response.json()
            if data['message'] == 'Sorry! some details are missing':
                messages.error(request, data['message'])
                return JsonResponse({'data': data})
            else:
                messages.error(request, data['message'])
                return redirect('\login')
        elif response.status_code == 503:
            data = response.json()
            messages.error(request, data['message'])
            return JsonResponse({'data': data})
        elif response.status_code == 500:
            messages.error(request, "Internal Server Error")
            return JsonResponse({'data': "Internal Server Error"})


def bust_dashboard(request):

    try:

        if 'accesskey' not in request.session:
            messages.error(request, 'Access denied!')
            return redirect('/login')
        accesskey = request.session['accesskey']
        role = request.session['role']
        menuname = request.session['mylist']
        url = "http://13.235.112.1/ziva/mobile-api/bus-list.php"
        payload = json.dumps({
            "accesskey": accesskey
        })
        headers = {
            'Content-Type': 'application/json'
        }

        response = requests.request("GET", url, headers=headers, data=payload)
        data = response.json()
        bus = data['buslist']

        url = "http://13.235.112.1/ziva/mobile-api/itemmaster-list-new.php"

        payload = json.dumps({"accesskey": accesskey})
        headers = {
            'Content-Type': 'application/json'
        }
        response = requests.request("GET", url, headers=headers, data=payload)
        data = response.json()
        item_masterlist = data['itemmasterlist']
        url = "http://13.235.112.1/ziva/mobile-api/warehousemaster-list.php"

        payload = json.dumps({"accesskey": accesskey})
        headers = {
            'Content-Type': 'text/plain'
        }
        response = requests.request("GET", url, headers=headers, data=payload)
        if response.status_code == 200:
            data = response.json()
            wh_masterlist = data['warehouselist']
            if role == 'Admin':
                return render(request, 'dashboard/bust_admin_dashboard.html', {"menuname": menuname, 'wh_masterlist': wh_masterlist,'item_masterlist':item_masterlist,'bus':bus})
            else:
                return render(request, 'dashboard/bust_dashboard.html',
                              {"menuname": menuname, 'wh_masterlist': wh_masterlist, 'item_masterlist': item_masterlist,'bus':bus})
        elif response.status_code == 400:
            data = response.json()
            messages.error(request, data['message'])
            return redirect('/login')
    except:

        if response.status_code == 400:
            data = response.json()
            messages.error(request, data['message'])
            return redirect('login')
    return render(request, 'dashboard/bust_dashboard.html',
                  {"menuname": menuname})

def bust_dashboard_data(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    accesskey = request.session['accesskey']
    role=request.session['role']
    if role == 'Admin':
        url = "http://13.235.112.1/ziva/mobile-api/busstation-stock-admin-report.php"
        payload = {"accesskey": accesskey,"busstationid":request.POST.get('busstationid')
                   }
        payload = json.dumps(payload, cls=BytesEncoder)
        headers = {
            'Content-Type': 'application/json'
        }
        response = requests.request("GET", url, headers=headers, data=payload)

        if response.status_code == 200:
            data = response.json()
            return JsonResponse({'data': data})
        elif response.status_code == 400:
            data = response.json()
            if data['message'] == 'Sorry! some details are missing':
                messages.error(request, data['message'])
                return JsonResponse({'data': data})
            else:
                messages.error(request, data['message'])
                return redirect('\login')
        elif response.status_code == 503:
            data = response.json()
            messages.error(request, data['message'])
            return JsonResponse({'data': data})
        elif response.status_code == 500:
            messages.error(request, "Internal Server Error")
            return JsonResponse({'data': "Internal Server Error"})
    else:
        url = "http://13.235.112.1/ziva/mobile-api/busstation-stock-report.php"
        payload = {"accesskey": accesskey,
                   }
        payload = json.dumps(payload, cls=BytesEncoder)
        headers = {
            'Content-Type': 'application/json'
        }
        response = requests.request("GET", url, headers=headers, data=payload)


        if response.status_code == 200:
            data = response.json()
            return JsonResponse({'data':data})
        elif response.status_code == 400:
            data = response.json()
            if data['message'] == 'Sorry! some details are missing':
                messages.error(request, data['message'])
                return JsonResponse({'data':data})
            else:
                messages.error(request, data['message'])
                return redirect('\login')
        elif response.status_code == 503:
            data = response.json()
            messages.error(request, data['message'])
            return JsonResponse({'data':data})
        elif response.status_code == 500:
            messages.error(request, "Internal Server Error")
            return JsonResponse({'data':"Internal Server Error"})


def bust_dashboard_data1(request):
        if 'accesskey' not in request.session:
            messages.error(request, 'Access denied!')
            return redirect('/login')
        accesskey = request.session['accesskey']
        role=request.session['role']
        if role == 'Admin':
            url = "http://13.235.112.1/ziva/mobile-api/busstation-stock-admin-report-new.php"
            payload = {"accesskey": accesskey,"busstationid":request.POST.get('busstationid'), "itemcode":request.POST.get('itemcode'),
                       }
            payload = json.dumps(payload, cls=BytesEncoder)
            headers = {
                'Content-Type': 'application/json'
            }
            response = requests.request("GET", url, headers=headers, data=payload)

            if response.status_code == 200:
                data = response.json()
                return JsonResponse({'data': data})
            elif response.status_code == 400:
                data = response.json()
                if data['message'] == 'Sorry! some details are missing':
                    messages.error(request, data['message'])
                    return JsonResponse({'data': data})
                else:
                    messages.error(request, data['message'])
                    return redirect('\login')
            elif response.status_code == 503:
                data = response.json()
                messages.error(request, data['message'])
                return JsonResponse({'data': data})
            elif response.status_code == 500:
                messages.error(request, "Internal Server Error")
                return JsonResponse({'data': "Internal Server Error"})
        else:
            url = "http://13.235.112.1/ziva/mobile-api/busstation-stock-report-new.php"
            payload = {"accesskey": accesskey,  "itemcode":request.POST.get('itemcode')
                       }
            payload = json.dumps(payload, cls=BytesEncoder)
            headers = {
                'Content-Type': 'application/json'
            }
            response = requests.request("GET", url, headers=headers, data=payload)


            if response.status_code == 200:
                data = response.json()
                return JsonResponse({'data':data})
            elif response.status_code == 400:
                data = response.json()
                if data['message'] == 'Sorry! some details are missing':
                    messages.error(request, data['message'])
                    return JsonResponse({'data':data})
                else:
                    messages.error(request, data['message'])
                    return redirect('\login')
            elif response.status_code == 503:
                data = response.json()
                messages.error(request, data['message'])
                return JsonResponse({'data':data})
            elif response.status_code == 500:
                messages.error(request, "Internal Server Error")
                return JsonResponse({'data':"Internal Server Error"})



def bust_pendin_sales(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    accesskey = request.session['accesskey']
    role = request.session['role']
    if role == 'Admin':
        url = "http://13.235.112.1/ziva/mobile-api/busstation-pending-admin-sales.php"
        fdate = request.POST.get('fdate')
        tdate = datetime.date.today()
        tdate = tdate.strftime("%Y-%m-%d")
        if fdate:
            date = fdate
        else:
            date = tdate
        payload = {
            "accesskey": accesskey, "date": date,"busstationid":request.POST.get('busstationid')

        }
        payload = json.dumps(payload, cls=BytesEncoder)
        headers = {
            'Content-Type': 'application/json'
        }
        response = requests.request("GET", url, headers=headers, data=payload)

        if response.status_code == 200:
            data = response.json()
            return JsonResponse({'data': data})
        elif response.status_code == 400:
            data = response.json()
            if data['message'] == 'Sorry! some details are missing':
                messages.error(request, data['message'])
                return JsonResponse({'data': data})
            else:
                messages.error(request, data['message'])
                return redirect('\login')
        elif response.status_code == 503:
            data = response.json()
            messages.error(request, data['message'])
            return JsonResponse({'data': data})
        elif response.status_code == 500:
            messages.error(request, "Internal Server Error")
            return JsonResponse({'data': "Internal Server Error"})
    else:
            url = "http://13.235.112.1/ziva/mobile-api/busstation-pending-sales.php"
            fdate = request.POST.get('fdate')
            tdate = datetime.date.today()
            tdate = tdate.strftime("%Y-%m-%d")
            if fdate:
                date=fdate
            else:
                date = tdate
            payload = {
                "accesskey": accesskey,"date":date

            }
            payload = json.dumps(payload, cls=BytesEncoder)
            headers = {
                'Content-Type': 'application/json'
            }
            response = requests.request("GET", url, headers=headers, data=payload)

            if response.status_code == 200:
                data = response.json()
                return JsonResponse({'data': data})
            elif response.status_code == 400:
                data = response.json()
                if data['message'] == 'Sorry! some details are missing':
                    messages.error(request, data['message'])
                    return JsonResponse({'data': data})
                else:
                    messages.error(request, data['message'])
                    return redirect('\login')
            elif response.status_code == 503:
                data = response.json()
                messages.error(request, data['message'])
                return JsonResponse({'data': data})
            elif response.status_code == 500:
                messages.error(request, "Internal Server Error")
                return JsonResponse({'data': "Internal Server Error"})



def bust_complete_sale_report(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    accesskey = request.session['accesskey']
    role = request.session['role']
    if role == 'Admin':
        url = "http://13.235.112.1/ziva/mobile-api/busstation-complete-sales-admin.php"
        fdate = request.POST.get('cdate')
        tdate = datetime.date.today()
        tdate = tdate.strftime("%Y-%m-%d")
        if fdate:
            date = fdate
        else:
            date = tdate
        payload = {"accesskey": accesskey, "date": date, "busstationid": request.POST.get('busstationid')
                   }
        payload = json.dumps(payload, cls=BytesEncoder)
        headers = {
            'Content-Type': 'application/json'
        }
        response = requests.request("GET", url, headers=headers, data=payload)

        if response.status_code == 200:
            data = response.json()
            return JsonResponse({'data': data})
        elif response.status_code == 400:
            data = response.json()
            if data['message'] == 'Sorry! some details are missing':
                messages.error(request, data['message'])
                return JsonResponse({'data': data})
            else:
                messages.error(request, data['message'])
                return redirect('\login')
        elif response.status_code == 503:
            data = response.json()
            messages.error(request, data['message'])
            return JsonResponse({'data': data})
        elif response.status_code == 500:
            messages.error(request, "Internal Server Error")
            return JsonResponse({'data': "Internal Server Error"})
    else:
        url = "http://13.235.112.1/ziva/mobile-api/busstation-complete-sales-report.php"
        fdate = request.POST.get('cdate')
        tdate = datetime.date.today()
        tdate = tdate.strftime("%Y-%m-%d")
        if fdate:
            date = fdate
        else:
            date = tdate
        payload = {"accesskey": accesskey,"date":date
                   }
        payload = json.dumps(payload, cls=BytesEncoder)
        headers = {
            'Content-Type': 'application/json'
        }
        response = requests.request("GET", url, headers=headers, data=payload)

        if response.status_code == 200:
            data = response.json()
            return JsonResponse({'data': data})
        elif response.status_code == 400:
            data = response.json()
            if data['message'] == 'Sorry! some details are missing':
                messages.error(request, data['message'])
                return JsonResponse({'data': data})
            else:
                messages.error(request, data['message'])
                return redirect('\login')
        elif response.status_code == 503:
            data = response.json()
            messages.error(request, data['message'])
            return JsonResponse({'data': data})
        elif response.status_code == 500:
            messages.error(request, "Internal Server Error")
            return JsonResponse({'data': "Internal Server Error"})



def zonal_dashboard(request):
    try:
            if 'accesskey' not in request.session:
                messages.error(request, 'Access denied!')
                return redirect('/login')
            menuname = request.session['mylist']
            accesskey = request.session['accesskey']
            role  = request.session['role']
            url = "http://13.235.112.1/ziva/mobile-api/warehousemaster-list.php"

            payload = json.dumps({"accesskey": accesskey})
            headers = {
                'Content-Type': 'text/plain'
            }
            response = requests.request("GET", url, headers=headers, data=payload)

            data = response.json()
            wh_masterlist = data['warehouselist']

            url = "http://13.235.112.1/ziva/mobile-api/itemmaster-list-new.php"

            payload = json.dumps({"accesskey": accesskey})
            headers = {
                'Content-Type': 'application/json'
            }
            response = requests.request("GET", url, headers=headers, data=payload)
            data = response.json()
            item_masterlist = data['itemmasterlist']

            url = "http://13.235.112.1/ziva/mobile-api/depo-list.php"

            payload = json.dumps({"accesskey": accesskey})
            headers = {
                'Content-Type': 'text/plain'
            }
            response = requests.request("GET", url, headers=headers, data=payload)
            if response.status_code == 200:
                data = response.json()
                depolist = data['depolist']
                if role == 'Admin':
                    return render(request, 'dashboard/zonal_dashboard_admin.html', {'wh_masterlist':wh_masterlist,"menuname": menuname,'depolist':depolist,'item_masterlist':item_masterlist})
                else:
                    return render(request, 'dashboard/zonal_dashboard.html',
                                  {'wh_masterlist': wh_masterlist, "menuname": menuname, 'depolist': depolist,
                                   'item_masterlist': item_masterlist})
            elif response.status_code == 400:
                data = response.json()
                messages.error(request,data['message'])
                return redirect('/login')
    except:
        if response.status_code == 400:
            data = response.json()
            messages.error(request, data['message'])
            return redirect('/login')
    return render(request, 'dashboard/zonal_dashboard.html', {"menuname": menuname})

def zonal_dashboard_data1(request):
        if 'accesskey' not in request.session:
            messages.error(request, 'Access denied!')
            return redirect('/login')
        role = request.session['role']
        accesskey = request.session['accesskey']
        if role == 'Admin':
            url = "http://13.235.112.1/ziva/mobile-api/warehouse-stock-admin-report-new.php"
            payload = {"accesskey": accesskey,'itemcode':request.POST.get('itemcode'),
                            "warehouseid":request.POST.get('warehouseid')
                       }
            payload = json.dumps(payload, cls=BytesEncoder)
            headers = {
                'Content-Type': 'application/json'
            }
            response = requests.request("GET", url, headers=headers, data=payload)
            if response.status_code == 200:
                data = response.json()
                return JsonResponse({'data':data})
            elif response.status_code == 400:
                data = response.json()
                if data['message'] == 'Sorry! some details are missing':
                    messages.error(request, data['message'])
                    return JsonResponse({'data':data})
                else:
                    messages.error(request, data['message'])
                    return redirect('\login')
            elif response.status_code == 503:
                data = response.json()
                messages.error(request, data['message'])
                return JsonResponse({'data':data})
            elif response.status_code == 500:
                messages.error(request, "Internal Server Error")
                return JsonResponse({'data':"Internal Server Error"})
        else:
            url = "http://13.235.112.1/ziva/mobile-api/warehouse-stock-report-new.php"
            payload = {"accesskey": accesskey, 'itemcode': request.POST.get('itemcode')
                       }
            payload = json.dumps(payload, cls=BytesEncoder)
            headers = {
                'Content-Type': 'application/json'
            }
            response = requests.request("GET", url, headers=headers, data=payload)
            if response.status_code == 200:
                data = response.json()
                return JsonResponse({'data': data})
            elif response.status_code == 400:
                data = response.json()
                if data['message'] == 'Sorry! some details are missing':
                    messages.error(request, data['message'])
                    return JsonResponse({'data': data})
                else:
                    messages.error(request, data['message'])
                    return redirect('\login')
            elif response.status_code == 503:
                data = response.json()
                messages.error(request, data['message'])
                return JsonResponse({'data': data})
            elif response.status_code == 500:
                messages.error(request, "Internal Server Error")
                return JsonResponse({'data': "Internal Server Error"})


def depots_less_stock(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    accesskey = request.session['accesskey']
    role = request.session['role']
    warehouseid = request.session['warehouseid']
    if role == 'Admin':
        url = "http://13.235.112.1/ziva/mobile-api/depo-lesss-stock-admin.php"
        payload = {"accesskey": accesskey, "warehouseid": request.POST.get('warehouseid')
                   }
        payload = json.dumps(payload, cls=BytesEncoder)

        headers = {
            'Content-Type': 'application/json'
        }
        response = requests.request("GET", url, headers=headers, data=payload)

        if response.status_code == 200:
            data = response.json()
            return JsonResponse({'data': data})
        elif response.status_code == 400:
            data = response.json()
            if data['message'] == 'Sorry! some details are missing':
                messages.error(request, data['message'])
                return JsonResponse({'data': data})
            else:
                messages.error(request, data['message'])
                return redirect('\login')
        elif response.status_code == 503:
            data = response.json()
            messages.error(request, data['message'])
            return JsonResponse({'data': data})
        elif response.status_code == 500:
            messages.error(request, "Internal Server Error")
            return JsonResponse({'data': "Internal Server Error"})
    else:
        url = "http://13.235.112.1/ziva/mobile-api/depo-lesss-stock.php"
        payload = {"accesskey": accesskey,
                   }
        payload = json.dumps(payload, cls=BytesEncoder)

        headers = {
            'Content-Type': 'application/json'
        }
        response = requests.request("GET", url, headers=headers, data=payload)

        if response.status_code == 200:
            data = response.json()
            return JsonResponse({'data': data})
        elif response.status_code == 400:
            data = response.json()
            if data['message'] == 'Sorry! some details are missing':
                messages.error(request, data['message'])
                return JsonResponse({'data': data})
            else:
                messages.error(request, data['message'])
                return redirect('\login')
        elif response.status_code == 503:
            data = response.json()
            messages.error(request, data['message'])
            return JsonResponse({'data': data})
        elif response.status_code == 500:
            messages.error(request, "Internal Server Error")
            return JsonResponse({'data': "Internal Server Error"})



def zonal_dashboard_data(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    accesskey = request.session['accesskey']
    role = request.session['role']
    if role == 'Admin':
        url = "http://13.235.112.1/ziva/mobile-api/warehouse-stock-admin-report.php"
        payload = {"accesskey": accesskey,  "warehouseid":request.POST.get('warehouseid')
                   }
        payload = json.dumps(payload, cls=BytesEncoder)

        headers = {
            'Content-Type': 'application/json'
        }
        response = requests.request("GET", url, headers=headers, data=payload)

        if response.status_code == 200:
            data = response.json()
            return JsonResponse({'data':data})
        elif response.status_code == 400:
            data = response.json()
            if data['message'] == 'Sorry! some details are missing':
                messages.error(request, data['message'])
                return JsonResponse({'data':data})
            else:
                messages.error(request, data['message'])
                return redirect('\login')
        elif response.status_code == 503:
            data = response.json()
            messages.error(request, data['message'])
            return JsonResponse({'data':data})
        elif response.status_code == 500:
            messages.error(request, "Internal Server Error")
            return JsonResponse({'data':"Internal Server Error"})
    else:
        url = "http://13.235.112.1/ziva/mobile-api/warehouse-stock-report.php"
        payload = {"accesskey": accesskey,
                   }
        payload = json.dumps(payload, cls=BytesEncoder)

        headers = {
            'Content-Type': 'application/json'
        }
        response = requests.request("GET", url, headers=headers, data=payload)

        if response.status_code == 200:
            data = response.json()
            return JsonResponse({'data': data})
        elif response.status_code == 400:
            data = response.json()
            if data['message'] == 'Sorry! some details are missing':
                messages.error(request, data['message'])
                return JsonResponse({'data': data})
            else:
                messages.error(request, data['message'])
                return redirect('\login')
        elif response.status_code == 503:
            data = response.json()
            messages.error(request, data['message'])
            return JsonResponse({'data': data})
        elif response.status_code == 500:
            messages.error(request, "Internal Server Error")
            return JsonResponse({'data': "Internal Server Error"})



def zonal_grn_report(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    accesskey = request.session['accesskey']
    warehouseid = request.session['warehouseid']
    role = request.session['role']
    if role == 'Admin':
        url = "http://13.235.112.1/ziva/mobile-api/grn-report.php"
        fdate = request.POST.get('fdate')
        tdate = datetime.date.today()
        tdate = tdate.strftime("%Y-%m-%d")
        if fdate:
            date=fdate
        else:
            date = tdate
        payload = {
            "accesskey": accesskey,"date":date,"warehouseid":request.POST.get('warehouseid')

        }
        payload = json.dumps(payload, cls=BytesEncoder)
        headers = {
            'Content-Type': 'application/json'
        }
        response = requests.request("GET", url, headers=headers, data=payload)

        if response.status_code == 200:
            data = response.json()
            return JsonResponse({'data': data})
        elif response.status_code == 400:
            data = response.json()
            if data['message'] == 'Sorry! some details are missing':
                messages.error(request, data['message'])
                return JsonResponse({'data': data})
            else:
                messages.error(request, data['message'])
                return redirect('\login')
        elif response.status_code == 503:
            data = response.json()
            messages.error(request, data['message'])
            return JsonResponse({'data': data})
        elif response.status_code == 500:
            messages.error(request, "Internal Server Error")
            return JsonResponse({'data': "Internal Server Error"})
    else:
        url = "http://13.235.112.1/ziva/mobile-api/grn-report.php"
        fdate = request.POST.get('fdate')
        tdate = datetime.date.today()
        tdate = tdate.strftime("%Y-%m-%d")
        if fdate:
            date = fdate
        else:
            date = tdate
        payload = {
            "accesskey": accesskey, "date": date, "warehouseid": warehouseid

        }
        payload = json.dumps(payload, cls=BytesEncoder)
        headers = {
            'Content-Type': 'application/json'
        }
        response = requests.request("GET", url, headers=headers, data=payload)

        if response.status_code == 200:
            data = response.json()
            return JsonResponse({'data': data})
        elif response.status_code == 400:
            data = response.json()
            if data['message'] == 'Sorry! some details are missing':
                messages.error(request, data['message'])
                return JsonResponse({'data': data})
            else:
                messages.error(request, data['message'])
                return redirect('\login')
        elif response.status_code == 503:
            data = response.json()
            messages.error(request, data['message'])
            return JsonResponse({'data': data})
        elif response.status_code == 500:
            messages.error(request, "Internal Server Error")
            return JsonResponse({'data': "Internal Server Error"})


def zonal_depotwise_data1(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    accesskey = request.session['accesskey']
    url = "http://13.235.112.1/ziva/mobile-api/depo-stock-available-new.php"
    fdate = request.POST.get('cdate')
    tdate = datetime.date.today()
    tdate = tdate.strftime("%Y-%m-%d")
    if fdate:
        date = fdate
    else:
        date = tdate
    payload = {"accesskey": accesskey,"depoid": request.POST.get('deponame'), "itemcode": request.POST.get('itemcode')
               }
    payload = json.dumps(payload, cls=BytesEncoder)
    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.request("GET", url, headers=headers, data=payload)

    if response.status_code == 200:
        data = response.json()
        return JsonResponse({'data': data})
    elif response.status_code == 400:
        data = response.json()
        if data['message'] == 'Sorry! some details are missing':
            messages.error(request, data['message'])
            return JsonResponse({'data': data})
        else:
            messages.error(request, data['message'])
            return redirect('\login')
    elif response.status_code == 503:
        data = response.json()
        messages.error(request, data['message'])
        return JsonResponse({'data': data})
    elif response.status_code == 500:
        messages.error(request, "Internal Server Error")
        return JsonResponse({'data': "Internal Server Error"})



def zonal_depotwise_data(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    accesskey = request.session['accesskey']
    url = "http://13.235.112.1/ziva/mobile-api/depo-stock-available.php"
    fdate = request.POST.get('cdate')
    tdate = datetime.date.today()
    tdate = tdate.strftime("%Y-%m-%d")
    if fdate:
        date = fdate
    else:
        date = tdate
    payload = {"accesskey": accesskey,"depoid": request.POST.get('deponame')
               }
    payload = json.dumps(payload, cls=BytesEncoder)
    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.request("GET", url, headers=headers, data=payload)

    if response.status_code == 200:
        data = response.json()
        return JsonResponse({'data': data})
    elif response.status_code == 400:
        data = response.json()
        if data['message'] == 'Sorry! some details are missing':
            messages.error(request, data['message'])
            return JsonResponse({'data': data})
        else:
            messages.error(request, data['message'])
            return redirect('\login')
    elif response.status_code == 503:
        data = response.json()
        messages.error(request, data['message'])
        return JsonResponse({'data': data})
    elif response.status_code == 500:
        messages.error(request, "Internal Server Error")
        return JsonResponse({'data': "Internal Server Error"})



def zonal_depotindent_data(request):
        if 'accesskey' not in request.session:
            messages.error(request, 'Access denied!')
            return redirect('/login')
        accesskey = request.session['accesskey']
        url = "http://13.235.112.1/ziva/mobile-api/depo-pending-indent-new-backup.php.php"
        fdate = request.POST.get('inddate')
        tdate = datetime.date.today()
        tdate = tdate.strftime("%Y-%m-%d")
        if fdate:
            date = fdate
        else:
            date = tdate
        payload = {"accesskey": accesskey,"date":date, "depoid": request.POST.get('deponame'),
                   }
        payload = json.dumps(payload, cls=BytesEncoder)
        headers = {
            'Content-Type': 'application/json'
        }
        response = requests.request("GET", url, headers=headers, data=payload)

        if response.status_code == 200:
            data = response.json()
            return JsonResponse({'data': data})
        elif response.status_code == 400:
            data = response.json()
            if data['message'] == 'Sorry! some details are missing':
                return JsonResponse({'data': data})
            else:
                messages.error(request, data['message'])
                return redirect('\login')
        elif response.status_code == 503:
            data = response.json()
            return JsonResponse({'data': data})
        elif response.status_code == 500:
            return JsonResponse({'data': "Internal Server Error"})



def admin_dashboard(request):
    if 'mylist' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    menuname = request.session['mylist']
    return render(request, 'dashboard/admin_dashboard.html', {"menuname": menuname})


def stock_tranfer_admin(request):
    if 'mylist' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    menuname = request.session['mylist']
    accesskey =  request.session['accesskey']
    return render(request,'stock_transfer/stock_transfer_admin.html',{"menuname": menuname})


def generate_transid_depo(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    try:
        menuname = request.session['mylist']
        accesskey = request.session['accesskey']
        fromid = request.POST.get('depotid2')
        request.session['fromid'] = fromid
        url = "http://13.235.112.1/ziva/mobile-api/quantitytypelist.php"
        payload = json.dumps({
            "accesskey": accesskey,

        })
        headers = {
            'Content-Type': 'application/json'
        }
        response = requests.request("GET", url, headers=headers, data=payload)
        data = response.json()
        type1 = data['qtyupdatedlist']
        request.session['type1'] = type1
        url = "http://13.235.112.1/ziva/mobile-api/generate-transitid-admin.php"
        toid = request.POST.get('warehouseid')
        if toid:
            request.session['toid'] = toid
            toid = toid
            toname = request.POST.get('warehousename')
            payload = {
                "accesskey": accesskey,
                "fromid": request.POST.get('depotid2'),
                "fromname": request.POST.get('depotname'),
                "toid": toid,
                "toname": toname,
                "type": "Warehouse"
            }
        else:
            toid = request.POST.get('bustid')
            request.session['toid'] = toid
            toid = toid
            toname = request.POST.get('bustname')

            payload = {
                "accesskey": accesskey,
                "fromid":  request.POST.get('depotid2'),
                "fromname": request.POST.get('depotname'),
                "toid": toid,
                "toname":toname,
                "type": "Bus station"
            }
        payload = json.dumps(payload, cls=BytesEncoder)
        headers = {
            'Content-Type': 'application/json'
        }
        response = requests.request("GET", url, headers=headers, data=payload)

        if response.status_code == 200:
            data = response.json()
            depot_taxinvoice = data['taxinvoice']
            request.session['depot_taxinvoice'] = depot_taxinvoice
            messages.success(request, data['message'])
            return render(request, 'stock_transfer/stock_transfer_admin.html', {'fromid':fromid,'toid':toid,"menuname": menuname, 'response': 'depo200','type':type1})
        elif response.status_code == 400:
            data = response.json()
            if data['message'] == 'Sorry! some details are missing':
                messages.error(request, data['message'])
                return render(request, 'stock_transfer/stock_transfer_admin.html',
                              {"menuname": menuname, 'response': 'depo503'})
            else:
                messages.error(request, data['message'])
                return redirect('\login')
        elif response.status_code == 503:
            data = response.json()
            messages.error(request, data['message'])
            return render(request, 'stock_transfer/stock_transfer_admin.html', {'fromid':fromid,'toid':toid,"menuname": menuname, 'response': 'depo503'})
        elif response.status_code == 500:
            messages.error(request, "Internal Server Error")
            return render(request, 'stock_transfer/stock_transfer_admin.html', {'fromid':fromid,'toid':toid,"menuname": menuname, 'response': 'depo200'})
    except Exception as e:
        messages.error(request, str(e))
        return render(request, 'stock_transfer/stock_transfer_admin.html', {"menuname": menuname, 'response': 'depo400'})


def depot_item_add_admin(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    fromid =    request.session['fromid']
    depot_taxinvoice = request.session['depot_taxinvoice']
    accesskey = request.session['accesskey']

    if request.method == 'POST':
        url = "http://13.235.112.1/ziva/mobile-api/add-stockitem-warehouse-admin.php"

        payload = json.dumps({
            "accesskey": accesskey,
            "noofbottles": request.POST.get('depot_nobt'),
            "type": request.POST.get('depot_typeid'),
            "cp_sno": request.POST.get('depot_sno'),
            "quantity": request.POST.get('depot_quantity'),
            "freeqty": " ",
            "id": fromid,
            "transitid": depot_taxinvoice
        })
        headers = {
            'Content-Type': 'application/json'
        }

        response = requests.request("GET", url, headers=headers, data=payload)
        if response.status_code == 200:
            data = response.json()
            messages.success(request, data['message'])
            return redirect('depot_item_list_admin')
        elif response.status_code == 400:
            data = response.json()
            if data['message'] == 'Sorry! some details are missing':
                messages.error(request, data['message'])
                return redirect('depot_item_list_admin')
            else:
                messages.error(request, data['message'])
                return redirect('/login')
        else:
            try:
                data = response.json()
                messages.error(request, data['message'])
                return redirect('depot_item_list_admin')
            except:
                messages.error(request, response.text)
            return redirect('depot_item_list_admin')

    else:
        return redirect('depot_item_list_admin')



def depot_item_list_admin(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    menuname = request.session['mylist']
    type1 = request.session['type1']
    accesskey = request.session['accesskey']
    depot_taxinvoice  = request.session['depot_taxinvoice']
    fromid = request.session['fromid']
    toid = request.session['toid']
    url = "http://13.235.112.1/ziva/mobile-api/stocktransfer-item-list.php"

    payload = json.dumps({"accesskey":accesskey,
        "transitid":depot_taxinvoice
        })
    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.request("GET", url, headers=headers, data=payload)
    if response.status_code == 200:
        data=response.json()
        wh_item_list=data['stocktransferitemlist']
        return render(request,'stock_transfer/stock_transfer_admin.html',{'fromid':fromid,'toid':toid,'type':type1,'taxinvoice':depot_taxinvoice,'wh_item_list':wh_item_list,'menuname':menuname,'wh':'active','status':'ok','response':'depo200'})
    elif response.status_code == 400:
        data = response.json()
        if data['message'] == 'Sorry! some details are missing':
            messages.error(request, data['message'])
            return render(request,'stock_transfer/stock_transfer_admin.html',{'fromid':fromid,'toid':toid,'type':type1,'taxinvoice':depot_taxinvoice,'menuname':menuname,'status':'ok','response':'depo400'})
        else:
            messages.error(request, data['message'])
            return redirect('/login')
    else:
        return render(request, 'stock_transfer/stock_transfer_admin.html',
                      {'type':type1, 'menuname': menuname,'whtaxinvoice':depot_taxinvoice,'response':'depo200','fromid':fromid,'toid':toid,})

def complete_depostk_admin(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')

    accesskey = request.session['accesskey']
    depot_taxinvoice =  request.session['depot_taxinvoice']
    url = "http://13.235.112.1/ziva/mobile-api/complete-stock.php"

    payload = json.dumps({
        "accesskey": accesskey,
        "transid":depot_taxinvoice,
        "remarks": request.POST.get('remarks'),
        "date": request.POST.get('date'),

    })
    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.request("GET", url, headers=headers, data=payload)
    if response.status_code == 200:
        data = response.json()
        messages.success(request, data['message'])
        return redirect('stock_tranfer_admin')
    elif response.status_code == 400:
        data = response.json()
        messages.error(request, data['message'])
        return render(request, 'login1.html')
    else:
        try:
            data = response.json()
            messages.error(request, data['message'])
            return redirect('stock_tranfer_admin')
        except Exception as e:
            messages.error(request, str(e))
        return redirect('stock_tranfer_admin')


def generate_transid_bust(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    try:
        menuname = request.session['mylist']
        accesskey = request.session['accesskey']
        depotid = request.POST.get('depotid')
        request.session['depotid'] = depotid
        busid1 = request.POST.get('busid1')
        request.session['busid1'] = busid1
        url = "http://13.235.112.1/ziva/mobile-api/quantitytypelist.php"
        payload = json.dumps({
            "accesskey": accesskey,

        })
        headers = {
            'Content-Type': 'application/json'
        }
        response = requests.request("GET", url, headers=headers, data=payload)
        data = response.json()
        type1 = data['qtyupdatedlist']
        request.session['type1'] = type1
        busid1 = request.POST.get('busid1')
        request.session['busid1'] = busid1
        url = "http://13.235.112.1/ziva/mobile-api/generate-transitid-admin.php"
        payload = {
            "accesskey": accesskey,
            "fromid": request.POST.get('busid1'),
            "fromname": request.POST.get('busname1'),
            "toid": depotid,
            "toname": request.POST.get('depotname1'),
            "type": "Depo"
        }
        payload = json.dumps(payload, cls=BytesEncoder)
        headers = {
            'Content-Type': 'application/json'
        }
        response = requests.request("GET", url, headers=headers, data=payload)

        if response.status_code == 200:
            data = response.json()
            bustaxinvoice = data['taxinvoice']
            request.session['bustaxinvoice'] = bustaxinvoice
            messages.success(request, data['message'])
            return render(request, 'stock_transfer/stock_transfer_admin.html', {'depotid':depotid,'busid1':busid1,"menuname": menuname, 'response': 'Bus200','type':type1})
        elif response.status_code == 400:
            data = response.json()
            if data['message'] == 'Sorry! some details are missing':
                messages.error(request, data['message'])
                return render(request, 'stock_transfer/stock_transfer_admin.html',
                              {"menuname": menuname, 'response': 'Bus400'})
            else:
                messages.error(request, data['message'])
                return redirect('\login')
        elif response.status_code == 503:
            data = response.json()
            messages.error(request, data['message'])
            return render(request, 'stock_transfer/stock_transfer_admin.html', {'depotid':depotid,'busid1':busid1,"menuname": menuname, 'response': 'Bus503'})
        elif response.status_code == 500:
            messages.error(request, "Internal Server Error")
            return render(request, 'stock_transfer/stock_transfer_admin.html', {'depotid':depotid,'busid1':busid1,"menuname": menuname, 'response': 'Bus500'})
    except Exception as e:
        messages.error(request, str(e))
        return render(request, 'stock_transfer/stock_transfer_admin.html', {"menuname": menuname, 'response': 'Bus400'})


def bust_item_add_admin(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    busid1 =  request.session['busid1']
    bustaxinvoice = request.session['bustaxinvoice']
    accesskey = request.session['accesskey']

    if request.method == 'POST':
        url = "http://13.235.112.1/ziva/mobile-api/add-stockitem-warehouse-admin.php"

        payload = json.dumps({
            "accesskey": accesskey,
            "noofbottles": request.POST.get('busnobt'),
            "type": request.POST.get('bustypeid'),
            "cp_sno": request.POST.get('buscp_sno'),
            "quantity": request.POST.get('busquantity'),
            "freeqty": " ",
            "id": busid1,
            "transitid": bustaxinvoice
        })
        headers = {
            'Content-Type': 'application/json'
        }

        response = requests.request("GET", url, headers=headers, data=payload)
        if response.status_code == 200:
            data = response.json()
            messages.success(request, data['message'])
            return redirect('bus_item_list_admin')
        elif response.status_code == 503:
            data = response.json()
            messages.error(request, data['message'])
            return redirect('bus_item_list_admin')
        elif response.status_code == 400:
            data = response.json()
            if data['message'] == 'Sorry! some details are missing':
                messages.error(request, data['message'])
                return redirect('bus_item_list_admin')
            else:
                messages.error(request, data['message'])
                return redirect('/login')
        elif response.status_code == 500:
            messages.error(request, 'Internal server error')
            return redirect('stock_tranfer_admin')
        else:
            try:
                data = response.json()
                messages.error(request, data['message'])
                return redirect('bus_item_list_admin')
            except:
                messages.error(request, response.text)
            return redirect('bus_item_list_admin')

    else:
        return redirect('stock_tranfer_admin')



def bus_item_list_admin(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    menuname = request.session['mylist']
    type1 = request.session['type1']
    accesskey = request.session['accesskey']
    bustaxinvoice  = request.session['bustaxinvoice']
    depotid =request.session['depotid']
    busid1 = request.session['busid1']


    url = "http://13.235.112.1/ziva/mobile-api/stocktransfer-item-list.php"

    payload = json.dumps({"accesskey":accesskey,
        "transitid":bustaxinvoice
        })
    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.request("GET", url, headers=headers, data=payload)
    if response.status_code == 200:
        data=response.json()
        wh_item_list=data['stocktransferitemlist']
        return render(request,'stock_transfer/stock_transfer_admin.html',{'depotid':depotid,'busid1':busid1,'type':type1,'taxinvoice':bustaxinvoice,'bus_item_list':wh_item_list,'menuname':menuname,'wh':'active','status':'ok','response':'Bus200'})
    elif response.status_code == 400:
        data = response.json()
        if data['message'] == 'Sorry! some details are missing':
            messages.error(request, data['message'])
            return render(request,'stock_transfer/stock_transfer_admin.html',{'depotid':depotid,'busid1':busid1,'type':type1,'taxinvoice':bustaxinvoice,'menuname':menuname,'wh':'active','status':'ok','response':'Bus200'})
        else:
            messages.error(request, data['message'])
            return redirect('/login')
    else:
        return render(request, 'stock_transfer/stock_transfer_admin.html',
                      {'depotid':depotid,'busid1':busid1,'type':type1, 'menuname': menuname,'whtaxinvoice':bustaxinvoice,'wh':'active','response':'Bus200'})

def generate_transid(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')

    try:
        menuname = request.session['mylist']
        accesskey = request.session['accesskey']


        url = "http://13.235.112.1/ziva/mobile-api/quantitytypelist.php"
        payload = json.dumps({
            "accesskey": accesskey,

        })
        headers = {
            'Content-Type': 'application/json'
        }
        response = requests.request("GET", url, headers=headers, data=payload)
        data = response.json()
        type1 = data['qtyupdatedlist']
        request.session['type1'] = type1
        depocode1 = request.POST.get('depocode1')
        request.session['depocode1'] = depocode1
        wh_code = request.POST.get('wh1')
        request.session['wh_code'] = wh_code
        url = "http://13.235.112.1/ziva/mobile-api/generate-transitid-admin.php"
        payload = {
            "accesskey": accesskey,
            "fromid": request.POST.get('wh1'),
            "fromname": request.POST.get('whname1'),
            "toid": depocode1,
            "toname": request.POST.get('deponame1'),
            "type": "Depo"
        }
        payload = json.dumps(payload, cls=BytesEncoder)
        headers = {
            'Content-Type': 'application/json'
        }
        response = requests.request("GET", url, headers=headers, data=payload)

        if response.status_code == 200:
            data = response.json()
            whtaxinvoice = data['taxinvoice']
            request.session['whtaxinvoice'] = whtaxinvoice
            messages.success(request, data['message'])
            return render(request, 'stock_transfer/stock_transfer_admin.html', {'wh_code':wh_code,'depocode1':depocode1,'type':type1,"menuname": menuname,'response':200,'type':type1})
        elif response.status_code == 400:
            data = response.json()
            if data['message'] == 'Sorry! some details are missing':
                messages.error(request, data['message'])
                return render(request, 'stock_transfer/stock_transfer_admin.html', {'wh_code':wh_code,'depocode1':depocode1,"menuname": menuname,'response':400})
            else:
                messages.error(request, data['message'])
                return redirect('\login')
        elif response.status_code == 503:
            data = response.json()
            messages.error(request, data['message'])
            return render(request, 'stock_transfer/stock_transfer_admin.html', {'wh_code':wh_code,'depocode1':depocode1,"menuname": menuname,'response':503})
        elif response.status_code == 500:
            messages.error(request, "Internal Server Error")
            return render(request, 'stock_transfer/stock_transfer_admin.html', {'wh_code':wh_code,'depocode1':depocode1,"menuname": menuname,'response':500})
    except Exception as e:
        messages.error(request, str(e))
        return render(request, 'stock_transfer/stock_transfer_admin.html', {"menuname": menuname})

def wh_item_add_admin(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    wh_code = request.session['wh_code']
    whtaxinvoice  = request.session['whtaxinvoice']
    accesskey = request.session['accesskey']

    if request.method == 'POST':
        url = "http://13.235.112.1/ziva/mobile-api/add-stockitem-warehouse-admin.php"

        payload = json.dumps({
            "accesskey":accesskey,
            "noofbottles":request.POST.get('nob'),
            "type":request.POST.get('typeid') ,
            "cp_sno": request.POST.get('whcp_sno'),
            "quantity": request.POST.get('quantity'),
            "freeqty":" ",
            "id": wh_code,
            "transitid": whtaxinvoice
        })
        headers = {
            'Content-Type': 'application/json'
        }

        response = requests.request("GET", url, headers=headers, data=payload)
        if response.status_code == 200:
            data = response.json()
            messages.success(request, data['message'])
            return redirect('wh_item_list_admin')
        elif response.status_code == 503:
            data = response.json()
            messages.error(request, data['message'])
            return redirect('wh_item_list_admin')
        elif response.status_code == 400:
            data = response.json()
            messages.error(request, data['message'])
            return render(request, 'login1.html')
        else:
            try:
                data = response.json()
                if data['message'] == 'Sorry! some details are missing':
                    messages.error(request, data['message'])
                    return redirect('wh_item_list_admin')
                else:
                    messages.error(request, data['message'])
                    return redirect('/login')
                messages.error(request, data['message'])
                return redirect('wh_item_list_admin')
            except:
                messages.error(request,response.text)
            return redirect('stock_tranfer_admin')

    else:
        return redirect('stock_tranfer_admin')



def wh_item_list_admin(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    menuname = request.session['mylist']
    type1 = request.session['type1']
    accesskey = request.session['accesskey']
    whtaxinvoice  = request.session['whtaxinvoice']
    wh_code = request.session['wh_code']
    depocode1 = request.session['depocode1']


    url = "http://13.235.112.1/ziva/mobile-api/stocktransfer-item-list.php"

    payload = json.dumps({"accesskey":accesskey,
        "transitid":whtaxinvoice
        })
    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.request("GET", url, headers=headers, data=payload)
    if response.status_code == 200:
        data=response.json()
        wh_item_list=data['stocktransferitemlist']
        return render(request,'stock_transfer/stock_transfer_admin.html',{'wh_code':wh_code,'depocode1':depocode1,'type':type1,'taxinvoice':whtaxinvoice,'wh_item_list':wh_item_list,'menuname':menuname,'wh':'active','status':'ok','response':200})
    elif response.status_code == 400:
        data = response.json()
        if data['message'] == 'Sorry! some details are missing':
            messages.error(request, data['message'])
            return render(request,'stock_transfer/stock_transfer_admin.html',{'wh_code':wh_code,'depocode1':depocode1,'type':type1,'taxinvoice':whtaxinvoice,'menuname':menuname,'wh':'active','status':'ok','response':200})
        else:
            messages.error(request, data['message'])
            return redirect('/login')
    else:
        return render(request, 'stock_transfer/stock_transfer_admin.html',

                      {'wh_code':wh_code,'depocode1':depocode1,'type':type1, 'menuname': menuname,'whtaxinvoice':whtaxinvoice,'wh':'active','response':200})


def intconsump_stocktransfer(request):
    if 'mylist' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    menuname = request.session['mylist']
    return render(request, 'intconsumption/intconsump_stocktransfer.html', {"menuname": menuname})


def intconsump_dashboard(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    try:

        menuname = request.session['mylist']
        accesskey = request.session['accesskey']

        url = "http://13.235.112.1/ziva/mobile-api/depo-list.php"

        payload = json.dumps({"accesskey": accesskey})
        headers = {
            'Content-Type': 'text/plain'
        }
        response = requests.request("GET", url, headers=headers, data=payload)
        data = response.json()
        depolist = data['depolist']

        url = "http://13.235.112.1/ziva/mobile-api/warehousemaster-list.php"

        payload = json.dumps({"accesskey": accesskey})
        headers = {
            'Content-Type': 'text/plain'
        }
        response = requests.request("GET", url, headers=headers, data=payload)
        data = response.json()
        wh_masterlist = data['warehouselist']

        url = "http://13.235.112.1/ziva/mobile-api/itemmaster-list-new.php"

        payload = json.dumps({"accesskey": accesskey})
        headers = {
            'Content-Type': 'application/json'
        }
        response = requests.request("GET", url, headers=headers, data=payload)
        data = response.json()
        item_masterlist = data['itemmasterlist']
        return render(request, 'intconsumption/intconsump_dashboard.html', {"wh_masterlist":wh_masterlist,"menuname": menuname,'depolist':depolist,'item_masterlist':item_masterlist})
    except:
        if response.status_code == 400:
            data = response.json()
            messages.error(request,data['message'])
            return redirect('/login')
    return render(request, 'intconsumption/intconsump_dashboard.html',{"menuname": menuname})



def intconsump_dashboard_data(request):
    if 'mylist' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    accesskey = request.session['accesskey']
    role = request.session['role']
    displayrole = request.session['displayrole']
    fdate = request.POST.get('fdate')
    cdate = request.POST.get('cdate')
    tdate = datetime.date.today()
    tdate = tdate.strftime("%Y-%m-%d")
    if fdate:
        date = fdate
    else:
        date = tdate
    if cdate:
        todate = cdate
    else:
        todate = tdate
    depoid = request.POST.get('depoid')
    warehouseid = request.POST.get('warehousename')
    regionid = request.POST.get('regionname')
    if role == 'Admin':
        if warehouseid:
            url = "http://13.235.112.1/ziva/mobile-api/consum-whdashboard.php"
            payload = {"accesskey": accesskey, "fdate": date, "tdate": todate, "warehouse": warehouseid,
                       }
        if regionid:
            url = "http://13.235.112.1/ziva/mobile-api/consum-regdashboard.php"
            payload = {"accesskey": accesskey, "fdate": date, "tdate": todate, "regionname": regionid,
                       }
        if depoid:
            url = "http://13.235.112.1/ziva/mobile-api/consumption-dashboard.php"
            payload = {"accesskey": accesskey, "fdate": date, "tdate":todate,"deponame":depoid
                       }
        payload = json.dumps(payload, cls=BytesEncoder)
        headers = {
            'Content-Type': 'application/json'
        }
        response = requests.request("GET", url, headers=headers, data=payload)

        if response.status_code == 200:
            data = response.json()
            return JsonResponse({'data': data})
        elif response.status_code == 400:
            data = response.json()
            if data['message'] == 'Sorry! some details are missing':
                messages.error(request, data['message'])
                return JsonResponse({'data': data})
            else:
                messages.error(request, data['message'])
                return redirect('\login')
        elif response.status_code == 503:
            data = response.json()
            messages.error(request, data['message'])
            return JsonResponse({'data': data})
        elif response.status_code == 500:
            messages.error(request, "Internal Server Error")
            return JsonResponse({'data': "Internal Server Error"})
    if displayrole == 'REGIONAL MANAGER':
        regionname = request.session['region']
        url = "http://13.235.112.1/ziva/mobile-api/regionconsumption-dashboard.php"
        payload = {
            "accesskey": accesskey,
            "regionname": regionname,
            "deponame": depoid,
            "fdate": date,
            "tdate": todate
        }
        payload = json.dumps(payload, cls=BytesEncoder)
        headers = {
            'Content-Type': 'application/json'
        }
        response = requests.request("GET", url, headers=headers, data=payload)

        if response.status_code == 200:
            data = response.json()
            return JsonResponse({'data': data})
        elif response.status_code == 400:
            data = response.json()
            if data['message'] == 'Sorry! some details are missing':
                messages.error(request, data['message'])
                return JsonResponse({'data': data})
            else:
                messages.error(request, data['message'])
                return redirect('\login')
        elif response.status_code == 503:
            data = response.json()
            messages.error(request, data['message'])
            return JsonResponse({'data': data})
        elif response.status_code == 500:
            messages.error(request, "Internal Server Error")
            return JsonResponse({'data': "Internal Server Error"})
    if role == 'Depo' or  role == 'Bus Station':
        deponame = request.session['deponame']
        url = "http://13.235.112.1/ziva/mobile-api/consumption-dashboard.php"
        payload = {"accesskey": accesskey, "fdate": date, "tdate": todate, "deponame":deponame
                   }
        payload = json.dumps(payload, cls=BytesEncoder)
        headers = {
            'Content-Type': 'application/json'
        }
        response = requests.request("GET", url, headers=headers, data=payload)

        if response.status_code == 200:
            data = response.json()
            return JsonResponse({'data': data})
        elif response.status_code == 400:
            data = response.json()
            if data['message'] == 'Sorry! some details are missing':
                messages.error(request, data['message'])
                return JsonResponse({'data': data})
            else:
                messages.error(request, data['message'])
                return redirect('\login')
        elif response.status_code == 503:
            data = response.json()
            messages.error(request, data['message'])
            return JsonResponse({'data': data})
        elif response.status_code == 500:
            messages.error(request, "Internal Server Error")
            return JsonResponse({'data': "Internal Server Error"})



def service_wise_shortage(request):
        if 'mylist' not in request.session:
            messages.error(request, 'Access denied!')
            return redirect('/login')
        accesskey = request.session['accesskey']

        url = "http://13.235.112.1/ziva/mobile-api/servicewise-sub-shortagelist.php"
        payload = {"accesskey": accesskey, "service_id": request.POST.get('service_id'),
                    "deponame": request.POST.get('deponame'),"fromdate": request.POST.get('fdate'), "todate": request.POST.get('tdate'),
                   }
        payload = json.dumps(payload, cls=BytesEncoder)
        headers = {
            'Content-Type': 'application/json'
        }
        response = requests.request("GET", url, headers=headers, data=payload)

        if response.status_code == 200:
            data = response.json()
            return JsonResponse({'data': data})
        elif response.status_code == 400:
            data = response.json()
            if data['message'] == 'Sorry! some details are missing':
                messages.error(request, data['message'])
                return JsonResponse({'data': data})
            else:
                messages.error(request, data['message'])
                return redirect('\login')
        elif response.status_code == 503:
            data = response.json()
            messages.error(request, data['message'])
            return JsonResponse({'data': data})
        elif response.status_code == 500:
            messages.error(request, "Internal Server Error")
            return JsonResponse({'data': "Internal Server Error"})



def driverwise_sub_shortage(request):
    if 'mylist' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    accesskey = request.session['accesskey']

    url = "http://13.235.112.1/ziva/mobile-api/sub-shortagelist.php"
    payload = {"accesskey": accesskey,"staff_number":request.POST.get('staffid') ,"fromdate": request.POST.get('fdate') , "todate":request.POST.get('tdate'),
               }
    payload = json.dumps(payload, cls=BytesEncoder)
    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.request("GET", url, headers=headers, data=payload)

    if response.status_code == 200:
        data = response.json()
        return JsonResponse({'data': data})
    elif response.status_code == 400:
        data = response.json()
        if data['message'] == 'Sorry! some details are missing':
            messages.error(request, data['message'])
            return JsonResponse({'data': data})
        else:
            messages.error(request, data['message'])
            return redirect('\login')
    elif response.status_code == 503:
        data = response.json()
        messages.error(request, data['message'])
        return JsonResponse({'data': data})
    elif response.status_code == 500:
        messages.error(request, "Internal Server Error")
        return JsonResponse({'data': "Internal Server Error"})


def driverwise_shortage(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    try:
        accesskey = request.session['accesskey']
        menuname = request.session['mylist']
        role = request.session['role']
        displayrole = request.session['displayrole']
        url = "http://13.235.112.1/ziva/mobile-api/depo-list.php"

        payload = json.dumps({"accesskey": accesskey})
        headers = {
            'Content-Type': 'text/plain'
        }

        response = requests.request("GET", url, headers=headers, data=payload)
        data = response.json()
        depolist = data['depolist']

        payload = json.dumps({"accesskey": accesskey})
        headers = {
            'Content-Type': 'application/json'
        }
        url = "http://13.235.112.1/ziva/mobile-api/region-list.php"
        response = requests.request("POST", url, headers=headers, data=payload)

        data = response.json()
        regionlist = data['regionlist']

        url = "http://13.235.112.1/ziva/mobile-api/dates-filter.php"

        payload = json.dumps({"accesskey": accesskey})
        headers = {
            'Content-Type': 'text/plain'
        }
        response = requests.request("GET", url, headers=headers, data=payload)

        data = response.json()
        selectrange = data['timingslist']
        if request.method == 'POST':
            deponame = request.POST.get('deponame')
            if deponame:
                deponame=deponame
            else:
                deponame = 'All'
            range = request.POST.get('from')
            if range:
                if range == 'Custom Dates':
                    fdate = request.POST.get('fdate')
                    tdate = request.POST.get('tdate')
                else:
                    fdate = request.POST.get('from')
                    tdate = request.POST.get('from')
            else:
                fdate = "Current Month"
                tdate = "Current Month"
            if role == 'Depo' or displayrole == 'DC CONTROLLER':
                deponame = request.session['deponame']
                payload = json.dumps({
                        "accesskey": accesskey,
                        "deponame": deponame,
                        "fromdate":fdate,
                        "todate":tdate,
                })
            else:
                payload = json.dumps({
                    "accesskey": accesskey,
                    "deponame": deponame,
                    "fromdate": fdate,
                    "todate": tdate,
                })
            headers = {
                'Content-Type': 'text/plain'
            }
            url = "http://13.235.112.1/ziva/mobile-api/shortagelist.php"
            response = requests.request("GET", url, headers=headers, data=payload)
            if response.status_code == 200:
                data = response.json()
                itemlist = data['shortagelist']
                return render(request, 'intconsumption/driverwise_shortagereport.html',
                              {'menuname': menuname, 'itemlist': itemlist,'depolist':depolist,'selectrange':selectrange,'fdate':fdate,'tdate':tdate,'regionlist':regionlist})
            else:
                return render(request, 'intconsumption/driverwise_shortagereport.html',
                              {'menuname': menuname,'depolist':depolist,'selectrange':selectrange,'fdate':fdate,'tdate':tdate,'regionlist':regionlist})
        else:

                    url = "http://13.235.112.1/ziva/mobile-api/shortagelist.php"
                    if role == 'Depo' or  displayrole == 'DC CONTROLLER':
                        deponame = request.session['deponame']
                        payload = json.dumps({
                            "accesskey": accesskey,
                            "deponame": deponame,
                            "fromdate": "Current Month",
                            "todate": "Current Month",
                        })
                    else:
                        payload = json.dumps({
                                              "accesskey": accesskey,
                                              "deponame": "All",
                                               "fromdate": "Current Month",
                                               "todate": "Current Month"
                                              })
                    headers = {
                        'Content-Type': 'text/plain'
                    }
                    response = requests.request("GET", url, headers=headers, data=payload)
                    if response.status_code == 200:
                        data = response.json()
                        itemlist = data['shortagelist']
                        return render(request, 'intconsumption/driverwise_shortagereport.html',
                                      {'menuname': menuname, 'itemlist': itemlist,'depolist':depolist,'selectrange':selectrange,'fdate': "Current Month",'tdate': "Current Month",'regionlist':regionlist})
                    else:
                        return render(request, 'intconsumption/driverwise_shortagereport.html',
                                  {'menuname': menuname,'depolist':depolist,'selectrange':selectrange,'fdate': "Current Month",'tdate': "Current Month",'regionlist':regionlist})
    except:
        if response.status_code == 400:
            data = response.json()
            messages.error(request, 'Access denied!')
            return redirect('/login')
    return render(request, 'intconsumption/driverwise_shortagereport.html',
                  {'menuname': menuname})


def servicewise_shortage(request):
    if 'mylist' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    try:
        accesskey = request.session['accesskey']
        menuname = request.session['mylist']
        role = request.session['role']
        displayrole = request.session['displayrole']
        url = "http://13.235.112.1/ziva/mobile-api/depo-list.php"

        payload = json.dumps({"accesskey": accesskey})
        headers = {
            'Content-Type': 'text/plain'
        }

        response = requests.request("GET", url, headers=headers, data=payload)

        data = response.json()
        depolist = data['depolist']

        payload = json.dumps({"accesskey": accesskey})
        headers = {
            'Content-Type': 'application/json'
        }
        url = "http://13.235.112.1/ziva/mobile-api/region-list.php"
        response = requests.request("POST", url, headers=headers, data=payload)

        data = response.json()
        regionlist = data['regionlist']

        url = "http://13.235.112.1/ziva/mobile-api/dates-filter.php"

        payload = json.dumps({"accesskey": accesskey})
        headers = {
            'Content-Type': 'text/plain'
        }
        response = requests.request("GET", url, headers=headers, data=payload)

        data = response.json()
        selectrange = data['timingslist']
        if request.method == 'POST':
            deponame = request.POST.get('deponame')
            if deponame:
                deponame = deponame
            else:
                deponame = 'All'
            range = request.POST.get('from')


            if range:
                if range == 'Custom Dates':
                    fdate = request.POST.get('fdate')
                    tdate = request.POST.get('tdate')
                else:
                    fdate = request.POST.get('from')
                    tdate = request.POST.get('from')
            else:
                fdate = "Current Month"
                tdate = "Current Month"
            if role == 'Depo' or displayrole == 'DC CONTROLLER':
                depoid = request.session['deponame']
                payload = json.dumps({
                    "accesskey": accesskey,
                    "deponame": depoid,
                    "service_id": "All",
                    "fromdate": fdate,
                    "todate": tdate
                })
            else:
                payload = json.dumps({
                        "accesskey": accesskey,
                        "service_id": "All",
                        "deponame": deponame,
                        "fromdate": fdate,
                        "todate": tdate,
                })

            headers = {
                'Content-Type': 'text/plain'
            }
            url = "http://13.235.112.1/ziva/mobile-api/servicewise-shortagelist.php"
            response = requests.request("GET", url, headers=headers, data=payload)
            if response.status_code == 200:
                data = response.json()
                itemlist = data['shortagelist']
                return render(request, 'intconsumption/servicewise_shortage.html',
                              {'menuname': menuname, 'itemlist': itemlist, 'depolist': depolist, 'fdate': fdate,
                               'tdate': tdate,'selectrange':selectrange,'regionlist':regionlist})
            else:
                return render(request, 'intconsumption/servicewise_shortage.html',
                              {'regionlist':regionlist,'menuname': menuname, 'depolist': depolist, 'fdate': fdate, 'tdate': tdate,'selectrange':selectrange})
        else:
            url = "http://13.235.112.1/ziva/mobile-api/servicewise-shortagelist.php"
            if role == 'Depo' or displayrole == 'DC CONTROLLER':
                depoid=request.session['deponame']
                payload = json.dumps({
                    "accesskey": accesskey,
                    "deponame": depoid,
                    "service_id":"All",
                    "fromdate":"Current Month",
                    "todate":"Current Month"
                })
            else:
                payload = json.dumps({
                    "accesskey": accesskey,
                    "deponame": "All",
                    "service_id": "All",
                    "fromdate": "Current Month",
                    "todate": "Current Month"
                })
            headers = {
                'Content-Type': 'text/plain'
            }
            response = requests.request("GET", url, headers=headers, data=payload)
            if response.status_code == 200:
                data = response.json()
                itemlist = data['shortagelist']
                return render(request, 'intconsumption/servicewise_shortage.html',
                              {'menuname': menuname,'regionlist':regionlist, 'itemlist': itemlist, 'depolist': depolist,'selectrange':selectrange,'fdate':"Current Month",'tdate':"Current Month"})
            else:
                return render(request, 'intconsumption/servicewise_shortage.html',
                              {'menuname': menuname, 'regionlist':regionlist,'depolist': depolist,'selectrange':selectrange,'fdate':"Current Month",'tdate':"Current Month"})
    except:
        if response.status_code == 400:
            data = response.json()
            messages.error(request,data['message'])
            return redirect('/login')
    return render(request, 'intconsumption/servicewise_shortage.html',
                  {'menuname': menuname})



def internal_stktransfer(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    try:
        accesskey = request.session['accesskey']
        menuname = request.session['mylist']
        role = request.session['role']

        url = "http://13.235.112.1/ziva/mobile-api/depo-list.php"

        payload = json.dumps({"accesskey": accesskey})
        headers = {
                'Content-Type': 'text/plain'
            }
        response = requests.request("GET", url, headers=headers, data=payload)
        data = response.json()
        depolist = data['depolist']


        if role == 'Admin':
                url = "http://13.235.112.1/ziva/mobile-api/depo-list.php"

                payload = json.dumps({"accesskey": accesskey})
                headers = {
                    'Content-Type': 'text/plain'
                }
                response = requests.request("GET", url, headers=headers, data=payload)
                data = response.json()
                depolist = data['depolist']
                if request.method == 'POST':
                    url = "http://13.235.112.1/ziva/mobile-api/stock-transfer-internal-admin.php"

                    payload = json.dumps({

                        "accesskey": accesskey,
                        "fromname": request.POST.get('depot_name'),
                        "fromid": request.POST.get('depotid'),
                        "toname": request.POST.get('stockpoint_name'),
                        "toid": request.POST.get('stockpoint'),
                        "quantity": request.POST.get('quantity'),
                        "noofbottles":request.POST.get('nob')
                    })
                    headers = {
                        'Content-Type': 'application/json'
                    }
                    response = requests.request("GET", url, headers=headers, data=payload)
                    if response.status_code == 200:
                        data = response.json()
                        messages.success(request, data['message'] + " " + "and transitid is" + data['transitid'])
                        return render(request, 'intconsumption/internal_stktransfer.html',
                                      {"menuname": menuname, 'depolist':depolist})
                    elif response.status_code == 400:
                        data = response.json()
                        if data['message'] == 'Sorry! some details are missing':
                            messages.error(request, data['message'])
                            return render(request, 'intconsumption/internal_stktransfer.html',
                                          {"menuname": menuname, 'depolist':depolist})
                        else:
                            messages.error(request, data['message'])
                            return redirect('/login')
                    elif response.status_code == 503:
                        data = response.json()
                        messages.error(request, data['message'])
                        return render(request, 'intconsumption/internal_stktransfer.html',
                                      {"menuname": menuname, 'depolist':depolist})
                else:
                    return render(request,'intconsumption/internal_stktransfer.html',{"menuname":menuname,'depolist':depolist})
        else:
            url = "http://13.235.112.1/ziva/mobile-api/internal-consumption-stockpoints.php"

            payload = json.dumps({
                "accesskey": accesskey,
                "depoid": ""
            })

            headers = {
                'Content-Type': 'application/json'
            }
            response = requests.request("GET", url, headers=headers, data=payload)
            data1 = response.json()
            stockpointlist = data1['stockpointlist']

            if request.method == 'POST':
                url = "http://13.235.112.1/ziva/mobile-api/stock-transfer-internal.php"

                payload = json.dumps({

                    "accesskey": accesskey,
                    "toname": request.POST.get('stockpoint_name'),
                    "toid": request.POST.get('stockpoint'),
                    "quantity": request.POST.get('quantity'),
                    "noofbottles": request.POST.get('nob')
                })
                headers = {
                    'Content-Type': 'application/json'
                }
                response = requests.request("GET", url, headers=headers, data=payload)
                if response.status_code == 200:
                    data = response.json()
                    messages.success(request, data['message'] + " " + "and transitid is" + data['transitid'])
                    return render(request, 'intconsumption/internal_stktransfer.html',
                                  {"menuname": menuname, 'stockpointlist': stockpointlist, 'depolist': depolist})
                elif response.status_code == 400:
                    data = response.json()
                    if data['message'] == 'Sorry! some details are missing':
                        messages.error(request, data['message'])
                        return render(request, 'intconsumption/internal_stktransfer.html',
                                      {"menuname": menuname, 'stockpointlist': stockpointlist})
                    else:
                        messages.error(request, data['message'])
                        return redirect('/login')
                elif response.status_code == 503:
                    data = response.json()
                    messages.error(request, data['message'])
                    return render(request, 'intconsumption/internal_stktransfer.html',
                                  {"menuname": menuname, 'stockpointlist': stockpointlist})
            else:
                return render(request, 'intconsumption/internal_stktransfer.html',
                              {"menuname": menuname, 'stockpointlist': stockpointlist})
    except:
        if response.status_code == 400:
            data = response.json()
            messages.error(request, data['message'])
            return redirect('/login')
    return render(request, 'intconsumption/internal_stktransfer.html', {"menuname": menuname})

def delete_sales(request):
    if 'accesskey' not in request.session:
            return redirect('/login')
    accesskey = request.session['accesskey']
    url = "http://13.235.112.1/ziva/mobile-api/delete-delivery-pending-list-region.php"

    payload = json.dumps({
            "accesskey": accesskey,
            "sonumber": request.POST.get('deletesono'),
        })
    headers = {
            'Content-Type': 'application/json'
        }

    response = requests.request("POST", url, headers=headers, data=payload)
    if response.status_code == 200:
            data = response.json()
            messages.success(request, data['message'])
            return redirect('medeliver_challan_pending')
    else:
            try:
                data = response.json()
                messages.error(request, data['message'])
                return redirect('medeliver_challan_pending')
            except:
                messages.error(request, response.text)
            return redirect('medeliver_challan_pending')

def delete_deliverchallan(request):
    if 'accesskey' not in request.session:
        return redirect('/login')
    accesskey = request.session['accesskey']
    url = "http://13.235.112.1/ziva/mobile-api/delete-deliverchallan.php"

    payload = json.dumps({
        "accesskey": accesskey,
        "sonumber": request.POST.get('deletesono'),
    })
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    if response.status_code == 200:
        data = response.json()
        messages.success(request, data['message'])
        return redirect('sales_admin_list')
    else:
        try:
            data = response.json()
            messages.error(request, data['message'])
            return redirect('sales_admin_list')
        except:
            messages.error(request, response.text)
        return redirect('sales_admin_list')



def delete_pendindent(request):
    if 'accesskey' not in request.session:
        return redirect('/login')
    accesskey = request.session['accesskey']
    status = request.POST.get('deletestatus')
    if status == 'Pending':
        url = "http://13.235.112.1/ziva/mobile-api/delete-indent-admin.php"
        payload = json.dumps({
            "accesskey": accesskey,
            "indentno": request.POST.get('deletesono'),
        })
        headers = {
            'Content-Type': 'application/json'
        }

        response = requests.request("POST", url, headers=headers, data=payload)
        if response.status_code == 200:
            data = response.json()
            messages.success(request, data['message'])
            return redirect('pending_indent_admin')
        else:
            try:
                data = response.json()
                messages.error(request, data['message'])
                return redirect('pending_indent_admin')
            except:
                messages.error(request, response.text)
            return redirect('pending_indent_admin')
    else:
        url = "http://13.235.112.1/ziva/mobile-api/delete-indent-admin.php"
        payload = json.dumps({
            "accesskey": accesskey,
            "indentno": request.POST.get('deletesono'),
        })
        headers = {
            'Content-Type': 'application/json'
        }

        response = requests.request("POST", url, headers=headers, data=payload)
        if response.status_code == 200:
            data = response.json()
            messages.success(request, data['message'])
            return redirect('ready_toship_admin')
        else:
            try:
                data = response.json()
                messages.error(request, data['message'])
                return redirect('ready_toship_admin')
            except:
                messages.error(request, response.text)
            return redirect('ready_toship_admin')

def delete_intconsumption(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    accesskey = request.session['accesskey']
    url = "http://13.235.112.1/ziva/mobile-api/delete-busservicesupply-admin.php"
    id = request.POST.get('deletesono')
    payload = json.dumps({
        "accesskey": accesskey,
        "service_id": id,
    })
    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.request("GET", url, headers=headers, data=payload)
    if response.status_code == 200:
        data = response.json()
        messages.success(request, data['message'])
        return redirect('/internal_consumption')
    elif response.status_code == 400:
        data = response.json()
        if data['message'] == 'Sorry! some details are missing':
            messages.error(request, data['message'])
            return redirect('/internal_consumption')
        else:
            messages.error(request, data['message'])
            return redirect('/login')
    else:
        try:
            data = response.json()
            messages.error(request, data['message'])
        except:
            messages.error(request, response.text)
        return redirect('/internal_consumption')


def service_master(request):
    try:
        if 'accesskey' not in request.session:
            messages.error(request, 'Access denied!')
            return redirect('/login')

        accesskey = request.session['accesskey']
        menuname = request.session['mylist']
        url = "http://13.235.112.1/ziva/mobile-api/depo-list.php"

        payload = json.dumps({"accesskey": accesskey})
        headers = {
            'Content-Type': 'text/plain'
        }
        response = requests.request("GET", url, headers=headers, data=payload)
        data = response.json()
        depolist = data['depolist']
        if request.method == 'POST':
            url = "http://13.235.112.1/ziva/mobile-api/service-masterlist.php"

            payload = json.dumps({"accesskey": accesskey,"depot_name":request.POST.get('deponame1')})
            headers = {
                'Content-Type': 'text/plain'
            }
            response = requests.request("GET", url, headers=headers, data=payload)
            if response.status_code == 200:
                data = response.json()
                servicemasterlist = data['servicemasterlist']
                return render(request, 'masters/service_master.html', {"menuname": menuname,'depolist':depolist,"servicemasterlist":servicemasterlist})
            elif response.status_code == 400:
                data = response.json()
                if data['message'] == 'Sorry! some details are missing':
                    messages.error(request, data['message'])
                    return render(request, 'masters/service_master.html', {"menuname": menuname, 'depolist': depolist})
                else:
                    messages.error(request, data['message'])
                    return redirect('/login')
            else:
                return render(request, 'masters/service_master.html', {"menuname": menuname, 'depolist': depolist})
        else:
            url = "http://13.235.112.1/ziva/mobile-api/service-masterlist.php"

            payload = json.dumps({"accesskey": accesskey, "depot_name": "HAKEEMPET"})
            headers = {
                'Content-Type': 'text/plain'
            }
            response = requests.request("GET", url, headers=headers, data=payload)
            if response.status_code == 200:
                data = response.json()
                servicemasterlist = data['servicemasterlist']
                return render(request, 'masters/service_master.html',
                              {"menuname": menuname, 'depolist': depolist, "servicemasterlist": servicemasterlist})
            elif response.status_code == 400:
                data = response.json()
                if data['message'] == 'Sorry! some details are missing':
                    messages.error(request, data['message'])
                    return render(request, 'masters/service_master.html', {"menuname": menuname, 'depolist': depolist})
                else:
                    messages.error(request, data['message'])
                    return redirect('/login')
            else:
                return render(request, 'masters/service_master.html', {"menuname": menuname, 'depolist': depolist})

    except Exception as e:
        if response.status_code == 400:
            data = response.json()
            messages.error(request, data['message'])
            return redirect('/login')
        else:
            messages.error(request, str(e))
            return render(request, 'masters/service_master.html', {"menuname": menuname})

def add_service_master(request):
        if 'accesskey' not in request.session:
            messages.error(request, 'Access denied!')
            return redirect('/login')
        accesskey = request.session['accesskey']
        if request.method == 'POST':
            url = "http://13.235.112.1/ziva/mobile-api/service-master-submit.php"

            payload = json.dumps({"accesskey": accesskey, "depot_name": request.POST.get('deponame'),
                                  "ser_no": request.POST.get('service'),
                                  "oprs": request.POST.get('oprs'),
                                  "depot": request.POST.get('departure'),
                                  "route": request.POST.get('route'),
                                  "oprs_I": request.POST.get('oprs'),
                                  "depot_code": ""
                                  })
            headers = {
                'Content-Type': 'text/plain',
            }
            response = requests.request("GET", url, headers=headers, data=payload)
            if response.status_code == 200:
                data = response.json()
                messages.success(request, data['message'])
                return redirect('/service_master')
            elif response.status_code == 400:
                data = response.json()
                text = data['message']
                if 'some details are missing' in text:
                    messages.error(request, data['message'])
                    return redirect('/service_master')
                else:
                    messages.error(request, data['message'])
                    return redirect('/login')
            else:
                return redirect('/service_master')

        else:
            return redirect('/service_master')

def get_servicelist(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    accesskey = request.session['accesskey']
    service_id = request.POST.get('service_id')
    deponame = request.POST.get('deponame')
    url = "http://13.235.112.1/ziva/mobile-api/service-masterlist.php"

    payload = json.dumps({
        "accesskey": accesskey, "depot_name": deponame
    })

    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    if response.status_code == 200:
        data = response.json()
        servicemasterlist = data['servicemasterlist']
        for i in servicemasterlist:
            if str(i['ser_no']) == service_id:
                data = {"sno": i["sno"], "depot_name": i["depot_name"], "ser_no": i["ser_no"], "oprs": i['oprs'],
                        "depot": i['depot'], "route": i['route']}
        return JsonResponse({'data': data})
    elif response.status_code == 400:
        data = response.json()
        if data['message'] == 'Sorry! some details are missing':
            messages.error(request, data['message'])
            return redirect('/service_master')
        else:
            messages.error(request, data['message'])
            return redirect('/login')
    else:
        try:
            data = response.json()
            messages.error(request, data['message'])
        except:
            messages.error(request, response.text)
        return redirect('/service_master')


def edit_service(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    accesskey = request.session['accesskey']
    if request.method == 'POST':
        url = "http://13.235.112.1/ziva/mobile-api/edit-service-master.php"

        payload = json.dumps({"accesskey": accesskey,
                              "depot_name": request.POST.get('depotid1'),
                              "ser_no": request.POST.get('service1'),
                              "oprs": request.POST.get('oprs1'),
                              "depot": request.POST.get('departuretime1'),
                              "route": request.POST.get('route1'),
                              "sno": request.POST.get('sno')
                              })
        headers = {
            'Content-Type': 'text/plain',
        }
        response = requests.request("GET", url, headers=headers, data=payload)
        if response.status_code == 200:
            data = response.json()
            messages.success(request, data['message'])
            return redirect('/service_master')
        elif response.status_code == 400:
            data = response.json()
            text = data['message']
            if   'some details are missing' in text:
                messages.error(request, data['message'])
                return redirect('/service_master')
            else:
                messages.error(request, data['message'])
                return redirect('/login')
        else:
            try:
                r = response.json()
                messages.error(request, r['message'])
            except:
                messages.error(request, response.text)
            return redirect('/service_master')

    else:
        return redirect('/service_master')

def edit_vehcle(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    accesskey = request.session['accesskey']
    if request.method == 'POST':
        url = "http://13.235.112.1/ziva/mobile-api/edit-vehiclemaster.php"

        payload = json.dumps({"accesskey": accesskey,
                              "depotname":request.POST.get('depotname1'),
                              "vehicleno": request.POST.get('vehicleno1'),
                              "product_type": request.POST.get('product1'),
                              "depotcode": "",
                              "sno":request.POST.get('sno')
                              })
        headers = {
            'Content-Type': 'text/plain',
        }
        response = requests.request("GET", url, headers=headers, data=payload)
        if response.status_code == 200:
            data = response.json()
            messages.success(request, data['message'])

            return redirect('/vehical_master')
        elif response.status_code == 400:
            data = response.json()
            text = data['message']
            if  'some details are missing' in text:
                messages.error(request, data['message'])
                return redirect('/vehical_master')
            else:
                messages.error(request, data['message'])
                return redirect('/login')
        else:
            try:
                r = response.json()
                messages.error(request, r['message'])
            except:
                messages.error(request, response.text)
            return redirect('/vehical_master')
    else:
        return redirect('/vehical_master')


def vehical_master(request):
    try:
        if 'accesskey' not in request.session:
            messages.error(request, 'Access denied!')
            return redirect('/login')

        accesskey = request.session['accesskey']
        menuname = request.session['mylist']

        url = "http://13.235.112.1/ziva/mobile-api/depo-list.php"

        payload = json.dumps({"accesskey": accesskey})
        headers = {
            'Content-Type': 'text/plain'
        }
        response = requests.request("GET", url, headers=headers, data=payload)
        data = response.json()
        depolist = data['depolist']

        if request.method == 'POST':
            url = "http://13.235.112.1/ziva/mobile-api/vehicle-masterslist.php"

            payload = json.dumps({"accesskey": accesskey,"depotname":request.POST.get('deponame1')})
            headers = {
                'Content-Type': 'text/plain'
            }
            response = requests.request("GET", url, headers=headers, data=payload)
            if response.status_code == 200:
                data = response.json()
                vehiclemasterlist = data['vehiclemasterlist']
                return render(request, 'masters/vehical_master.html', {"menuname": menuname,'depolist':depolist,"vehiclemasterlist":vehiclemasterlist})
            elif response.status_code == 400:
                data = response.json()
                if data['message'] == 'Sorry! some details are missing':
                    messages.error(request, data['message'])
                    return render(request, 'masters/vehical_master.html', {"menuname": menuname, 'depolist': depolist})
                else:
                    messages.error(request, data['message'])
                    return redirect('/login')
            else:
                    return render(request, 'masters/vehical_master.html', {"menuname": menuname, 'depolist': depolist})
        else:
            url = "http://13.235.112.1/ziva/mobile-api/vehicle-masterslist.php"

            payload = json.dumps({"accesskey": accesskey,"depotname":"HAKEEMPET"})
            headers = {
                'Content-Type': 'text/plain'
            }
            response = requests.request("GET", url, headers=headers, data=payload)
            if response.status_code == 200:
                data = response.json()
                vehiclemasterlist = data['vehiclemasterlist']
                return render(request, 'masters/vehical_master.html',
                              {"menuname": menuname, 'depolist': depolist, "vehiclemasterlist": vehiclemasterlist})
            elif response.status_code == 400:
                data = response.json()
                if data['message'] == 'Sorry! some details are missing':
                    messages.error(request, data['message'])
                    return render(request, 'masters/vehical_master.html', {"menuname": menuname, 'depolist': depolist})
                else:
                    messages.error(request, data['message'])
                    return redirect('/login')
            else:
                return render(request, 'masters/vehical_master.html', {"menuname": menuname, 'depolist': depolist})
    except Exception as e:
        if response.status_code == 400:
            data = response.json()
            messages.error(request, data['message'])
            return redirect('/login')
        else:
            messages.error(request, str(e))
            return render(request, 'masters/vehical_master.html', {"menuname": menuname})


def add_vehical_master(request):
        if 'accesskey' not in request.session:
            messages.error(request, 'Access denied!')
            return redirect('/login')
        accesskey = request.session['accesskey']
        if request.method == 'POST':
            url = "http://13.235.112.1/ziva/mobile-api/vehicle-master-submit.php"

            payload = json.dumps({"accesskey": accesskey, "depotname": request.POST.get('deponame'),
                                  "vehicleno": request.POST.get('vehicleno'),
                                  "product_type": request.POST.get('product'),
                                  })
            headers = {
                'Content-Type': 'text/plain',
            }
            response = requests.request("GET", url, headers=headers, data=payload)
            if response.status_code == 200:
                data = response.json()
                messages.success(request, data['message'])
                return redirect('/vehical_master')
            elif response.status_code == 400:
                data = response.json()
                if data['message'] == 'Sorry! some details are missing':
                    messages.error(request, data['message'])
                    return JsonResponse({'data': data})
                else:
                    messages.error(request, data['message'])
                    return redirect('/login')
            else:
                return redirect('/vehical_master')

        else:
            return redirect('/vehical_master')



def get_vehicle(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    accesskey = request.session['accesskey']
    vehicle = request.POST.get('vehicle')
    deponame = request.POST.get('deponame')
    url = "http://13.235.112.1/ziva/mobile-api/vehicle-masterslist.php"

    payload = json.dumps({
        "accesskey": accesskey, "depotname":deponame
    })

    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    if response.status_code == 200:
        data = response.json()
        vehiclemasterlist = data['vehiclemasterlist']
        for i in vehiclemasterlist:
            if str(i['vehicleno']) == vehicle:
                data = {"sno": i["sno"], "depot_name": i["depotname"], "vehicleno": i["vehicleno"], "product_type": i['product_type']}
        return JsonResponse({'data': data})
    elif response.status_code == 400:
        data = response.json()
        if data['message'] == 'Sorry! some details are missing':
            messages.error(request, data['message'])
            return redirect('/vehical_master')
        else:
            messages.error(request, data['message'])
            return redirect('/login')
    else:
        try:
            data = response.json()
            messages.error(request, data['message'])
            return redirect('/vehical_master')
        except:
            messages.error(request, response.text)
        return redirect('/vehical_master')



def driver_master(request):
    try:
        if 'accesskey' not in request.session:
            messages.error(request, 'Access denied!')
            return redirect('/login')

        accesskey = request.session['accesskey']
        menuname = request.session['mylist']
        url = "http://13.235.112.1/ziva/mobile-api/depo-list.php"

        payload = json.dumps({"accesskey": accesskey})
        headers = {
            'Content-Type': 'text/plain'
        }
        response = requests.request("GET", url, headers=headers, data=payload)
        data = response.json()
        depolist = data['depolist']
        if request.method == 'POST':
            url = "http://13.235.112.1/ziva/mobile-api/staff-masterlist.php"

            payload = json.dumps({"accesskey": accesskey,"deponame":request.POST.get('deponame1')})
            headers = {
                'Content-Type': 'text/plain'
            }
            response = requests.request("GET", url, headers=headers, data=payload)
            if response.status_code == 200:
                data = response.json()
                stafflist = data['staffmasterlist']
                return render(request, 'masters/driver_master.html', {"menuname": menuname,'depolist':depolist,"stafflist":stafflist})
            elif response.status_code == 400:
                data = response.json()
                if data['message'] == 'Sorry! some details are missing':
                    messages.error(request, data['message'])
                    return render(request, 'masters/driver_master.html', {"menuname": menuname, 'depolist': depolist})
                else:
                    messages.error(request, data['message'])
                    return redirect('/login')
            else:
                try:
                    data = response.json()
                    messages.error(request, data['message'])
                except:
                    messages.error(request,response.text)
                return render(request, 'masters/driver_master.html', {"menuname": menuname, 'depolist': depolist})
        else:
            url = "http://13.235.112.1/ziva/mobile-api/staff-masterlist.php"

            payload = json.dumps({"accesskey": accesskey, "deponame": "HAKEEMPET"})
            headers = {
                'Content-Type': 'text/plain'
            }
            response = requests.request("GET", url, headers=headers, data=payload)
            if response.status_code == 200:
                data = response.json()
                stafflist = data['staffmasterlist']
                return render(request, 'masters/driver_master.html',
                              {"menuname": menuname, 'depolist': depolist, "stafflist": stafflist})
            elif response.status_code == 400:
                data = response.json()
                if data['message'] == 'Sorry! some details are missing':
                    messages.error(request, data['message'])
                    return render(request, 'masters/driver_master.html', {"menuname": menuname, 'depolist': depolist})
                else:
                    messages.error(request, data['message'])
                    return redirect('/login')
            else:
                return render(request, 'masters/driver_master.html', {"menuname": menuname, 'depolist': depolist})

    except Exception as e:
        if response.status_code == 400:
            data = response.json()
            messages.error(request, data['message'])
            return redirect('/login')
        else:
            messages.error(request, str(e))
            return render(request, 'masters/driver_master.html', {"menuname": menuname})
def dgt_master(request):
    try:
        if 'accesskey' not in request.session:
            messages.error(request, 'Access denied!')
            return redirect('/login')

        accesskey = request.session['accesskey']
        menuname = request.session['mylist']
        url = "http://13.235.112.1/ziva/mobile-api/depo-list.php"

        payload = json.dumps({"accesskey": accesskey})
        headers = {
            'Content-Type': 'text/plain'
        }
        response = requests.request("GET", url, headers=headers, data=payload)
        data = response.json()
        depolist = data['depolist']
        if request.method == 'POST':
            url = "http://13.235.112.1/ziva/mobile-api/dgtvehicle-masterslist.php"

            payload = json.dumps({"accesskey": accesskey, "depotname": request.POST.get('deponame1')})
            headers = {
                'Content-Type': 'text/plain'
            }
            response = requests.request("GET", url, headers=headers, data=payload)
            if response.status_code == 200:
                data = response.json()
                dgtmasterlist = data['dgtmasterlist']
                return render(request, 'masters/dgt_master.html',
                              {"menuname": menuname, 'depolist': depolist, "dgtmasterlist": dgtmasterlist})
            elif response.status_code == 400:
                data = response.json()
                if data['message'] == 'Sorry! some details are missing':
                    messages.error(request, data['message'])
                    return render(request, 'masters/dgt_master.html', {"menuname": menuname, 'depolist': depolist})
                else:
                    messages.error(request, data['message'])
                    return redirect('/login')
            else:
                return render(request, 'masters/dgt_master.html', {"menuname": menuname, 'depolist': depolist})
        else:
            url = "http://13.235.112.1/ziva/mobile-api/dgtvehicle-masterslist.php"

            payload = json.dumps({"accesskey": accesskey, "depotname": "HAKEEMPET"})
            headers = {
                'Content-Type': 'text/plain'
            }
            response = requests.request("GET", url, headers=headers, data=payload)
            if response.status_code == 200:
                data = response.json()
                dgtmasterlist = data['dgtmasterlist']
                return render(request, 'masters/dgt_master.html',
                              {"menuname": menuname, 'depolist': depolist, "dgtmasterlist": dgtmasterlist})
            elif response.status_code == 400:
                data = response.json()
                if data['message'] == 'Sorry! some details are missing':
                    messages.error(request, data['message'])
                    return render(request, 'masters/dgt_master.html', {"menuname": menuname, 'depolist': depolist})
                else:
                    messages.error(request, data['message'])
                    return redirect('/login')
            else:
                return render(request, 'masters/dgt_master.html', {"menuname": menuname, 'depolist': depolist})

    except Exception as e:
        if response.status_code == 400:
            data = response.json()
            messages.error(request, data['message'])
            return redirect('/login')
        else:
            messages.error(request, str(e))
            return render(request, 'masters/dgt_master.html', {"menuname": menuname})

def add_dgt_master(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    accesskey = request.session['accesskey']
    if request.method == 'POST':
        url = "http://13.235.112.1/ziva/mobile-api/create-dgtmaster.php"

        payload = json.dumps({"accesskey": accesskey,
                              "depotname": request.POST.get('deponame'),
                              "vehicleno": request.POST.get('vehicle'),
                              "department": request.POST.get('department')
                              })
        headers = {
            'Content-Type': 'text/plain',
        }
        response = requests.request("GET", url, headers=headers, data=payload)
        if response.status_code == 200:
            data = response.json()
            messages.success(request, data['message'])
            return redirect('/dgt_master')
        elif response.status_code == 400:
            data = response.json()
            text = data['message']
            if 'some details are missing' in text:
                messages.error(request, data['message'])
                return redirect('/dgt_master')
            else:
                messages.error(request, data['message'])
                return redirect('/login')
        else:
            try:
                data = response.json()
                messages.error(request, data['message'])
                return redirect('/dgt_master')
            except:
                messages.error(request,response.text)
                return redirect('/dgt_master')

    else:
        return redirect('/dgt_master')


def add_driver_master(request):
        if 'accesskey' not in request.session:
            messages.error(request, 'Access denied!')
            return redirect('/login')
        accesskey = request.session['accesskey']
        if request.method == 'POST':
            url = "http://13.235.112.1/ziva/mobile-api/staff_master_submit.php"

            payload = json.dumps({"accesskey": accesskey,"deponame": request.POST.get('deponame'),
                "st_no": request.POST.get('driverid'),
                "name": request.POST.get('drivername'),
                "phone_no": request.POST.get('mobile'),
                "designation": request.POST.get('designation'),
            })
            headers = {
                'Content-Type': 'text/plain',
            }
            response = requests.request("GET", url, headers=headers, data=payload)
            if response.status_code == 200:
                data = response.json()
                messages.success(request,data['message'])
                return redirect('/driver_master')
            elif response.status_code == 400:
                data = response.json()
                text = data['message']
                if 'some details are missing' in text:
                    messages.error(request, data['message'])
                    return redirect('/driver_master')
                else:
                    messages.error(request, data['message'])
                    return redirect('/login')
            else:
                return redirect('/driver_master')

        else:
            return redirect('/driver_master')


def get_driver(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    accesskey = request.session['accesskey']
    staffid = request.POST.get('st_no')
    deponame = request.POST.get('deponame')
    url = "http://13.235.112.1/ziva/mobile-api/staff-masterlist.php"

    payload = json.dumps({
        "accesskey": accesskey, "deponame":deponame
    })

    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    if response.status_code == 200:
        data = response.json()
        staffmasterlist = data['staffmasterlist']
        for i in staffmasterlist:
            if str(i['st_no']) == staffid:
                data = {"sno": i["sno"], "depot_name": i["depot_name"], "st_no": i["st_no"], "name": i['name'], "mobile": i['phone_no'], "designation": i['designation']}
        return JsonResponse({'data': data})
    elif response.status_code == 400:
        data = response.json()
        messages.error(request, data['message'])
        return render(request, 'login1.html')
    else:
        try:
            data = response.json()
            messages.error(request, data['message'])
            return redirect('/driver_master')
        except:
            messages.error(request, response.text)
        return redirect('/driver_master')


def edit_driver(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    accesskey = request.session['accesskey']
    if request.method == 'POST':
        url = "http://13.235.112.1/ziva/mobile-api/staff_master_update.php"

        payload = json.dumps({"accesskey": accesskey,
                              "deponame": request.POST.get('depotname'),
                              "st_no": request.POST.get('driverid'),
                              "name": request.POST.get('drivername'),
                              "phone_no": request.POST.get('mobile'),
                              "designation": request.POST.get('designation'),
                              "sno": request.POST.get('sno')
                              })
        headers = {
            'Content-Type': 'text/plain',
        }
        response = requests.request("GET", url, headers=headers, data=payload)
        if response.status_code == 200:
            data = response.json()
            messages.success(request, data['message'])
            return redirect('/driver_master')
        elif response.status_code == 400:
            data = response.json()
            text = data['message']
            if 'some details are missing' in text:
                messages.error(request, data['message'])
                return redirect('/driver_master')
            else:
                messages.error(request, data['message'])
                return redirect('/login')
        else:
            try:
                r = response.json()
                messages.error(request, r['message'])
            except:
                messages.error(request, response.text)
            return redirect('/driver_master')
    else:
        return redirect('/driver_master')


def delete_driver(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    accesskey = request.session['accesskey']
    if request.method == 'POST':
        url = "http://13.235.112.1/ziva/mobile-api/delete-staffmaster.php"

        payload = json.dumps({"accesskey": accesskey,
                              "sno": request.POST.get('id')
                              })
        headers = {
            'Content-Type': 'text/plain',
        }
        response = requests.request("GET", url, headers=headers, data=payload)
        if response.status_code == 200:
            data = response.json()
            messages.success(request, data['message'])
            return redirect('/driver_master')
        elif response.status_code == 400:
            data = response.json()
            if data['message'] == 'Sorry! some details are missing':
                messages.error(request, data['message'])
                return redirect('/driver_master')
            else:
                messages.error(request, data['message'])
                return redirect('/login')
        else:
            return redirect('/driver_master')
    else:
        return redirect('/driver_master')


def delete_vehicle(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    accesskey = request.session['accesskey']
    if request.method == 'POST':
        url = "http://13.235.112.1/ziva/mobile-api/delete-vehiclemaster.php"

        payload = json.dumps({"accesskey": accesskey,
                              "sno": request.POST.get('id1')
                              })
        headers = {
            'Content-Type': 'text/plain',
        }
        response = requests.request("GET", url, headers=headers, data=payload)
        if response.status_code == 200:
            data = response.json()
            messages.success(request, data['message'])
            return redirect('/vehical_master')
        elif response.status_code == 400:
            data = response.json()
            if data['message'] == 'Sorry! some details are missing':
                messages.error(request, data['message'])
                return redirect('/vehical_master')
            else:
                messages.error(request, data['message'])
                return redirect('/login')
        else:
            return redirect('/vehical_master')
    else:
        return redirect('/vehical_master')

def delete_service(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    accesskey = request.session['accesskey']
    if request.method == 'POST':
        url = "http://13.235.112.1/ziva/mobile-api/delete-servicemaster.php"

        payload = json.dumps({"accesskey": accesskey,
                              "sno": request.POST.get('id1')
                              })
        headers = {
            'Content-Type': 'text/plain',
        }
        response = requests.request("GET", url, headers=headers, data=payload)
        if response.status_code == 200:
            data = response.json()
            messages.success(request, data['message'])
            return redirect('/service_master')
        elif response.status_code == 400:
            data = response.json()
            if data['message'] == 'Sorry! some details are missing':
                messages.error(request, data['message'])
                return redirect('/service_master')
            else:
                messages.error(request, data['message'])
                return redirect('/login')
        else:
            return redirect('/service_master')
    else:
        return redirect('/service_master')


def intconsumption_report(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')

    try:
        accesskey = request.session['accesskey']
        menuname = request.session['mylist']

        url = "http://13.235.112.1/ziva/mobile-api/warehousemaster-list.php"

        payload = json.dumps({"accesskey": accesskey})
        headers = {
            'Content-Type': 'text/plain'
        }
        response = requests.request("GET", url, headers=headers, data=payload)
        if response.status_code == 200:
            data = response.json()
            wh_masterlist = data['warehouselist']

        payload = json.dumps({"accesskey": accesskey})
        headers = {
            'Content-Type': 'application/json'
        }
        url = "http://13.235.112.1/ziva/mobile-api/region-list.php"
        response = requests.request("POST", url, headers=headers, data=payload)
        if response.status_code == 200:
            data = response.json()
            regionlist = data['regionlist']

        url = "http://13.235.112.1/ziva/mobile-api/depo-list.php"

        payload = json.dumps({"accesskey": accesskey})
        headers = {
            'Content-Type': 'text/plain'
        }
        response = requests.request("GET", url, headers=headers, data=payload)
        if response.status_code == 200:
            data = response.json()
            depolist = data['depolist']
        if request.method == 'POST':
            depot_id =  request.POST.get('depoid1')
            warehouse_id = request.POST.get('warehouseid1')
            region_id =  request.POST.get('regionid1')
            fdate = request.POST.get('fdate')
            tdate = request.POST.get('ldate')
            if warehouse_id:
                url = "http://13.235.112.1/ziva/mobile-api/warehousewise-stockissue-list.php"

                payload = json.dumps({"accesskey": accesskey,
                                      "warehouse_id":warehouse_id,
                                      "fdate": request.POST.get('fdate'),
                                      "tdate": request.POST.get('ldate')
                                      })
            if region_id:
                url = "http://13.235.112.1/ziva/mobile-api/regionwise-stockissue-list.php"

                payload = json.dumps({"accesskey": accesskey,
                                      "region_id": request.POST.get('regionid1'),
                                      "fdate": request.POST.get('fdate'),
                                      "tdate": request.POST.get('ldate')
                                      })
            if depot_id:

                url = "http://13.235.112.1/ziva/mobile-api/depowise-stockissue-list.php"

                payload = json.dumps({"accesskey": accesskey,
                                      "depot_id": request.POST.get('depoid1'),
                                      "fdate": request.POST.get('fdate'),
                                      "tdate": request.POST.get('ldate')
                                      })

            headers = {
                'Content-Type': 'text/plain'
            }
            response = requests.request("GET", url, headers=headers, data=payload)
            if response.status_code == 200:
                data = response.json()
                servicereportslist = data['servicereportslist']
                return render(request,'intconsumption/intconsumption_report.html',{'fdate':fdate,'tdate':tdate,"menuname":menuname,'wh_masterlist':wh_masterlist,'servicereportslist':servicereportslist,'regionlist':regionlist,'depolist':depolist})
            elif response.status_code == 400:
                data = response.json()
                if data['message'] == 'Sorry! some details are missing':
                    messages.error(request, data['message'])
                    return render(request, 'intconsumption/intconsumption_report.html',
                              {'fdate':fdate,'tdate':tdate,"menuname": menuname, 'wh_masterlist': wh_masterlist,
                               'regionlist': regionlist, 'depolist': depolist})
                else:
                    messages.error(request, data['message'])
                    return redirect('/login')
            else:
                    return render(request, 'intconsumption/intconsumption_report.html',
                                  {"menuname": menuname, 'wh_masterlist': wh_masterlist,
                                   'fdate': fdate,'tdate': tdate, 'regionlist': regionlist, 'depolist': depolist})
        else:
            current_date = datetime.date.today()
            fdate = current_date - timedelta(days=current_date.weekday() + 7)
            fdate = fdate.strftime("%Y-%m-%d")
            tdate = datetime.date.today()
            tdate = tdate.strftime("%Y-%m-%d")
            url = "http://13.235.112.1/ziva/mobile-api/depowise-stockissue-list.php"

            payload = json.dumps({"accesskey": accesskey,
                                      "depot_id": 'All',
                                      "fdate": fdate,
                                      "tdate": tdate
                                      })
            headers = {
                'Content-Type': 'text/plain'
            }
            response = requests.request("GET", url, headers=headers, data=payload)
            if response.status_code == 200:
                data = response.json()
                servicereportslist = data['servicereportslist']
                return render(request, 'intconsumption/intconsumption_report.html',
                              {'fdate': fdate, 'tdate': tdate, "menuname": menuname, 'wh_masterlist': wh_masterlist,
                               'servicereportslist': servicereportslist, 'regionlist': regionlist, 'depolist': depolist})
            elif response.status_code == 400:
                data = response.json()
                if data['message'] == 'Sorry! some details are missing':
                    messages.error(request, data['message'])
                    return render(request, 'intconsumption/intconsumption_report.html',
                                  {'fdate': fdate, 'tdate': tdate, "menuname": menuname, 'wh_masterlist': wh_masterlist,
                                   'regionlist': regionlist, 'depolist': depolist})
                else:
                    messages.error(request, data['message'])
                    return redirect('/login')
            else:
                return render(request, 'intconsumption/intconsumption_report.html',
                              {"menuname": menuname, 'wh_masterlist': wh_masterlist,
                               'fdate': fdate, 'tdate': tdate, 'regionlist': regionlist, 'depolist': depolist})
    except:
        if response.status_code == 400:
            messages.error(request, data['message'])
            return redirect('/login')
    return render(request, 'intconsumption/intconsumption_report.html',{"menuname":menuname})


def intconsumption_servicereport(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    try:
        accesskey = request.session['accesskey']
        menuname = request.session['mylist']
        regionid=request.session['regionid']
        displayrole = request.session['displayrole']
        role = request.session['role']

        url = "http://13.235.112.1/ziva/mobile-api/warehousemaster-list.php"

        payload = json.dumps({"accesskey": accesskey})
        headers = {
            'Content-Type': 'text/plain'
        }
        response = requests.request("GET", url, headers=headers, data=payload)
        if response.status_code == 200:
            data = response.json()
            wh_masterlist = data['warehouselist']

        if request.method == 'POST':
            fdate =  request.POST.get('fdate')
            tdate = request.POST.get('ldate')
            url = "http://13.235.112.1/ziva/mobile-api/internal-consumption-report.php"
            if role == 'Admin':
                payload = json.dumps({"accesskey": accesskey,
                                      "depot_id": request.POST.get('depoid1'),
                                      "region_id": request.POST.get('regionid1'),
                                      "warehouse_id":request.POST.get('warehouseid1'),
                                      "fdate": request.POST.get('fdate'),
                                      "tdate": request.POST.get('ldate'),
                              })
            if displayrole == 'REGIONAL MANAGER':
                payload = json.dumps({"accesskey": accesskey,
                                      "depot_id": request.POST.get('depoid1'),
                                      "region_id":regionid ,
                                      "warehouse_id":"All",
                                      "fdate": request.POST.get('fdate'),
                                      "tdate": request.POST.get('ldate'),
                                      })
                headers = {
                'Content-Type': 'text/plain'
            }
            response = requests.request("GET", url, headers=headers, data=payload)
            if response.status_code == 200:
                data = response.json()
                intercondepowiselist = data['internalconsumptionlist']
                return render(request, 'intconsumption/intconsumption_servicereport.html',
                              {"menuname": menuname, 'wh_masterlist': wh_masterlist,
                               "intercondepowiselist": intercondepowiselist, "fdate":fdate,
                                   "tdate": tdate})
            elif response.status_code == 400:
                data = response.json()
                if data['message'] == 'Sorry! some details are missing':
                    messages.error(request, data['message'])
                    return render(request, 'intconsumption/intconsumption_servicereport.html',
                                  {"menuname": menuname, 'wh_masterlist': wh_masterlist, "fdate":fdate,
                                   "tdate": tdate
                                 })
                else:
                    messages.error(request, data['message'])
                    return redirect('/login')
            else:
                return render(request, 'intconsumption/intconsumption_servicereport.html',
                              {"menuname": menuname, 'wh_masterlist': wh_masterlist, "fdate":fdate,
                                   "tdate": tdate
                              })
        else:
            tdate = datetime.date.today()
            tdate = tdate.strftime("%Y-%m-%d")
            url = "http://13.235.112.1/ziva/mobile-api/internal-consumption-report.php"

            payload = json.dumps({"accesskey": accesskey,
                                    "depot_id": "All",
                                    "region_id": "All",
                                    "warehouse_id": "All",
                                   "fdate":tdate,
                                   "tdate": tdate
                                  })
            headers = {
                'Content-Type': 'text/plain'
            }
            response = requests.request("GET", url, headers=headers, data=payload)
            if response.status_code == 200:
                data = response.json()
                intercondepowiselist = data['internalconsumptionlist']
                return render(request, 'intconsumption/intconsumption_servicereport.html',
                              {"menuname": menuname, 'wh_masterlist': wh_masterlist,
                               'intercondepowiselist':intercondepowiselist, "fdate":tdate,
                                   "tdate": tdate})
            elif response.status_code == 400:
                data = response.json()
                if data['message'] == 'Sorry! some details are missing':
                    messages.error(request, data['message'])
                    return render(request, 'intconsumption/intconsumption_servicereport.html',
                                  {"menuname": menuname, 'wh_masterlist': wh_masterlist, "fdate":tdate,
                                   "tdate": tdate
                                  })
                else:
                    messages.error(request, data['message'])
                    return redirect('/login')
            else:
                return render(request, 'intconsumption/intconsumption_servicereport.html',
                              {"menuname": menuname, 'wh_masterlist': wh_masterlist,
                              })
    except:
        if response.status_code == 400:
            messages.error(request, data['message'])
            return redirect('/login')
    return render(request,'intconsumption/intconsumption_servicereport.html',{"menuname":menuname})

def get_stocklist(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    menuname = request.session['mylist']
    accesskey = request.session['accesskey']

    url = "http://13.235.112.1/ziva/mobile-api/internal-consumption-stockpoints.php"

    payload = json.dumps({"accesskey": accesskey,
                          "depoid": request.POST.get('depotid')})
    headers = {
        'Content-Type': 'text/plain'
    }
    response = requests.request("GET", url, headers=headers, data=payload)
    if response.status_code == 200:
        data = response.json()
        return JsonResponse({'data': data})
    elif response.status_code == 400:
        data = response.json()
        if data['message'] == 'Sorry! some details are missing':
            messages.error(request, data['message'])
            return JsonResponse({'data': data})
        else:
            messages.error(request, data['message'])
            return redirect('/login')
    else:
        try:
            data = response.json()
            messages.error(request, data['message'])
        except:
            messages.error(request, response.text)
        return JsonResponse({'data': data})


def forgot_pwd(request):

    try:

        url = "http://13.235.112.1/ziva/mobile-api/forgotpassword-new.php"

        payload = json.dumps({
                              "empid":request.POST.get('employee'),
                               "mobileno":request.POST.get('mobileno'),
                               "newpassword": request.POST.get('pwd')
                              })
        headers = {
            'Content-Type': 'text/plain'
        }
        response = requests.request("GET", url, headers=headers, data=payload)
        if response.status_code == 200:
            data = response.json()
            messages.success(request, data['message'])
            return render(request, 'login1.html')
        elif response.status_code == 400:
            data = response.json()
            messages.error(request, data['message'])
            return render(request, 'login1.html')
        else:
            try:
                data = response.json()
                messages.error(request, data['message'])
            except:
                messages.error(request, response.text)
            return render(request, 'login1.html')
    except:
        if response.status_code == 400:
            data = response.json()
            messages.error(request, data['message'])
            return redirect('/login')
        messages.error(request, response.text)
    return render(request, 'login1.html')

def change_pwd(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')

    try:
        menuname = request.session['mylist']
        accesskey = request.session['accesskey']
        url = "http://13.235.112.1/ziva/mobile-api/changepassword.php"

        payload = json.dumps({
            "accesskey": accesskey,
            "oldpassword": request.POST.get('oldpwd'),
            "newpassword": request.POST.get('newpwd')
        })
        headers = {
            'Content-Type': 'text/plain'
        }
        response = requests.request("GET", url, headers=headers, data=payload)
        if response.status_code == 200:
            data = response.json()
            messages.success(request, data['message'])
            return JsonResponse({'data': data})
        elif response.status_code == 400:
            data = response.json()
            return JsonResponse({'data': data})
        elif response.status_code == 503:
            data = response.json()
            messages.error(request, data['message'])
            return JsonResponse({'data': data})
        elif response.status_code == 500:
            data ={'error':'true0','message':'Internal server error'}
            return JsonResponse({'data': data})
        else:
            data ={'error':'true0','message':'something went wrong'}
            return JsonResponse({'data': data})
    except:
        if response.status_code == 400:
            data = response.json()
            messages.error(request, data['message'])
            return redirect('/login')
        messages.error(request, response.text)
    return render(request, 'login1.html')

def internal_stk_list(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    try:
        accesskey = request.session['accesskey']
        menuname = request.session['mylist']
        role = request.session['displayrole']
        url = "http://13.235.112.1/ziva/mobile-api/depo-list.php"

        payload = json.dumps({"accesskey": accesskey})
        headers = {
            'Content-Type': 'text/plain'
        }
        response = requests.request("GET", url, headers=headers, data=payload)
        data = response.json()
        depolist = data['depolist']

        if request.method == 'POST':
                        fdate = request.POST.get('fdate')
                        tdate = request.POST.get('tdate')
                        url = "http://13.235.112.1/ziva/mobile-api/stock-transfer-list.php"
                        if role == 'Admin':
                            payload = json.dumps({"accesskey": accesskey,
                                                  "fdate":fdate,
                                                  "tdate":tdate,
                                                  "depoid": request.POST.get('depoid11'),
                                                  })

                        headers = {
                            'Content-Type': 'text/plain'
                        }
                        response = requests.request("GET", url, headers=headers, data=payload)
                        if response.status_code == 200:
                            data = response.json()
                            stocktransferlist = data['stocktransferlist']
                            return render(request,'intconsumption/internal_stk_list.html',{'stocktransferlist':stocktransferlist,"depolist":depolist,'menuname':menuname,'fdate':fdate,'tdate':tdate,'depolist': depolist})
                        elif response.status_code == 400:
                            data = response.json()
                            if data['message'] == 'Sorry! some details are missing':
                                messages.error(request, data['message'])
                                return render(request, 'intconsumption/internal_stk_list.html',
                                              { 'menuname': menuname,
                                               'fdate': fdate, 'tdate': tdate, 'depolist': depolist})
                            else:
                                messages.error(request, data['message'])
                                return redirect('/login')
                        elif response.status_code == 503:
                            data = response.json()
                            messages.error(request, data['message'])
                            return render(request, 'intconsumption/internal_stk_list.html',
                                          { 'menuname': menuname, 'fdate': fdate,
                                           'tdate': tdate, 'depolist': depolist})
                        elif response.status_code == 500:
                            messages.error(request, 'Internal server error')
                            return render(request, 'intconsumption/internal_stk_list.html',{'menuname':menuname,'fdate':fdate,'tdate':tdate,'depolist': depolist})
                        else:
                            try:
                                data = response.json()
                                return render(request, 'intconsumption/internal_stk_list.html',{'menuname':menuname,'fdate':fdate,'tdate':tdate,'depolist': depolist})
                            except:
                                return render(request, 'intconsumption/internal_stk_list.html',
                                              {'menuname': menuname, 'fdate': fdate, 'tdate': tdate,
                                               'depolist': depolist})
        else:
                        current_date = datetime.date.today()
                        fdate = current_date - timedelta(days=current_date.weekday() + 7)
                        fdate = fdate.strftime("%Y-%m-%d")
                        tdate = datetime.date.today()
                        tdate = tdate.strftime("%Y-%m-%d")

                        url = "http://13.235.112.1/ziva/mobile-api/stock-transfer-list.php"
                        if role == 'DC CONTROLLER':
                            depo = request.session['depoid']
                            payload = json.dumps(
                            {
                                "accesskey": accesskey,
                                 "fdate":fdate,
                                 "tdate":tdate,
                                 "depoid": depo,
                             })
                        if role == 'Admin':
                                payload = json.dumps(
                                {
                                "accesskey": accesskey,
                                "fdate": fdate,
                                "tdate": tdate,
                                "depoid": "All",
                                })

                        headers = {
                            'Content-Type': 'text/plain'
                        }
                        response = requests.request("GET", url, headers=headers, data=payload)
                        if response.status_code == 200:
                            data = response.json()
                            stocktransferlist = data['stocktransferlist']
                            return render(request, 'intconsumption/internal_stk_list.html',
                                          {'stocktransferlist': stocktransferlist,
                                           'depolist': depolist,'menuname': menuname,'fdate':fdate,'tdate':tdate})
                        elif response.status_code == 400:
                            data = response.json()
                            messages.error(request, data['message'])
                            return redirect('/login')
                        elif response.status_code == 500:
                            messages.error(request, 'Internal server error')
                            return render(request, 'intconsumption/internal_stk_list.html',
                                          {'depolist': depolist, 'menuname': menuname,'fdate':fdate,'tdate':tdate})
                        else:
                            try:
                                data = response.json()
                                return render(request, 'intconsumption/internal_stk_list.html',
                                              {'depolist': depolist,'menuname':menuname,'fdate':fdate,'tdate':tdate})
                            except:
                                return render(request, 'intconsumption/internal_stk_list.html',
                                              {'depolist': depolist, 'menuname': menuname, 'fdate': fdate,
                                               'tdate': tdate})

    except:
        if response.status_code == 400:
            data = response.json()
            messages.error(request,data['message'])
            return redirect('/login')
        return render(request, 'intconsumption/internal_stk_list.html',{'menuname':menuname})


def edit_bus_services(request):
    if 'accesskey' not in request.session:
        messages.error(request, 'Access denied!')
        return redirect('/login')
    accesskey = request.session['accesskey']
    if request.method == 'POST':
        url = "http://13.235.112.1/ziva/mobile-api/update-sleeperacbusescount.php"

        payload = json.dumps({"accesskey": accesskey,
                              "depoid": request.POST.get('depot'),
                              "noof_services_ac": request.POST.get('ac'),
                              "noof_services_sl": request.POST.get('sl'),
                              })
        headers = {
            'Content-Type': 'text/plain',
        }
        response = requests.request("GET", url, headers=headers, data=payload)
        if response.status_code == 200:
            data = response.json()
            messages.success(request, data['message'])
            return redirect('/intconsumption_servicereport')
        elif response.status_code == 400:
            data = response.json()
            text = data['message']
            if  'some details are missing' in text:
                messages.error(request, data['message'])
                return redirect('/intconsumption_servicereport')
            else:
                messages.error(request, data['message'])
                return redirect('/login')
        else:
            try:
                r = response.json()
                messages.error(request, r['message'])
            except:
                messages.error(request, response.text)
            return redirect('/intconsumption_servicereport')

    else:
        return redirect('/intconsumption_servicereport')