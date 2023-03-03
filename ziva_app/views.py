import base64
import json

import time

import geocoder as geocoder
from django.shortcuts import render, HttpResponse, redirect
from .models import StoreList, Store, Region, State, Category, Warehouse, UOM, ItemList, WarehouseList, VendorList, \
    Role, Designation, Level, City, GST, Grn_item_list, Grn, InventoryList, user, SaleItemList, DeliveryChallan, \
    Indent_Item_List, CarBrand
import requests
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required

class BytesEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, bytes):
            return obj.decode('utf-8')
        return json.JSONEncoder.default(self, obj)


# Create your views here.

@login_required
def index(request):
    return render(request, 'base.html')

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
            accesskey = data['accesskey']
            username = data['username']
            request.session['accesskey'] = accesskey
            request.session['username'] = username
            messages.success(request,data['message'])
            return redirect('store_master')
        else:
            try:
                data = response.json()
                messages.error(request, data['message'])
                return render(request,'login.html')
            except:
                messages.error(request,response.text)
                return render(request, 'login.html')
    return render(request, 'login.html')
def logout(request):
    del request.session['accesskey']
    del request.session['username']
    return redirect('/login')
def store_master(request):
    accesskey  = request.session['accesskey']

    url = "http://13.235.112.1/ziva/mobile-api/bus-list.php"
    payload = json.dumps({
        "accesskey": accesskey
    })
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("GET", url, headers=headers, data=payload)

    bus_list = response.json()
    bus = bus_list['buslist']

    url = "http://13.235.112.1/ziva/mobile-api/dropdwn-table-list.php"

    payload = json.dumps({"accesskey": accesskey,
                          "name": "STATE"})
    headers = {
        'Content-Type': 'text/plain'
    }
    response = requests.request("GET", url, headers=headers, data=payload)
    res_state = response.json()
    state_list = res_state['itemmasterlist']

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
        return render(request, 'masters/store_master_list.html', {"list": store_masterlist,'state':state_list,'bus':bus})
    else:
        return render(request, 'masters/store_master_list.html', {'state_list': state_list,'bus':bus})
def get_store(request):
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
                        "state": i["state"],"bus_station": i["bus_station"],"busstation_id": i["busstation_id"],"depoid": i["depoid"],"depo": i["depo"],"warehouse": i["warehouse"],"warehouseid": i["warehouseid"],"email":i["email"]}
        return JsonResponse({'data': data})

def add_store(request):
    g = geocoder.ip('me', user_agent='http')
    latlng = g.latlng
    lat = latlng[0]
    lng = latlng[1]
    accesskey = request.session['accesskey']

    url = "http://13.235.112.1/ziva/mobile-api/bus-list.php"
    payload = json.dumps({
        "accesskey":accesskey
    })
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("GET", url, headers=headers, data=payload)

    bus_list = response.json()
    bus = bus_list['buslist']

    url = "http://13.235.112.1/ziva/mobile-api/dropdwn-table-list.php"

    payload = json.dumps({"accesskey":accesskey,
                 "name":"STATE"})
    headers = {
        'Content-Type': 'text/plain'
    }
    response = requests.request("GET", url, headers=headers, data=payload)
    res_state = response.json()
    state_list = res_state['itemmasterlist']

    if request.method == "POST":
        id = request.POST.get("busstationid")
        for i in bus:
            if i['busatationid'] == id:
                depoid = i['depoid']
                deponame = i['deponame']
                regionid = i['regionid']
                regionname = i['regionname']
                warehouseid = i['warehouseid']
                warehousename = i['warehousename']

        url = "http://13.235.112.1/ziva/mobile-api/add-storemaster.php"
        payload = {
            'accesskey': 'MDY5MjAyMDIyLTEyLTE3IDA2OjE1OjU4',
            "storename": request.POST.get("storename"),
            'storeattachfilename': request.FILES.get("storephoto").name,
            'storephoto': base64.b64encode(request.FILES.get("storephoto").file.read()),
            'legalname': request.POST.get("legalname"),
            "depo":regionname ,
            "regionid": regionid,
            "depo": deponame,
            "depoid":depoid,
            "warehouse":warehousename,
            "warehouseid":warehouseid,
            "busstationname": request.POST.get("busstationname"),
            "busstationid": request.POST.get("busstationid"),
            'gstnumber': request.POST.get("gstnumber"),
            'gstattachfilename': request.FILES.get("gstattach").name,
            'pancard': request.POST.get("pancard"),
            'panattachfilename': request.FILES.get("panattach").name,
            'foodlicence': request.POST.get("foodlicence"),
            'flattachfilename': request.FILES.get("flattach").name,
            'tradelicenceno': request.POST.get("tradelicenceno"),
            'tlattachfilename': request.FILES.get("tlattach").name,
            'storelocation': str(lat)+","+str(lng),
            'email': request.POST.get("email"),
            'storeaddress': request.POST.get("storeaddress"),
            'pincode': request.POST.get("pincode"),
            'state': request.POST.get('state'),
            'contactperson': request.POST.get("contactperson"),
            'mobileno': request.POST.get("mobileno"),
            'remarks': request.POST.get("remarks"),
            'gstattach': base64.b64encode(request.FILES.get("gstattach").file.read()),
            'panattach': base64.b64encode(request.FILES.get("panattach").file.read()),
            'flattach': base64.b64encode(request.FILES.get("flattach").file.read()),
            'tlattach': base64.b64encode(request.FILES.get("tlattach").file.read()),

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
        return render(request, 'masters/store_master_add.html', {'state': state_list, 'bus': bus})


def store_edit(request):
    accesskey = request.session['accesskey']
    url = "http://13.235.112.1/ziva/mobile-api/bus-list.php"
    payload = json.dumps({
        "accesskey": accesskey
    })
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("GET", url, headers=headers, data=payload)

    bus_list = response.json()
    bus = bus_list['buslist']


    if request.method == "POST":
        id = request.POST.get("busstationid1")
        for i in bus:
            if i['busatationid'] == id:
                depoid = i['depoid']
                deponame = i['deponame']
                regionid = i['regionid']
                regionname = i['regionname']
                warehouseid = i['warehouseid']
                warehousename = i['warehousename']

                url = "http://13.235.112.1/ziva/mobile-api/edit-storemaster.php"
                payload =json.dumps( {
                    "storecode": request.POST.get("stcode"),
                    'accesskey':accesskey,
                    "storename": request.POST.get("storename"),
                    'legalname': request.POST.get("legalname"),
                    'gstnumber': request.POST.get("gstnumber"),
                    'pancard': request.POST.get("pancard"),
                    "depo": regionname,
                    "regionid":regionid,
                    "depo": deponame,
                    "depoid": depoid,
                    "warehouse": warehousename,
                    "warehouseid": warehouseid,
                    "busstationname":request.POST.get("busstationname1"),
                    "busstationid":request.POST.get("busstationid1"),
                    'foodlicence': request.POST.get("foodlicence"),
                    'tradelicenceno': request.POST.get("tradelicenceno"),
                    'storelocation': request.POST.get("storelocation"),
                    'email': request.POST.get("email"),
                    'storeaddress': request.POST.get("storeaddress"),
                    'pincode': request.POST.get("pincode"),
                    'state': request.POST.get('state'),
                    'contactperson': request.POST.get("contactperson"),
                    'mobileno': request.POST.get("mobileno"),
                    'remarks': request.POST.get("remarks"),
                })
                headers = {
                    'Content-Type': 'application/json'
                }
                r = requests.post(url, payload, headers=headers)
                if r.status_code == 200:
                    data = r.json()
                    messages.success(request, data['message'])
                    return redirect('/store_master')
                else:
                    data = r.json()
                    messages.error(request, data['message'])
                    return redirect('/store_master')

def store_status_active(request):
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
    print(response)
    if response.status_code == 200:
        messages.success(request, data['message'])
        return redirect('store_master')
    else:
        messages.error(request, data['message'])
        return redirect('store_master')


def item_add(request):
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

        url = "http://13.235.112.1/ziva/mobile-api/add-item-master.php"
        payload = {

            "accesskey": "MDY5MjAyMDIyLTEyLTE3IDA2OjE1OjU4",
            "itemname": request.POST.get('name'),
            "hsncode": request.POST.get('hsncode'),
            "lpp": request.POST.get('latestpurchase'),
            "gst": request.POST.get("gst"),
            "category": request.POST.get('category'),
            "mrp": request.POST.get('mrp'),
            "manufacturername": request.POST.get('manufacture'),
            "uom": request.POST.get('uom'),
            "image": base64.b64encode(request.FILES.get("imagefile").file.read()),
        }
        payload = json.dumps(payload, cls=BytesEncoder)
        headers = {
            'Content-Type': 'application/json'
        }
        r = requests.post(url, payload, headers=headers)
        print(r)
        data = r.json()
        if r.status_code == 200:
            messages.success(request, data['message'])
            return redirect('item_master')
        else:
            messages.error(request, data['message'])

    else:

        return render(request, 'Item_master/item_add.html', {'uom_data': uom, 'cat_data': category})


def item_list(request):
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

    url = "http://13.235.112.1/ziva/mobile-api/itemmaster-list.php"

    payload = json.dumps({"accesskey":accesskey})
    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.request("GET", url, headers=headers, data=payload)
    if response.status_code == 200:
        data = response.json()
        item_masterlist = data['itemmasterlist']
        return render(request, 'Item_master/item_list.html', {'all_data': item_masterlist,'category':category,'uom':uom})
    else:
        return render(request, 'Item_master/item_list.html')


def item_status_active(request):
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

def item_status_inactive(request):
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
    else:
        try:
            data = response.json()
            messages.error(request, data['message'])
            return redirect('item_master')
        except:
            messages.error(request, data['message'])
        return redirect('item_master')




def des_add(request):
    attempt_num = 0
    if request.method == 'POST':

        url = "http://13.235.112.1/ziva/mobile-api/addmasterdata.php"

        payload = {
            "accesskey": "LTIwMjIxMjIwMDc2ODg1",
            "type": "DESIGNATION",
            "value": request.POST.get('designation'),
        }
        headers = {
            'Content-Type': 'text/plain'
        }
        payload = json.dumps(payload, cls=BytesEncoder)
        response = requests.request("POST", url, data=payload, headers=headers)
        print(response)
        r = response.json()
        if response.status_code == 200:
            messages.success(request, r['message'])
            return redirect('des_list')
        else:
            messages.error(request, r['message'])
    return render(request, 'category_master/df.html')


def role(request):
    attempt_num = 0
    if request.method == 'POST':

        url = "http://13.235.112.1/ziva/mobile-api/addmasterdata.php"

        payload = {
            "accesskey": "LTIwMjIxMjIwMDc2ODg1",
            "type": "ROLE",
            "value": request.POST.get('role'),
        }
        headers = {
            'Content-Type': 'text/plain'
        }
        payload = json.dumps(payload, cls=BytesEncoder)
        response = requests.request("POST", url, data=payload, headers=headers)
        print(response)
        print(payload)
        r = response.json()
        if response.status_code == 200:
            messages.success(request, r['message'])
            return redirect('role_list')
        else:
            messages.error(request, r['message'])

    return render(request, 'category_master/df.html', {"home_page": "active"})


def level(request):
    attempt_num = 0
    if request.method == 'POST':

        url = "http://13.235.112.1/ziva/mobile-api/addmasterdata.php"

        payload = {
            "accesskey": "LTIwMjIxMjIwMDc2ODg1",
            "type": "LEVEL",
            "value": request.POST.get('level'),
        }
        headers = {
            'Content-Type': 'text/plain'
        }
        payload = json.dumps(payload, cls=BytesEncoder)
        response = requests.request("POST", url, data=payload, headers=headers)
        print(response)
        print(payload)
        r = response.json()
        if response.status_code == 200:
            messages.success(request, r['message'])
            return redirect('level_list')
        else:
            messages.error(request, r['message'])
    return render(request, 'category_master/df.html')


def city(request):
    attempt_num = 0
    if request.method == 'POST':

        url = "http://13.235.112.1/ziva/mobile-api/addmasterdata.php"

        payload = {
            "accesskey": "LTIwMjIxMjIwMDc2ODg1",
            "type": "CITY",
            "value": request.POST.get('city'),
        }
        headers = {
            'Content-Type': 'text/plain'
        }
        payload = json.dumps(payload, cls=BytesEncoder)
        response = requests.request("POST", url, data=payload, headers=headers)
        print(response)
        print(payload)
        r = response.json()
        if response.status_code == 200:
            messages.success(request, r['message'])
            return redirect('city_list')
        else:
            messages.error(request, r['message'])

    return render(request, 'category_master/df.html', {"home_page": "active"})


def state(request):
    attempt_num = 0
    if request.method == 'POST':

        url = "http://13.235.112.1/ziva/mobile-api/addmasterdata.php"

        payload = {
            "accesskey": "LTIwMjIxMjIwMDc2ODg1",
            "type": "STATE",
            "value": request.POST.get('state'),
        }
        headers = {
            'Content-Type': 'text/plain'
        }
        payload = json.dumps(payload, cls=BytesEncoder)
        response = requests.request("POST", url, data=payload, headers=headers)
        print(response)
        print(payload)
        r = response.json()
        if response.status_code == 200:
            messages.success(request, r['message'])
            return redirect('state_list')
        else:
            messages.error(request, r['message'])

    return render(request, 'category_master/df.html', {"home_page": "active"})


def uom(request):
    attempt_num = 0
    if request.method == 'POST':

        url = "http://13.235.112.1/ziva/mobile-api/addmasterdata.php"

        payload = {
            "accesskey": "LTIwMjIxMjIwMDc2ODg1",
            "type": "UOM",
            "value": request.POST.get('uom'),
        }
        headers = {
            'Content-Type': 'text/plain'
        }
        payload = json.dumps(payload, cls=BytesEncoder)
        response = requests.request("POST", url, data=payload, headers=headers)
        print(response)
        print(payload)
        r = response.json()
        if response.status_code == 200:
            messages.success(request, r['message'])
            return redirect('uom_list')
        else:
            messages.error(request, r['message'])

    return render(request, 'Category_master/df.html', {"home_page": "active"})


def gst(request):
    attempt_num = 0
    if request.method == 'POST':

        url = "http://13.235.112.1/ziva/mobile-api/addmasterdata.php"

        payload = {
            "accesskey": "LTIwMjIxMjIwMDc2ODg1",
            "type": "GST",
            "value": request.POST.get('gst'),
        }
        headers = {
            'Content-Type': 'text/plain'
        }
        payload = json.dumps(payload, cls=BytesEncoder)
        response = requests.request("POST", url, data=payload, headers=headers)
        print(response)
        print(payload)
        r = response.json()
        if response.status_code == 200:
            messages.success(request, r['message'])
            return redirect('gst_list')
        else:
            messages.error(request, r['message'])
    return render(request, 'Category_master/df.html', {"home_page": "active"})


def category(request):
    attempt_num = 0
    if request.method == 'POST':

        url = "http://13.235.112.1/ziva/mobile-api/addmasterdata.php"

        payload = {
            "accesskey": "LTIwMjIxMjIwMDc2ODg1",
            "type": "CATEGORY",
            "value": request.POST.get('category'),
        }
        headers = {
            'Content-Type': 'text/plain'
        }
        payload = json.dumps(payload, cls=BytesEncoder)
        response = requests.request("POST", url, data=payload, headers=headers)
        print(response)
        print(payload)
        r = response.json()
        if response.status_code == 200:
            messages.success(request, r['message'])
            return redirect('category_list')
        else:
            messages.error(request, r['message'])

    return render(request, 'Category_master/df.html', {"home_page": "active"})


def role_list(request):
    url = "http://13.235.112.1/ziva/mobile-api/dropdwn-table-list.php"

    payload = "{\r\n    \"accesskey\":\"LTIwMjIxMjIwMDc2ODg1\",\r\n    \"name\":\"ROLE\"\r\n}"
    headers = {
        'Content-Type': 'text/plain'
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    data = response.json()
    print(data)
    role_list = data['itemmasterlist']
    return render(request, 'category_master/role_list.html', {"all_data": role_list})


def level_list(request):
    url = "http://13.235.112.1/ziva/mobile-api/dropdwn-table-list.php"

    payload = "{\r\n    \"accesskey\":\"LTIwMjIxMjIwMDc2ODg1\",\r\n    \"name\":\"LEVEL\"\r\n}"
    headers = {
        'Content-Type': 'text/plain'
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    data = response.json()
    print(data)
    level_list = data['itemmasterlist']
    return render(request, 'category_master/level_list.html', {"all_data": level_list})


def city_list(request):
    url = "http://13.235.112.1/ziva/mobile-api/dropdwn-table-list.php"

    payload = "{\r\n    \"accesskey\":\"LTIwMjIxMjIwMDc2ODg1\",\r\n    \"name\":\"CITY\"\r\n}"
    headers = {
        'Content-Type': 'text/plain'
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    data = response.json()
    print(data)
    city_list = data['itemmasterlist']

    return render(request, 'category_master/city_list.html', {"all_data": city_list})


def state_list(request):
    url = "http://13.235.112.1/ziva/mobile-api/dropdwn-table-list.php"

    payload = "{\r\n    \"accesskey\":\"LTIwMjIxMjIwMDc2ODg1\",\r\n    \"name\":\"STATE\"\r\n}"
    headers = {
        'Content-Type': 'text/plain'
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    data = response.json()
    print(data)
    state_list = data['itemmasterlist']

    return render(request, 'category_master/state_list.html', {"all_data": state_list})


def uom_list(request):
    url = "http://13.235.112.1/ziva/mobile-api/dropdwn-table-list.php"

    payload = "{\r\n    \"accesskey\":\"LTIwMjIxMjIwMDc2ODg1\",\r\n    \"name\":\"UOM\"\r\n}"
    headers = {
        'Content-Type': 'text/plain'
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    data = response.json()
    print(data)
    uom_list = data['itemmasterlist']

    return render(request, 'category_master/uom_list.html', {"all_data": uom_list})


def gst_list(request):
    url = "http://13.235.112.1/ziva/mobile-api/dropdwn-table-list.php"

    payload = "{\r\n    \"accesskey\":\"LTIwMjIxMjIwMDc2ODg1\",\r\n    \"name\":\"GST\"\r\n}"
    headers = {
        'Content-Type': 'text/plain'
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    data = response.json()
    print(data)
    gst_list = data['itemmasterlist']

    return render(request, 'category_master/gst_list.html', {"all_data": gst_list})


def category_list(request):
    url = "http://13.235.112.1/ziva/mobile-api/dropdwn-table-list.php"

    payload = "{\r\n    \"accesskey\":\"LTIwMjIxMjIwMDc2ODg1\",\r\n    \"name\":\"CATEGORY\"\r\n}"
    headers = {
        'Content-Type': 'text/plain'
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    data = response.json()
    print(data)
    category_list = data['itemmasterlist']

    return render(request, 'category_master/category_list.html', {"all_data": category_list})


def des_list(request):
    accesskey = request.session['accesskey']
    url = "http://13.235.112.1/ziva/mobile-api/dropdwn-table-list.php"

    payload = json.dumps({"accesskey":accesskey,   "name":"DESIGNATION"})
    headers = {
        'Content-Type': 'text/plain'
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    if response.status_code == 200:
        data = response.json()
        des_list = data['itemmasterlist']
        return render(request, 'category_master/des_list.html', {"all_data": des_list})
    else:
        return render(request, 'category_master/des_list.html')


def depo_add(request):
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
            messages.error(request, "Add region data")
        return render(request, 'depo/depo_add.html')



    if request.method == "POST":
        id=request.POST.get('regionid')
        for i in regionlist:
            if i['regionid'] == id:
                whid=i['warehouseid']
                whname=i['warehousename']
                regionname = i['regionname']

                url = "http://13.235.112.1/ziva/mobile-api/add-depomaster.php"

                payload = {
                    "accesskey": accesskey,
                    "deponame": request.POST.get("deponame"),
                    "gstnumber": request.POST.get("gstnumber"),
                    "address": request.POST.get("address"),
                    "depo_manager": request.POST.get("depomanager"),
                    "location":  str(lat)+","+str(lng),
                    "depo_contact_no": request.POST.get('mobileno'),
                    "gstattach": base64.b64encode(request.FILES.get("gstattach").file.read()),
                    "gstattachfilename": request.FILES.get("gstattach").name,
                    "licence":request.POST.get("license"),
                    "licenceattach":base64.b64encode(request.FILES.get("licattach").file.read()),
                    "licencefilename": request.FILES.get("licattach").name,
                    "depoattach": base64.b64encode(request.FILES.get("depofile").file.read()),
                    "depoattachfilename": request.FILES.get("depofile").name,
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

        return render(request, 'depo/depo_add.html', {'data': regionlist})


def depo_list(request):
    accesskey = request.session['accesskey']
    payload = json.dumps({"accesskey": accesskey})
    headers = {
        'Content-Type': 'application/json'
    }
    url = "http://13.235.112.1/ziva/mobile-api/region-list.php"
    response = requests.request("POST", url, headers=headers, data=payload)
    data = response.json()
    regionlist = data['regionlist']
    url = "http://13.235.112.1/ziva/mobile-api/depo-list.php"

    payload = json.dumps({"accesskey":accesskey})
    headers = {
        'Content-Type': 'text/plain'
    }
    response = requests.request("GET", url, headers=headers, data=payload)
    if response.status_code == 200:
        data = response.json()
        depolist = data['depolist']
        return render(request, 'depo/depo_list.html', {'all_data': depolist,'data':regionlist})
    else:
        return render(request, 'depo/depo_list.html',{'data':regionlist})



def depo_status_active(request):
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
            messages.error(request, data['message'])
        return redirect('depo_list')

def depo_status_inactive(request):
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
            messages.error(request, data['message'])
        return redirect('bus_list')
def bus_status_active(request):
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
            messages.error(request, data['message'])
        return redirect('bus_list')

def bus_status_inactive(request):
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
            messages.error(request, data['message'])
        return redirect('bus_list')
def region_list(request):
    accesskey = request.session['accesskey']

    url = "http://13.235.112.1/ziva/mobile-api/warehousemaster-list.php"

    payload = "{\r\n    \"accesskey\":\"MDY5MjAyMDIyLTEyLTE3IDA2OjE1OjU4\"\r\n   \r\n}"
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
        return render(request, 'region/region-list.html', {'all_data': regionlist,'data':wh_masterlist})
    else:
        return render(request, 'region/region-list.html',{'data':wh_masterlist})

def region_add(request):

    url = "http://13.235.112.1/ziva/mobile-api/warehousemaster-list.php"

    payload = "{\r\n    \"accesskey\":\"MDY5MjAyMDIyLTEyLTE3IDA2OjE1OjU4\"\r\n   \r\n}"
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
        return render(request,'region/region-add.html',{'data':wh_masterlist})


def get_region(request):
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
    accesskey = request.session['accesskey']
    if request.method == 'POST':
        url = "http://13.235.112.1/ziva/mobile-api/edit-regionmaster.php"

        payload = json.dumps({
            "accesskey": accesskey,
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
        else:
            data = response.json()
            messages.error(request, data['message'])
            return redirect('/region_list')
    return redirect('/region_list')


def warehouse_list(request):
    url = "http://13.235.112.1/ziva/mobile-api/warehousemaster-list.php"

    payload = "{\r\n    \"accesskey\":\"MDY5MjAyMDIyLTEyLTE3IDA2OjE1OjU4\"\r\n   \r\n}"
    headers = {
        'Content-Type': 'text/plain'
    }
    response = requests.request("GET", url, headers=headers, data=payload)
    if response.status_code == 200:
        data = response.json()
        wh_masterlist = data['warehouselist']
        return render(request, 'warehouse/warehouse_list.html', {'all_data': wh_masterlist})
    else:
        return render(request, 'warehouse/warehouse_list.html')


def warehouse_add(request):

    url = "http://13.235.112.1/ziva/mobile-api/region-list.php"
    payload = json.dumps({
        "accesskey": "MDgxNzcyMDIyLTExLTA5IDE1OjI0OjQ2",
        "regionid": ""
    })
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("GET", url, headers=headers, data=payload)

    res_region = response.json()
    region = res_region['regionlist']


    if request.method == "POST":

        url = "http://13.235.112.1/ziva/mobile-api/add-warehousemaster.php"
        payload = {
            "accesskey": "MDY5MjAyMDIyLTEyLTE3IDA2OjE1OjU4",
            "regionid": request.POST.get('depo'),
            "warehousename": request.POST.get('warehousename'),
            "gstnumber": request.POST.get('gstnumber'),
            "licenseno": request.POST.get('licenceno'),
            "panno": request.POST.get('pancard'),
            "address": request.POST.get('storeaddress'),
            "wh_manager": request.POST.get('warehousemamager'),
            "location": request.POST.get('location'),
            "wh_contact_no": request.POST.get('mobileno'),
            "gstattachfilename": request.FILES.get("gstattach").name,
            "panattachfilekename": request.FILES.get('panattach').name,
            "licencefilename": request.FILES.get('licattach').name,
            "warehouseattachfilename": request.FILES.get('warehousefile').name,
            "panattach": base64.b64encode(request.FILES.get('panattach').file.read()),
            "warehouseattach": base64.b64encode(request.FILES.get('warehousefile').file.read()),
            "gstattach": base64.b64encode(request.FILES.get('gstattach').file.read()),
            "licence": base64.b64encode(request.FILES.get('licattach').file.read()),
        }
        payload = json.dumps(payload, cls=BytesEncoder)

        headers = {
            'Content-Type': 'application/json'
        }
        r = requests.post(url, payload, headers=headers)
        print(r)
        r1 = r.json()
        if r.status_code == 200:
            messages.success(request, r1['message'])
            return redirect('warehouse_list')
        else:
            messages.error(request, r['message'])

    return render(request, 'warehouse/warehouse_add.html', {'data': region})

def warehouse_status_active(request):
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
    accesskey = request.session['accesskey']
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
            "city": request.POST.get('city'),
            "panattach": base64.b64encode(request.FILES.get('panattach').file.read()),
            "gstattach": base64.b64encode(request.FILES.get('gstattach').file.read()),

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

    return render(request, 'vendor/vendor_add.html', {'data': state_list})


def vendor_list(request):
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
        return render(request, 'vendor/vendor_list.html', {'all_data': vendor_masterlist})
    else:
        try:
            data = response.json()
            return render(request, 'vendor/vendor_list.html')
        except:
            messages.error(request,response.text)
        return render(request, 'vendor/vendor_list.html')

def vendor_status_active(request, id):
    url = "http://13.235.112.1/ziva/mobile-api/status-change.php"

    payload = json.dumps({
        "accesskey": "LTIwMjIxMjE5MjIyMzcy",
        "sno": id,
        "type": "Vendormaster",
        "status": "Inactive"
    })
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    data = response.json()
    print(response)
    if response.status_code == 200:
        messages.success(request, data['message'])
        return redirect('vendor_list')
    else:
        messages.error(request, data['message'])
        return redirect('vendor_list')


def vendor_status_inactive(request, id):
    url = "http://13.235.112.1/ziva/mobile-api/status-change.php"

    payload = json.dumps({
        "accesskey": "LTIwMjIxMjE5MjIyMzcy",
        "sno": id,
        "type": "Vendormaster",
        "status": "Active"
    })
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    data = response.json()
    print(response)
    if response.status_code == 200:
        messages.success(request, data['message'])
        return redirect('vendor_list')
    else:
        messages.error(request, data['message'])
        return redirect('vendor_list')
def get_depregion(request):
    accesskey = request.session['accesskey']
    warehouse = request.POST.get('warehouse')
    url = "http://13.235.112.1/ziva/mobile-api/dependent-region-list.php"

    payload = json.dumps({"accesskey": accesskey, "warehousename": warehouse})
    headers = {
        'Content-Type': 'text/plain'
    }
    response = requests.request("GET", url, headers=headers, data=payload)
    data = response.json()
    return JsonResponse({'data': data})

def get_dependent_depo(request):
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
    data = response.json()
    return JsonResponse({'data': data})

def get_dependent_bus(request):
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
    data = response.json()
    return JsonResponse({'data': data})

def user_add(request):
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


    url = "http://13.235.112.1/ziva/mobile-api/dropdwn-table-list.php"

    payload = json.dumps({"accesskey": accesskey,  "name":"ROLE"})
    headers = {
        'Content-Type': 'text/plain'
    }

    response3 = requests.request("GET", url, headers=headers, data=payload)
    data2 = response3.json()
    role_list = data2['itemmasterlist']



    url = "http://13.235.112.1/ziva/mobile-api/dropdwn-table-list.php"

    payload = json.dumps({"accesskey": accesskey,  "name":"LEVEL"})
    headers = {
        'Content-Type': 'text/plain'
    }
    response4 = requests.request("GET", url, headers=headers, data=payload)
    data3 = response4.json()
    level_list = data3['itemmasterlist']

    if request.method == "POST":


        url = "http://13.235.112.1/ziva/mobile-api/create-user.php"

        payload = {
            "accesskey": accesskey,
            "username": request.POST.get('username'),
            "mobile": request.POST.get('mobile'),
            "userid": request.POST.get('uid'),
            "emailid": request.POST.get('email'),
            "region": request.POST.get('regionname'),
            "regionid": request.POST.get('region'),
            "warehousename": request.POST.get('warehousename'),
            "depo": request.POST.get('depo'),
            "level": request.POST.get('level'),
            "role": request.POST.get('role'),
            "userattachfilename": request.FILES.get("image").name,
            "designation": request.POST.get('designation'),
            "deponame":request.POST.get('deponame'),
             "depoid": request.POST.get('depo'),
             "busstationname":request.POST.get('busstationname'),
             "busstationid": request.POST.get('busstation'),
            "userimage": base64.b64encode(request.FILES.get("image").file.read())
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
        else:
            r = response.json()
            messages.error(request, r['message'])
            return redirect('user_add')

    return render(request, 'user/user_add.html',
                  {'all_data': des_list,'all_data2': role_list, 'all_data3': level_list,'data':wh_masterlist})


def user_list(request):
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
        user_list = data['userlist']
        return render(request, 'user/user_list.html', {"list": user_list})
    else:
        return render(request, 'user/user_list.html')


def user_status_active(request):
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
    data = response.json()
    print(response)
    if response.status_code == 200:
        messages.success(request, data['message'])
        return redirect('user_list')
    else:
        messages.error(request, data['message'])
        return redirect('user_list')


def add_grn(request):
    url = "http://13.235.112.1/ziva/mobile-api/vendormasterlist.php"

    payload = "{\r\n    \"accesskey\":\"LTIwMjIxMjIwMDc2ODg1\"\r\n \r\n}"
    headers = {
        'Content-Type': 'text/plain'
    }

    response = requests.request("GET", url, headers=headers, data=payload)

    data = response.json()
    print(data)
    vendor_masterlist = data['vendormasterlist']

    url = "http://13.235.112.1/ziva/mobile-api/warehousemaster-list.php"

    payload = "{\r\n    \"accesskey\":\"MDY5MjAyMDIyLTEyLTE3IDA2OjE1OjU4\"\r\n   \r\n}"
    headers = {
        'Content-Type': 'text/plain'
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    data1 = response.json()
    print(data1)
    wh_masterlist = data1['warehouselist']

    if request.method == "POST":
        url = "http://13.235.112.1/ziva/mobile-api/create-grn.php"
        payload = {
            "accesskey": "MDExNjczMjAyMi0xMi0xNyAwNjoxNzo1Nw==",
            "vendorname": request.POST.get('vname'),
            "invoiceno": request.POST.get('invno'),
            "invoicedate": request.POST.get('invoicedate'),
            "invoiceamount": request.POST.get('invoiceamount'),
            "vendorid": request.POST.get('vname'),
            "whcode": request.POST.get('whname')
        }
        payload = json.dumps(payload, cls=BytesEncoder)
        headers = {
            'Content-Type': 'application/json'
        }
        print(payload)
        r = requests.post(url, payload, headers=headers)
        print(r)
        data2 = r.json()
        print(data2['message'])
        print(data2['grnnumber'])
        grn = data2['grnnumber']
        request.session['grnnumber'] = grn
        if r.status_code == 200:
            messages.success(request, data2['message'])
            return redirect('add_grnitem')
        else:
            messages.error(request, data2['message'])
            return redirect('add_grn')
    else:
        return render(request, 'grn/add_grn.html', {'all_data': vendor_masterlist, 'all_data1': wh_masterlist})


def add_grnitem(request):
    id = request.session['grnnumber']
    url = "http://13.235.112.1/ziva/mobile-api/itemmaster-list.php"

    payload = "{\r\n    \"accesskey\":\"MDY5MjAyMDIyLTEyLTE3IDA2OjE1OjU4\"\r\n}"
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    data = response.json()
    print(data)
    item_masterlist = data['itemmasterlist']
    if request.method == "POST":

        url = "http://13.235.112.1/ziva/mobile-api/grn-item.php"
        payload = {
            "accesskey": "MDExNjczMjAyMi0xMi0xNyAwNjoxNzo1Nw==",
            "grnnumber": id,
            "itemname": request.POST.get('txtItemName'),
            "itemcode": request.POST.get('itemcode'),
            "hsncode": request.POST.get('hsn'),
            "qty": request.POST.get('quantity'),
            "batchno": request.POST.get('batchno'),
            "expdate": request.POST.get('expdate'),
            "purchaseprice": request.POST.get('latestpurchase'),
            "mrp": request.POST.get('mrp'),
            "freeqty": request.POST.get('freequantity'),
            "gst": request.POST.get('gst'),
            "uom": request.POST.get('uom'),
            "manufacturer": request.POST.get('manufacture'),
            "itemsno": request.POST.get('itemsno')
        }
        payload = json.dumps(payload, cls=BytesEncoder)
        headers = {
            'Content-Type': 'application/json'
        }
        print(payload)
        r = requests.post(url, payload, headers=headers)
        print(r)
        r1 = r.json()
        if r.status_code == 200:

            messages.success(request, r1['message'])
            url = "http://13.235.112.1/ziva/mobile-api/grn-item-list.php"

            payload = json.dumps({
                "accesskey": "LTIwMjIxMjIwMDc2ODg1",
                "grnno": id
            })
            headers = {
                'Content-Type': 'text/plain'
            }

            response = requests.request("GET", url, headers=headers, data=payload)
            data = response.json()
            grn_item_list = data['grnitemlist']
            return render(request, 'grn/add_grnitem.html', {'all_data': grn_item_list})
        else:
            messages.error(request, r1['message'])
            return redirect('add_grnitem')

    else:
        return render(request, 'grn/add_grnitem.html', {'data': item_masterlist})


'''def add_grnitem_list(request):
    id = request.session['grnnumber']

    url = "http://13.235.112.1/ziva/mobile-api/grn-item-list.php"

    payload = json.dumps({
        "accesskey": "LTIwMjIxMjIwMDc2ODg1",
        "grnno": id
    })
    headers = {
        'Content-Type': 'text/plain'
    }

    response = requests.request("GET", url, headers=headers, data=payload)

    data = response.json()
    grn_item_list = data['grnitemlist']
    return render(request, 'grn/add_grnitem_list.html', {'all_data': grn_item_list})'''


def add_grn_inventory(request):
    url = "http://13.235.112.1/ziva/mobile-api/grn-add-inventory.php"

    payload = json.dumps({
        "accesskey": "MDY5MjAyMDIyLTEyLTE3IDA2OjE1OjU4",
        "grn_no": request.POST.get('txtHdnId'),
        "comments": request.POST.get('comment')
    })
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("GET", url, headers=headers, data=payload)

    data = response.json()
    print(data)
    return redirect('grn_list')
def add_pending_grn_inventory(request):
    url = "http://13.235.112.1/ziva/mobile-api/grn-add-inventory.php"

    payload = json.dumps({
        "accesskey": "MDY5MjAyMDIyLTEyLTE3IDA2OjE1OjU4",
        "grn_no": request.POST.get('txtHdnId'),
        "comments": request.POST.get('comment')
    })
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("GET", url, headers=headers, data=payload)

    data = response.json()
    print(data)
    if response.status_code == 200:
        messages.success(request, data['message'])
        return redirect('grn_pending_status')
    else:
        messages.error(request, data['message'])
        return redirect('grn_pending_status')




def grn_list(request):
    url = "http://13.235.112.1/ziva/mobile-api/grn-list.php"

    payload = "{\r\n     \"accesskey\":\"MDY5MjAyMDIyLTEyLTE3IDA2OjE1OjU4\",\r\n     \"status\":\"All\"\r\n}"
    headers = {
        'Content-Type': 'text/plain'
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    data = response.json()
    print(data)
    grn_list = data['grnlist']

    return render(request, 'grn/grn_list_all.html', {'all_data': grn_list})


def grn_verified_status(request):
    url = "http://13.235.112.1/ziva/mobile-api/grn-list.php"

    payload = "{\r\n     \"accesskey\":\"MDY5MjAyMDIyLTEyLTE3IDA2OjE1OjU4\",\r\n     \"status\":\"verified\"\r\n}"
    headers = {
        'Content-Type': 'text/plain'
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    data = response.json()
    print(data)
    grn_list = data['grnlist']

    return render(request, 'grn/grn_list_verified.html', {'all_data': grn_list})


def grn_pending_status(request):
    url = "http://13.235.112.1/ziva/mobile-api/grn-list.php"

    payload = "{\r\n     \"accesskey\":\"MDY5MjAyMDIyLTEyLTE3IDA2OjE1OjU4\",\r\n     \"status\":\"pending\"\r\n}"
    headers = {
        'Content-Type': 'text/plain'
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    data = response.json()
    print(data)
    grn_list = data['grnlist']

    return render(request, 'grn/grn_list_pending.html', {'all_data': grn_list})


def store_view(request):
    store_code = request.GET.get('store_code')
    store_one = []
    if store_code:
        store_one = StoreList.objects.get(id=store_code)
    store = StoreList.objects.filter(deleted=False).order_by('store_name')

    return render(request, "sales/sales_store_view.html",
                  {'store': store, 'store_one': store_one})


def sales(request):
    url = "http://13.235.112.1/ziva/mobile-api/store-master-list.php"

    payload = "{\r\n    \"accesskey\":\"MDY5MjAyMDIyLTEyLTE3IDA2OjE1OjU4\"\r\n  \r\n}"
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    data = response.json()
    print(data)
    store_masterlist = data['storemasterlist']
    if request.method == "POST":
        attempt_num = 0
        url = "http://13.235.112.1/ziva/mobile-api/generate-salebill-number.php"

        payload = {
            "accesskey": "MDExNjczMjAyMi0xMi0xNyAwNjoxNzo1Nw==",
            "storeid": request.POST.get('storecode'),
        }
        headers = {
            'Content-Type': 'text/plain'
        }
        payload = json.dumps(payload, cls=BytesEncoder)
        response = requests.request("POST", url, headers=headers, data=payload)
        print(payload)
        store_id = request.POST.get('storecode')
        print(store_id)
        print(response)
        data1 = response.json()
        print(data1['message'])
        print(data1['taxinvoice'])
        tax_inv = data1['taxinvoice']
        cus_name = data1['customer_name']
        cus_mobile = data1['customer_mobile']
        request.session['storeid'] = store_id
        request.session['taxinvoice'] = tax_inv
        request.session['customer_name'] = cus_name
        request.session['customer_mobile'] = cus_mobile
        if response.status_code == 200:
            messages.success(request, data1['message'])
            return redirect('sale_item_list')
        else:
            messages.error(request, data1['message'])
            return redirect('sale_item_list')

    else:
        return render(request, 'sales/sales1.html', {"list": store_masterlist})

def sale_item_list(request):
    id = request.session['storeid']

    id1 = request.session['taxinvoice']

    id2 = request.session['customer_name']

    id3 = request.session['customer_mobile']

    url = "http://13.235.112.1/ziva/mobile-api/inventory-search.php"

    payload = json.dumps({
        "accesskey": "MDY5MjAyMDIyLTEyLTE3IDA2OjE1OjU4",
        "searchterm": "bott",
        "storeid": id
    })
    headers = {
        'Content-Type': 'text/plain'
    }

    response = requests.request("GET", url, headers=headers, data=payload)

    data = response.json()
    print(data)
    inventory_list = data['list']
    if request.method == "GET":
        return render(request, 'sales/sale_item_add2.html', {'whitemlist': inventory_list})
    elif request.method == "POST":
        if 'add' in request.POST:
            url = "http://13.235.112.1/ziva/mobile-api/add-saleitem.php"
            payload = {
                "accesskey": "MDY5MjAyMDIyLTEyLTE3IDA2OjE1OjU4",
                "cp_sno": request.POST.get('cpsno'),
                "customername": id2,
                "customermobile": id3,
                "quantity": request.POST.get('quantity'),
                "discount": "0",
                "storeid": id,
                "taxinvoice": id1,
            }

            payload = json.dumps(payload, cls=BytesEncoder)
            headers = {
                'Content-Type': 'application/json'
            }
            print(payload)
            r = requests.post(url, payload, headers=headers)
            print(r)

            data = r.json()

            url = "http://13.235.112.1/ziva/mobile-api/store-master-list.php"

            payload = "{\r\n    \"accesskey\":\"MDY5MjAyMDIyLTEyLTE3IDA2OjE1OjU4\"\r\n  \r\n}"
            headers = {
                'Content-Type': 'application/json'
            }

            response = requests.request("GET", url, headers=headers, data=payload)
            data = response.json()
            print(data)
            store_masterlist = data['storemasterlist']
            url = "http://13.235.112.1/ziva/mobile-api/sale-item-list.php"

            payload = json.dumps({
                "accesskey": "MDY5MjAyMDIyLTEyLTE3IDA2OjE1OjU4",
                "sonumber": id1
            })
            headers = {
                'Content-Type': 'text/plain'
            }

            response = requests.request("GET", url, headers=headers, data=payload)
            data = response.json()
            print(response)

            sale_item_list = data['saleitemlist']
            return render(request, 'sales/sale_item_add2.html',
                          {"all_data": sale_item_list, 'data': sale_item_list[0]})
        if 'complete' in request.POST:
            url = "http://13.235.112.1/ziva/mobile-api/dc-pending.php"

            payload = json.dumps({
                "accesskey": "LTIwMjIxMjIwMDc2ODg1",
                "sonumber": request.POST.get('txtHdnId'),
                "paymentmode": request.POST.get('paymenttype'),
                "remarks": ""
            })
            headers = {
                'Content-Type': 'application/json'
            }

            response = requests.request("GET", url, headers=headers, data=payload)

            data = response.json()
            print(payload)
            if response.status_code == 200:
                messages.success(request, data['message'])
                return redirect('sales')
            else:
                messages.error(request, data['message'])
                return redirect('sale_item_list')
        return render(request, 'sales/sale_item_add2.html')

def proformainvoice(request):
     if request.method == "GET":
        return render(request, 'sales/sales_new.html')
     elif request.method == "POST":
        if 'search' in request.POST:
            url = "http://13.235.112.1/ziva/mobile-api/generate-salebill-number.php"

            payload = {
                "accesskey": "MDExNjczMjAyMi0xMi0xNyAwNjoxNzo1Nw==",
                "storeid": request.POST.get('txtStoreId'),
            }
            headers = {
                'Content-Type': 'text/plain'
            }
            payload = json.dumps(payload, cls=BytesEncoder)
            response = requests.request("POST", url, headers=headers, data=payload)
            print(payload)
            data=response.json()
            stid=request.POST.get('txtStoreId')
            tax_inv = data['taxinvoice']
            cus_name = data['customer_name']
            cus_mobile = data['customer_mobile']
            request.session['taxinvoice'] = tax_inv
            request.session['customer_name'] = cus_name
            request.session['customer_mobile'] = cus_mobile
            request.session['storeid'] = stid
            if response.status_code == 200:
                messages.success(request, data['message'])
                return redirect('proformainvoice')
            else:
                messages.error(request, data['message'])
                return redirect('proformainvoice')


        if 'add' in request.POST:
            tax_inv =  request.session['taxinvoice']
            cus_name = request.session['customer_name']
            cus_mobile = request.session['customer_mobile']
            stid = request.session['storeid']

            url = "http://13.235.112.1/ziva/mobile-api/add-saleitem.php"
            payload = {
                "accesskey": "MDY5MjAyMDIyLTEyLTE3IDA2OjE1OjU4",
                "cp_sno": request.POST.get('cpsno'),
                "customername": cus_name,
                "customermobile": cus_mobile,
                "quantity": request.POST.get('quantity'),
                "storeid":stid ,
                "taxinvoice": tax_inv,
            }

            payload = json.dumps(payload, cls=BytesEncoder)
            headers = {
                'Content-Type': 'application/json'
            }
            print(payload)
            r = requests.post(url, payload, headers=headers)
            print(r)

            data = r.json()
            url = "http://13.235.112.1/ziva/mobile-api/sale-item-list.php"

            payload = json.dumps({
                "accesskey": "MDY5MjAyMDIyLTEyLTE3IDA2OjE1OjU4",
                "sonumber": tax_inv
            })
            headers = {
                'Content-Type': 'text/plain'
            }

            response = requests.request("GET", url, headers=headers, data=payload)
            data = response.json()
            print(response)


            if response.status_code == 200:
                messages.success(request, data['message'])
                sale_item_list = data['saleitemlist']
                return render(request, 'sales/sales_new.html',
                              {"all_data": sale_item_list, 'data': sale_item_list[0]})
            else:
                messages.error(request, data['message'])
                return redirect('proformainvoice')
        if 'complete' in request.POST:
            url = "http://13.235.112.1/ziva/mobile-api/dc-pending.php"

            payload = json.dumps({
                "accesskey": "LTIwMjIxMjIwMDc2ODg1",
                "sonumber": request.POST.get('txtHdnId'),
                "paymentmode": request.POST.get('paymenttype'),
                "remarks": ""
            })
            headers = {
                'Content-Type': 'application/json'
            }

            response = requests.request("GET", url, headers=headers, data=payload)

            data = response.json()
            print(payload)
            if response.status_code == 200:
                messages.success(request, data['message'])
                return redirect('proformainvoice')
            else:
                messages.error(request, data['message'])
                return redirect('proformainvoice')
        return render(request, 'sales/sales_new.html')

def grn(request):
    url = "http://13.235.112.1/ziva/mobile-api/vendormasterlist.php"

    payload = "{\r\n    \"accesskey\":\"LTIwMjIxMjIwMDc2ODg1\"\r\n \r\n}"
    headers = {
        'Content-Type': 'text/plain'
    }

    response = requests.request("GET", url, headers=headers, data=payload)

    data = response.json()
    print(data)
    vendor_masterlist = data['vendormasterlist']

    url = "http://13.235.112.1/ziva/mobile-api/warehousemaster-list.php"

    payload = "{\r\n    \"accesskey\":\"MDY5MjAyMDIyLTEyLTE3IDA2OjE1OjU4\"\r\n   \r\n}"
    headers = {
        'Content-Type': 'text/plain'
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    data1 = response.json()
    print(data1)
    wh_masterlist = data1['warehouselist']

    if request.method == "POST":
        url = "http://13.235.112.1/ziva/mobile-api/create-grn.php"
        payload = {
            "accesskey": "MDExNjczMjAyMi0xMi0xNyAwNjoxNzo1Nw==",
            "vendorname": request.POST.get('vname'),
            "invoiceno": request.POST.get('invno'),
            "invoicedate": request.POST.get('invoicedate'),
            "invoiceamount": request.POST.get('invoiceamount'),
            "vendorid": request.POST.get('vname'),
            "whcode": request.POST.get('whname')
        }
        payload = json.dumps(payload, cls=BytesEncoder)
        headers = {
            'Content-Type': 'application/json'
        }
        print(payload)
        r = requests.post(url, payload, headers=headers)
        print(r)
        data2 = r.json()
        print(data2['message'])
        print(data2['grnnumber'])
        grn = data2['grnnumber']
        request.session['grnnumber'] = grn
        if r.status_code == 200:
            messages.success(request, data2['message'])
            return redirect('add_grnitem')
        else:
            messages.error(request, data2['message'])
            return redirect('add_grn')
    else:
        return render(request, 'grn/grn_new.html', {'all_data': vendor_masterlist, 'all_data1': wh_masterlist})

def deliver_challan(request):
    url = "http://13.235.112.1/ziva/mobile-api/delivery-pending-list.php"

    payload = json.dumps({
        "accesskey": "LTIwMjIxMjIwMDc2ODg1"
    })
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    data = response.json()
    print(data)
    deliv_challan = data['deliverypendinglist']

    return render(request, 'deliverychallan/deliverychallan.html', {"all_data": deliv_challan})

def deliver_challan_status(request):
    url = "http://13.235.112.1/ziva/mobile-api/delivery-challan.php"

    payload = json.dumps({

        "accesskey":"MDY5MjAyMDIyLTEyLTE3IDA2OjE1OjU4",
        "sonumber":request.POST.get('txtHdnId'),
        "agentname":request.POST.get('agentname'),
        "vehicledetails":request.POST.get('vehicaldetails'),
        "remarks":request.POST.get('remarks')
    })
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    data = response.json()
    print(data)
    if response.status_code == 200:
        messages.success(request, data['message'])
        return redirect('deliver_challan')
    else:
        messages.error(request, data['message'])
        return redirect('deliver_challan')



def create_indent(request):
    url = "http://13.235.112.1/ziva/mobile-api/itemmaster-list.php"

    payload = "{\r\n    \"accesskey\":\"MDY5MjAyMDIyLTEyLTE3IDA2OjE1OjU4\"\r\n}"
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    data = response.json()
    print(data)
    item_masterlist = data['itemmasterlist']

    if request.method == 'POST':
        url = "http://13.235.112.1/ziva/mobile-api/create-indent-item.php"

        payload = {
            "accesskey": "LTIwMjIxMjE5MjIyMzcy",
            "indentno": "IND221200004",
            "itemname": request.POST.get('itemcode'),
            "itemcode":request.POST.get('itemcode') ,
            "qty": request.POST.get('quantity'),
            "mrp": request.POST.get('mrp'),

        }
        headers = {
            'Content-Type': 'text/plain'
        }
        print(payload)
        response = requests.request("GET", url, headers=headers, data=payload)
        print(response)
        data = response.json()
        print(data)
        if response.status_code == 200:
            messages.success(request, data['message'])
            return redirect('/')
        else:
            messages.error(request, data['message'])
    return render(request, 'create_indent/create_indent.html',{'all_data':item_masterlist})


def indent_list(request):
    url = "http://13.235.112.1/ziva/mobile-api/indent-list.php"

    payload = json.dumps({
        "accesskey": "LTIwMjIxMjE5MjIyMzcy",
        "type": "Region"
    })
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("GET", url, headers=headers, data=payload)

    data = response.json()
    print(data)
    ind_list = data['indentlist']

    return render(request, 'create_indent/indent_item_list.html', {"all_data": ind_list})


def indent_item_list(request):
    url = "http://13.235.112.1/ziva/mobile-api/indent-item-list.php"

    payload = json.dumps({
        "accesskey": "LTIwMjIxMjE5MjIyMzcy",
        "indentno": "IND221200003"
    })
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    data = response.json()
    print(data)
    ind_item_list = data['indentitemlist']
    return render(request, 'create_indent/indent_item_list.html', {"all_data": ind_item_list})


@csrf_exempt
def get_grn_item_data(request):
    itemname = request.POST.get('itemcode')

    url = "http://13.235.112.1/ziva/mobile-api/itemmaster-search.php"

    payload = json.dumps({
        "accesskey": "MDY5MjAyMDIyLTEyLTE3IDA2OjE1OjU4",
        "itemcode": itemname
    })

    headers = {
        'Content-Type': 'application/json'
    }

    data = requests.request("POST", url, headers=headers, data=payload)
    data2 = data.json()
    return JsonResponse({'data': data2})


@csrf_exempt
def get_item_data(request):
    name = request.POST.get('name')

    url = "http://13.235.112.1/ziva/mobile-api/itemmaster-search.php"

    payload = json.dumps({
        "accesskey": "MDY5MjAyMDIyLTEyLTE3IDA2OjE1OjU4",
        "itemcode": name
    })

    headers = {
        'Content-Type': 'application/json'
    }

    data = requests.request("POST", url, headers=headers, data=payload)
    data2 = data.json()
    return JsonResponse({'data': data2})


@csrf_exempt
def get_sale_item_data(request):

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
    print(payload)
    data = requests.request("POST", url, headers=headers, data=payload)
    data2 = data.json()
    return JsonResponse({'data': data2})


def item_edit(request):
    accesskey = request.session['accesskey']


    if request.method == "POST":
        url = "http://13.235.112.1/ziva/mobile-api/edit-itemmaster.php"

        payload = json.dumps({
            "accesskey":accesskey ,
            "itemname": request.POST.get('nameitem'),
            "hsncode": request.POST.get('hsn1'),
            "lpp": request.POST.get('latestpurchase'),
            "gst": request.POST.get('gst'),
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
        else:
            messages.error(request, data['message'])
            return redirect('/item_edit')
    return redirect('/item_list')

def vendor_edit(request):
    pass


def get_warehouse(request):
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
                        "wh_contact_no":i["wh_contact_no"],"location":i["location"]}
    return JsonResponse({'data': data})



def warehouse_edit(request):
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
            "wh_contact_no": request.POST.get('mobilewh')
        })
        headers = {
            'Content-Type': 'application/json'
        }

        response = requests.request("GET", url, headers=headers, data=payload)

        if response.status_code == 200:
            data = response.json()
            messages.success(request, data['message'])
            return redirect('/warehouse_list')
        else:
            data = response.json()
            messages.error(request, data['message'])
            return redirect('/warehouse_list')
def des_edit(request):
    pass
def get_depo(request):
    accesskey = request.session['accesskey']
    url = "http://13.235.112.1/ziva/mobile-api/depo-search.php"

    payload = json.dumps({
        "accesskey": accesskey,
        "depoid": request.POST.get('id')
    })

    headers = {
        'Content-Type': 'application/json'
    }
    data = requests.request("POST", url, headers=headers, data=payload)
    data2 = data.json()
    return JsonResponse({'data': data2})

def depo_edit(request):
    accesskey = request.session['accesskey']
    if request.method == "POST":
        url = "http://13.235.112.1/ziva/mobile-api/edit-depomaster.php"

        payload = json.dumps({

            "accesskey": accesskey,
            "depoid": request.POST.get('depoid'),
            "deponame": request.POST.get('deponame1'),
            "gstnumber": request.POST.get('gstnumber1'),
            "address": request.POST.get('address1'),
            "licenseno": request.POST.get('license1'),
            "depo_manager":request.POST.get('depomanager1'),
            "depo_contact_no":request.POST.get('mobileno1'),
            "warehouseid":request.POST.get('whid'),
            "warehouse":request.POST.get('whname'),
            "regionid": request.POST.get('regionid1'),
            "regionname":request.POST.get('regionname'),
        })
        headers = {
            'Content-Type': 'application/json'
        }

        response = requests.request("GET", url, headers=headers, data=payload)

        data = response.json()

        if response.status_code == 200:
            messages.success(request, data['message'])
            return redirect('depo_list')
        else:
            messages.error(request, data['message'])
            return redirect('depo_list')
    return redirect('region_list')


def level_edit(request):
    pass


def warehouse_indent_ack(request):
    url = "http://13.235.112.1/ziva/mobile-api/warehouse-indent-list.php"

    payload = json.dumps({
        "accesskey": "LTIwMjIxMjE5MjIyMzcy",
        "status": "Acknowledgement"
    })
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    data = response.json()
    data = data['indentlist']
    return render(request, 'create_indent/wh_indent_ack.html', {'data': data})


def warehouse_indent_pending(request):
    url = "http://13.235.112.1/ziva/mobile-api/warehouse-indent-list.php"

    payload = json.dumps({
        "accesskey": "LTIwMjIxMjE5MjIyMzcy",
        "status": "pending"
    })
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    data = response.json()
    data = data['indentlist']
    return render(request, 'create_indent/wh_indent_pending.html', {'data': data})

def wh_ind_status(request):
    url = "http://13.235.112.1/ziva/mobile-api/acknowledgement-update.php"

    payload = json.dumps({
        "accesskey": "LTIwMjIxMjE5MjIyMzcy",
        "sno": request.POST.get('txtHdnId'),
        "remarks":request.POST.get('comment')
    })
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    data=response.json()
    print(data)
    if response.status_code == 200:
        messages.success(request, data['message'])
        return redirect('warehouse_indent_pending')
    else:
        messages.error(request, data['message'])
        return redirect('warehouse_indent_pending')


def sales_list(request):
    url = "http://13.235.112.1/ziva/mobile-api/sales-list.php"

    payload = json.dumps({
        "accesskey": "MDY5MjAyMDIyLTEyLTE3IDA2OjE1OjU4",
        "type": "Pending"
    })
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    data = response.json()
    data = data['saleslist']
    return render(request, 'sales/sales_list.html', {'data': data})


def sales_list_outpass(request):
    url = "http://13.235.112.1/ziva/mobile-api/sales-list.php"

    payload = json.dumps({
        "accesskey": "MDY5MjAyMDIyLTEyLTE3IDA2OjE1OjU4",
        "type": "Outpass"
    })
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    data = response.json()
    data = data['saleslist']
    return render(request, 'sales/sales_outpass_list.html', {'data': data})


def dc_pending(request):


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
        else:
            messages.error(request, data['message'])
            return redirect('sale_item_list')



def stock_transfer(request):
    #brand = CarBrand.objects.all()
    #return render(request, 'stock_transfer/complete.html',{'list':list})
    return render(request,'stock_transfer/stock_transfer_home.html')


def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'
def autocompleteModel(request):

    if (1==1):
        q = request.GET.get('term', '').capitalize()
        search_qs = CarBrand.objects.filter(name__startswith=q)
        results = []
        print(q)
        for r in search_qs:
            results.append(r.name)
        data = json.dumps(results)
    else:
        data = 'fail'
    mimetype = 'application/json'
    return HttpResponse(data, mimetype)
def get_store_data(request):
    serchterm = request.POST.get('searchterm')
    stid = request.POST.get('store_id')

    url = "http://13.235.112.1/ziva/mobile-api/inventory-search.php"

    payload = json.dumps({
        "accesskey": "MDY5MjAyMDIyLTEyLTE3IDA2OjE1OjU4",
        "searchterm": serchterm,
        "storeid":stid

    })
    headers = {
        'Content-Type': 'application/json'

    }

    response = requests.request("GET", url, headers=headers, data=payload)
    data = response.json()

    return JsonResponse({'data': data})

def store_search(request):

    serchterm = request.POST.get('searchterm')
    url = "http://13.235.112.1/ziva/mobile-api/store-master-search.php"

    payload = json.dumps({
            "accesskey":"MDY5MjAyMDIyLTEyLTE3IDA2OjE1OjU4",
            "storename":serchterm
    })
    headers = {
        'Content-Type': 'text/plain'
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    data = response.json()

    return JsonResponse({'data': data})
def get_wh_item(request):
    serchterm = request.POST.get('searchterm')
    whid = request.POST.get('wh_id')



    url = "http://13.235.112.1/ziva/mobile-api/warehouseinventory-search.php"

    payload = json.dumps({
        "accesskey": "LTIwMjIxMjIwMDc2ODg1",
        "searchterm":serchterm,
        "id": whid ,
    })
    headers = {
        'Content-Type': 'application/json'

    }

    response = requests.request("GET", url, headers=headers, data=payload)
    data=response.json()


    return JsonResponse({'data': data})
def wh_search(request):
    url = "http://13.235.112.1/ziva/mobile-api/warehousemaster-list.php"

    payload = "{\r\n    \"accesskey\":\"MDY5MjAyMDIyLTEyLTE3IDA2OjE1OjU4\"\r\n   \r\n}"
    headers = {
        'Content-Type': 'text/plain'
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    data = response.json()
    print(data)
    wh_masterlist = data['warehouselist']

    if request.method == "POST":
        url = "http://13.235.112.1/ziva/mobile-api/generate-transitid.php"

        payload = json.dumps({
            "accesskey": "MDY5MjAyMDIyLTEyLTE3IDA2OjE1OjU4",
            "id": request.POST.get('whcode'),
            "name": request.POST.get('whName'),
        })
        headers = {
            'Content-Type': 'application/json'
        }

        response = requests.request("GET", url, headers=headers, data=payload)
        print(payload)
        data = response.json()
        request.session['taxinvoice'] = data['taxinvoice']
        request.session['id'] = request.POST.get('whcode')

        if response.status_code == 200:
            messages.success(request, data['message'])
            return redirect('wh_item_add')
        else:
            messages.error(request, data['message'])
            return redirect('wh_search')
    else:
        return render(request,'stock_transfer/wh_search_inventory.html',{'data':wh_masterlist})

def wh_item_add(request):
    code =  request.session['id']
    taxinvoice  = request.session['taxinvoice']

    if request.method == 'POST':
        url = "http://13.235.112.1/ziva/mobile-api/add-stockitem-warehouse.php"

        payload = json.dumps({
            "accesskey": "MDY5MjAyMDIyLTEyLTE3IDA2OjE1OjU4",
            "cp_sno": request.POST.get('cpsno'),
            "quantity": request.POST.get('quantity'),
            "freeqty": request.POST.get('freequantity'),
            "id": code,
            "transitid": taxinvoice
        })
        headers = {
            'Content-Type': 'application/json'
        }

        response = requests.request("GET", url, headers=headers, data=payload)
        print(payload)
        data=response.json()
        if response.status_code == 200:
            messages.success(request, data['message'])
            return redirect('wh_item_list')
        else:
            messages.error(request, data['message'])
            return redirect('wh_item_list')

    else:
        return render(request,'stock_transfer/wh_item_add.html')

def wh_item_list(request):

    taxinvoice  = request.session['taxinvoice']
    url = "http://13.235.112.1/ziva/mobile-api/stocktransfer-item-list.php"

    payload = json.dumps({"accesskey":"MDY5MjAyMDIyLTEyLTE3IDA2OjE1OjU4",
    "transitid":taxinvoice
    })
    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.request("GET", url, headers=headers, data=payload)
    data=response.json()
    wh_item_list=data['stocktransferitemlist']
    return render(request,'stock_transfer/wh_item_list.html',{'data':wh_item_list})

def depo_search(request):
    url = "http://13.235.112.1/ziva/mobile-api/region-list.php"

    payload = "{\r\n    \"accesskey\":\"MDgxNzcyMDIyLTExLTA5IDE1OjI0OjQ2\"\r\n}\r\n"
    headers = {
        'Content-Type': 'text/plain'
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    data = response.json()
    print(data)
    region_list = data['regionlist']


    if request.method == "POST":
            url = "http://13.235.112.1/ziva/mobile-api/generate-transitid.php"

            payload = json.dumps({
                "accesskey": "MDY5MjAyMDIyLTEyLTE3IDA2OjE1OjU4",
                "id": request.POST.get('regioncode'),
                "name": request.POST.get('whName'),
            })
            headers = {
                'Content-Type': 'application/json'
            }

            response = requests.request("GET", url, headers=headers, data=payload)
            print(payload)
            data = response.json()
            request.session['taxinvoice'] = data['taxinvoice']
            request.session['id'] = request.POST.get('regioncode')

            if response.status_code == 200:
                messages.success(request, data['message'])
                return redirect('reg_item_add')
            else:
                messages.error(request, data['message'])
                return redirect('reg_item_add')
    return render(request, 'stock_transfer/region_search_inventory.html', {'all_data': region_list})

def get_region_item(request):

    serchterm = request.POST.get('searchterm')
    whid = request.POST.get('wh_id')
    url = "http://13.235.112.1/ziva/mobile-api/warehouseinventory-search.php"

    payload = json.dumps({
        "accesskey": "LTIwMjIxMjIwMDc2ODg1",
        "searchterm":serchterm,
        "id": whid ,
    })
    headers = {
        'Content-Type': 'application/json'

    }

    response = requests.request("GET", url, headers=headers, data=payload)
    data=response.json()


    return JsonResponse({'data': data})


def reg_item_add(request):
    code = request.session['id']
    taxinvoice = request.session['taxinvoice']

    if request.method == 'POST':
        url = "http://13.235.112.1/ziva/mobile-api/add-stockitem-warehouse.php"

        payload = json.dumps({
            "accesskey": "MDY5MjAyMDIyLTEyLTE3IDA2OjE1OjU4",
            "cp_sno": request.POST.get('cpsno'),
            "quantity": request.POST.get('quantity'),
            "freeqty": request.POST.get('freequantity'),
            "id": code,
            "transitid": taxinvoice
        })
        headers = {
            'Content-Type': 'application/json'
        }

        response = requests.request("GET", url, headers=headers, data=payload)
        print(payload)
        data=response.json()
        if response.status_code == 200:
            messages.success(request, data['message'])
            return redirect('reg_item_add')
        else:
            messages.error(request, data['message'])
            return redirect('reg_item_add')

    else:
        return render(request, 'stock_transfer/region_item_add.html')

def bus_list(request):
    accesskey = request.session['accesskey']
    url = "http://13.235.112.1/ziva/mobile-api/depo-list.php"

    payload = json.dumps({"accesskey": accesskey})
    headers = {
        'Content-Type': 'text/plain'
    }

    response = requests.request("GET", url, headers=headers, data=payload)

    data = response.json()
    depolist = data['depolist']

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
        data = response.json()
        bus = data['buslist']
        return render(request,'busstation/bus_list.html',{'bus':bus,'data':depolist})
    else:
        return render(request, 'busstation/bus_list.html',{'data':depolist})


def bus_add(request):
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
                payload = json.dumps(
                {
                    "accesskey": accesskey,
                    "busstationname":request.POST.get('busname'),
                    "depoid": request.POST.get('depoid'),
                    "deponame": request.POST.get('diponame'),
                    "busstation_contact_no": request.POST.get('mobileno'),
                    "busstation_manager": request.POST.get('busmanager'),
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
    return render(request,'busstation/bus_add.html',{'data':depolist})
def get_bus(request):

    accesskey = request.session['accesskey']
    url = "http://13.235.112.1/ziva/mobile-api/bus-search.php"

    payload = json.dumps({
        "accesskey":accesskey ,
        "busid": request.POST.get('id')
    })

    headers = {
        'Content-Type': 'application/json'
    }
    data = requests.request("POST", url, headers=headers, data=payload)
    data2 = data.json()
    return JsonResponse({'data': data2})



def bus_edit(request):
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
        else:
            data = response.json()
            messages.error(request, data['message'])
            return redirect('/bus_list')
    return redirect('/bus_list')
