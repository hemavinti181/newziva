import base64
import json

import time

from django.shortcuts import render, HttpResponse, redirect
from .models import StoreList, Store, Region, State, Category, Warehouse, UOM, ItemList, WarehouseList, VendorList, \
    Role, Designation, Level, City, GST, Grn_item_list, Grn, InventoryList, user, SaleItemList, DeliveryChallan, \
    Indent_Item_List, CarBrand
import requests
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse


class BytesEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, bytes):
            return obj.decode('utf-8')
        return json.JSONEncoder.default(self, obj)


# Create your views here.
def index(request):
    return render(request, 'base.html')


def store_master(request):
    url = "http://13.235.112.1/ziva/mobile-api/store-master-list.php"

    payload = "{\r\n    \"accesskey\":\"MDY5MjAyMDIyLTEyLTE3IDA2OjE1OjU4\"\r\n  \r\n}"
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    data = response.json()
    print(data)
    store_masterlist = data['storemasterlist']
    return render(request, 'masters/store_master_list.html', {"list": store_masterlist})


def add_store(request):
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
    print(res_region)
    region = res_region['regionlist']

    url = "http://13.235.112.1/ziva/mobile-api/dropdwn-table-list.php"

    payload = "{\r\n    \"accesskey\":\"LTIwMjIxMjIwMDc2ODg1\",\r\n    \"name\":\"STATE\"\r\n}"
    headers = {
        'Content-Type': 'text/plain'
    }
    response = requests.request("GET", url, headers=headers, data=payload)
    res_state = response.json()
    state_list = res_state['itemmasterlist']

    if request.method == "POST":
        attempt_num = 0
        url = "http://13.235.112.1/ziva/mobile-api/add-storemaster.php"
        payload = {
            'accesskey': 'MDY5MjAyMDIyLTEyLTE3IDA2OjE1OjU4',
            "storename": request.POST.get("storename"),
            'storeattachfilename': request.FILES.get("storephoto").name,
            'storephoto': base64.b64encode(request.FILES.get("storephoto").file.read()),
            'legalname': request.POST.get("legalname"),
            'region': request.POST.get("region"),
            'gstnumber': request.POST.get("gstnumber"),
            'gstattachfilename': request.FILES.get("gstattach").name,
            'pancard': request.POST.get("pancard"),
            'panattachfilename': request.FILES.get("panattach").name,
            'foodlicence': request.POST.get("foodlicence"),
            'flattachfilename': request.FILES.get("flattach").name,
            'tradelicenceno': request.POST.get("tradelicenceno"),
            'tlattachfilename': request.FILES.get("tlattach").name,
            'storelocation': request.POST.get("storelocation"),
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
        data = r.json()
        print(r)
        if r.status_code == 200:
            messages.success(request, data['message'])
            return redirect('store_master')
        else:
            messages.error(request, data['message'])
    else:
        return render(request, 'masters/store_master_add.html', {'state': state_list, 'data1': region})


def store_edit(request, id):
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
    print(res_region)
    region = res_region['regionlist']

    url = "http://13.235.112.1/ziva/mobile-api/dropdwn-table-list.php"

    payload = "{\r\n    \"accesskey\":\"LTIwMjIxMjIwMDc2ODg1\",\r\n    \"name\":\"STATE\"\r\n}"
    headers = {
        'Content-Type': 'text/plain'
    }
    response = requests.request("GET", url, headers=headers, data=payload)
    res_state = response.json()
    state_list = res_state['itemmasterlist']

    if request.method == "POST":
        url = "http://13.235.112.1/ziva/mobile-api/edit-storemaster.php"
        payload = {
            'accesskey': 'MDY5MjAyMDIyLTEyLTE3IDA2OjE1OjU4',
            "storename": request.POST.get("storename"),
            'storeattachfilename': request.FILES.get("storephoto").name,
            'storephoto': base64.b64encode(request.FILES.get("storephoto").file.read()),
            'legalname': request.POST.get("legalname"),
            'region': request.POST.get("region"),
            'gstnumber': request.POST.get("gstnumber"),
            'gstattachfilename': request.FILES.get("gstattach").name,
            'pancard': request.POST.get("pancard"),
            'panattachfilename': request.FILES.get("panattach").name,
            'foodlicence': request.POST.get("foodlicence"),
            'flattachfilename': request.FILES.get("flattach").name,
            'tradelicenceno': request.POST.get("tradelicenceno"),
            'tlattachfilename': request.FILES.get("tlattach").name,
            'storelocation': request.POST.get("storelocation"),
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
        data = r.json()
        print(data)
        print(r)
        if r.status_code == 200:
            messages.success(request, data['message'])
            return redirect('/store_master')
        else:
            messages.error(request, data['message'])
            return redirect('/store_master')

    else:
        url = "http://13.235.112.1/ziva/mobile-api/store-master-search.php"

        payload = json.dumps({
            "accesskey": "LTIwMjIxMjIwMDc2ODg1",
            "storename": id
        })

        headers = {
            'Content-Type': 'text/plain'
        }

        response = requests.request("GET", url, headers=headers, data=payload)
        data = response.json()
        if response.status_code == 200:
            messages.success(request, data['message'])
            data = data['storemasterlist']
            return render(request, 'masters/store_edit.html', {'data': data[0], 'region': region, 'state': state_list})
        else:
            messages.error(request, data['message'])
            return redirect('/store_master')


def store_status_active(request, id):
    url = "http://13.235.112.1/ziva/mobile-api/status-change.php"

    payload = json.dumps({
        "accesskey": "LTIwMjIxMjE5MjIyMzcy",
        "sno": id,
        "type": "Storemaster",
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
        return redirect('store_master')
    else:
        messages.error(request, data['message'])
        return redirect('store_master')

    return render(request, 'masters/store_master_list.html')


def store_status_inactive(request, id):
    url = "http://13.235.112.1/ziva/mobile-api/status-change.php"

    payload = json.dumps({
        "accesskey": "LTIwMjIxMjE5MjIyMzcy",
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
    url = "http://13.235.112.1/ziva/mobile-api/dropdwn-table-list.php"
    payload = "{\r\n    \"accesskey\":\"MDY5MjAyMDIyLTEyLTE3IDA2OjE1OjU4\",\r\n    \"name\":\"UOM\"\r\n}"
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    response = response.json()
    uom = response['itemmasterlist']

    for i in uom:
        uom_list = UOM(
            code=i['ddcode'],
            name=i['displayname'])
        uom_list.save()
        uom_data = UOM.objects.all().order_by('-id')
    payload = "{\r\n    \"accesskey\":\"MDY5MjAyMDIyLTEyLTE3IDA2OjE1OjU4\",\r\n    \"name\":\"CATEGORY\"\r\n}"
    headers = {
        'Content-Type': 'text/plain'
    }

    response1 = requests.request("GET", url, headers=headers, data=payload)
    response1 = response1.json()
    category = response1['itemmasterlist']

    for i in category:
        cat_list = Category(
            code=i['ddcode'],
            name=i['displayname'])
        cat_list.save()
        cat_data = Category.objects.all().order_by('-id')

    if request.method == "POST":
        attempt_num = 0
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

        return render(request, 'Item_master/item_add.html', {'uom_data': uom_data, 'cat_data': cat_data})


def item_list(request):
    url = "http://13.235.112.1/ziva/mobile-api/itemmaster-list.php"

    payload = "{\r\n    \"accesskey\":\"MDY5MjAyMDIyLTEyLTE3IDA2OjE1OjU4\"\r\n}"
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    data = response.json()
    print(data)
    item_masterlist = data['itemmasterlist']

    return render(request, 'Item_master/item_list.html', {'all_data': item_masterlist})


def item_status_active(request, id):
    url = "http://13.235.112.1/ziva/mobile-api/status-change.php"

    payload = json.dumps({
        "accesskey": "LTIwMjIxMjIwMDc2ODg1",
        "sno": id,
        "type": "Itemmaster",
        "status": "Inactive"
    })
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    print(response)
    data = response.json()
    if response.status_code == 200:
        messages.success(request, data['message'])
        return redirect('item_master')
    else:
        messages.error(request, data['message'])
        return redirect('item_master')

    return render(request, 'item_master/item_list.html')


def item_status_inactive(request, id):
    url = "http://13.235.112.1/ziva/mobile-api/status-change.php"

    payload = json.dumps({
        "accesskey": "LTIwMjIxMjIwMDc2ODg1",
        "sno": id,
        "type": "Itemmaster",
        "status": "Active"
    })
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    print(response)
    data = response.json()
    if response.status_code == 200:
        messages.success(request, data['message'])
        return redirect('item_master')
    else:
        messages.error(request, data['message'])
        return redirect('item_master')

    return render(request, 'item_master/item_list.html')


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
    url = "http://13.235.112.1/ziva/mobile-api/dropdwn-table-list.php"

    payload = "{\r\n    \"accesskey\":\"LTIwMjIxMjIwMDc2ODg1\",\r\n    \"name\":\"DESIGNATION\"\r\n}"
    headers = {
        'Content-Type': 'text/plain'
    }

    response = requests.request("GET", url, headers=headers, data=payload)

    data = response.json()
    print(data)
    des_list = data['itemmasterlist']

    return render(request, 'category_master/des_list.html', {"all_data": des_list})


def region_add(request):
    url = "http://13.235.112.1/ziva/mobile-api/warehousemaster-list.php"

    payload = "{\r\n    \"accesskey\":\"MDY5MjAyMDIyLTEyLTE3IDA2OjE1OjU4\"\r\n   \r\n}"
    headers = {
        'Content-Type': 'text/plain'
    }
    response = requests.request("GET", url, headers=headers, data=payload)
    response = response.json()
    warehouse = response['warehouselist']

    for i in warehouse:
        list = Warehouse(
            code=i['warehouseid'],
            name=i['warehousename'])
        list.save()
        data = Warehouse.objects.all().order_by('-id')
    if request.method == "POST":
        attempt_num = 0
        url = "http://13.235.112.1/ziva/mobile-api/add-regionmaster.php"

        payload = {
            "accesskey": "MDY5MjAyMDIyLTEyLTE3IDA2OjE1OjU4",
            "regionname": request.POST.get("regionname"),
            "gstnumber": request.POST.get("gstnumber"),
            "address": request.POST.get("address"),
            "region_manager": request.POST.get("regionmanager"),
            "location": request.POST.get("location"),
            "region_contact_no": request.POST.get('mobileno'),
            "gstattach": base64.b64encode(request.FILES.get("gstattach").file.read()),
            "gstattachfilename": request.FILES.get("gstattach").name,
            "licence": base64.b64encode(request.FILES.get("licattach").file.read()),
            "licencefilename": request.FILES.get("licattach").name,
            "regionattach": base64.b64encode(request.FILES.get("regionfile").file.read()),
            "regionattachfilename": request.FILES.get("regionfile").name,
            "warehouseid": request.POST.get('wa_id'),
            "warehouse": request.POST.get('warehouse'),
        }
        payload = json.dumps(payload, cls=BytesEncoder)
        # loaded_r = json.loads(payload)
        # data=payload.json()
        headers = {
            'Content-Type': 'application/json'
        }
        r = requests.post(url, payload, headers=headers)
        print(r)
        r1 = r.json()
        if r.status_code == 200:
            messages.success(request, r1['message'])
            return redirect('region_list')
        else:
            messages.error(request, r1['message'])
    else:

        return render(request, 'region/region_add.html', {'data': data})


def region_list(request):
    url = "http://13.235.112.1/ziva/mobile-api/region-list.php"

    payload = "{\r\n    \"accesskey\":\"MDgxNzcyMDIyLTExLTA5IDE1OjI0OjQ2\"\r\n}\r\n"
    headers = {
        'Content-Type': 'text/plain'
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    data = response.json()
    print(data)
    region_list = data['regionlist']
    return render(request, 'region/region_list.html', {'all_data': region_list})


def region_status_active(request, id):
    url = "http://13.235.112.1/ziva/mobile-api/status-change.php"

    payload = json.dumps({
        "accesskey": "LTIwMjIxMjE5MjIyMzcy",
        "sno": id,
        "type": "Regionmaster",
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
        return redirect('region_list')
    else:
        messages.error(request, data['message'])
        return redirect('region_list')


def region_status_inactive(request, id):
    url = "http://13.235.112.1/ziva/mobile-api/status-change.php"

    payload = json.dumps({
        "accesskey": "LTIwMjIxMjE5MjIyMzcy",
        "sno": id,
        "type": "Regionmaster",
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
        return redirect('region_list')
    else:
        messages.error(request, data['message'])
        return redirect('region_list')


def warehouse_list(request):
    url = "http://13.235.112.1/ziva/mobile-api/warehousemaster-list.php"

    payload = "{\r\n    \"accesskey\":\"MDY5MjAyMDIyLTEyLTE3IDA2OjE1OjU4\"\r\n   \r\n}"
    headers = {
        'Content-Type': 'text/plain'
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    data = response.json()
    print(data)
    wh_masterlist = data['warehouselist']

    return render(request, 'warehouse/warehouse_list.html', {'all_data': wh_masterlist})


def warehouse_add(request):
    '''ip = requests.get('https://api.ipify.org?format=json')
    ip_data = json.loads(ip.text)
    response1 = requests.get('http://ip-api.com/json/' + ip_data["ip"])
    res_data = response1.text
    users = json.loads(res_data)'''

    attempt_num = 0
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
    print(res_region)
    region = res_region['regionlist']

    for i in region:
        region_list = Region(
            code=i['regionid'],
            name=i['regionname'])
        region_list.save()
        all_data = Region.objects.all().order_by('-id')
    if request.method == "POST":

        url = "http://13.235.112.1/ziva/mobile-api/add-warehousemaster.php"
        payload = {
            "accesskey": "MDY5MjAyMDIyLTEyLTE3IDA2OjE1OjU4",
            "regionid": request.POST.get('region'),
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

    return render(request, 'warehouse/warehouse_add.html', {'data': all_data})


def warehouse_status_active(request, id):
    url = "http://13.235.112.1/ziva/mobile-api/status-change.php"

    payload = json.dumps({
        "accesskey": "LTIwMjIxMjE5MjIyMzcy",
        "sno": id,
        "type": "Warehousemaster",
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
        return redirect('warehouse_list')
    else:
        messages.error(request, data['message'])
        return redirect('warehouse_list')


def warehouse_status_inactive(request, id):
    url = "http://13.235.112.1/ziva/mobile-api/status-change.php"

    payload = json.dumps({
        "accesskey": "LTIwMjIxMjE5MjIyMzcy",
        "sno": id,
        "type": "Warehousemaster",
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
        return redirect('warehouse_list')
    else:
        messages.error(request, data['message'])
        return redirect('warehouse_list')


def vendor_add(request):
    url = "http://13.235.112.1/ziva/mobile-api/statelist.php"

    payload = json.dumps({
        "accesskey": "MDgxNzcyMDIyLTExLTA5IDE1OjI0OjQ2",
        "category": "Indian"
    })
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    res_state = response.json()
    state_list = res_state['statelist']
    # data = state_list['state']
    for i in state_list:
        state = Store(state=i['state'])
    state.save()
    data = Store.objects.all().order_by('-id')
    if request.method == "POST":
        url = "http://13.235.112.1/ziva/mobile-api/add-vendormaster.php"

        payload = {
            "accesskey": "LTIwMjIxMjIwMDc2ODg1",
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
            "panattach": request.POST.get('panattach'),
            "gstattach": request.POST.get('gstattach'),

        }
        payload = json.dumps(payload, cls=BytesEncoder)
        headers = {
            'Content-Type': 'application/json'
        }
        r = requests.post(url, payload, headers=headers)
        data = r.json()
        print(r)
        if r.status_code == 200:
            messages.success(request, data['message'])
            return redirect('vendor_list')
        else:
            messages.error(request, data['message'])

    return render(request, 'vendor/vendor_add.html', {'data': data})


def vendor_list(request):
    url = "http://13.235.112.1/ziva/mobile-api/vendormasterlist.php"

    payload = "{\r\n    \"accesskey\":\"LTIwMjIxMjE5MjIyMzcy\"\r\n \r\n}"
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("GET", url, headers=headers, data=payload)

    data = response.json()
    print(data)
    vendor_masterlist = data['vendormasterlist']

    return render(request, 'vendor/vendor_list.html', {'all_data': vendor_masterlist})


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


def user_add(request):
    url = "http://13.235.112.1/ziva/mobile-api/dropdwn-table-list.php"

    payload = json.dumps({
        "accesskey": "LTIwMjIxMjIwMDc2ODg1",
        "name": "DESIGNATION"
    })
    headers = {
        'Content-Type': 'application/json'
    }

    response1 = requests.request("GET", url, headers=headers, data=payload)
    data = response1.json()
    print(data)
    des_list = data['itemmasterlist']

    for i in des_list:
        des_list = Designation(id=i['sno'], name=i['displayname'])
        des_list.save()
        all_data = Designation.objects.all().order_by('-id')
    url = "http://13.235.112.1/ziva/mobile-api/region-list.php"

    payload = "{\r\n    \"accesskey\":\"MDgxNzcyMDIyLTExLTA5IDE1OjI0OjQ2\"\r\n}\r\n"
    headers = {
        'Content-Type': 'text/plain'
    }

    response2 = requests.request("GET", url, headers=headers, data=payload)
    data1 = response2.json()
    print(data1)
    region_list = data1['regionlist']

    for i in region_list:
        region_list = Region(name=i['regionname'],
                             region_manager=i['region_manager'],
                             contact_no=i['region_contact_no'],
                             address=i['address'],
                             code=i['regionid'],
                             gst_image=i['gstattach'],
                             lic_image=i['licenceattach'],
                             image=i['regionphoto'],
                             gst=i['gst_no'],
                             licence=i['licenseno'], )
        region_list.save()
        all_data1 = Region.objects.all().order_by('-id')
    url = "http://13.235.112.1/ziva/mobile-api/dropdwn-table-list.php"

    payload = "{\r\n    \"accesskey\":\"LTIwMjIxMjIwMDc2ODg1\",\r\n    \"name\":\"ROLE\"\r\n}"
    headers = {
        'Content-Type': 'text/plain'
    }

    response3 = requests.request("GET", url, headers=headers, data=payload)
    data2 = response3.json()
    print(data)
    role_list = data2['itemmasterlist']

    for i in role_list:
        role_list = Role(id=i['sno'], name=i['displayname'])
        role_list.save()
        all_data2 = Role.objects.all().order_by('-id')

    url = "http://13.235.112.1/ziva/mobile-api/dropdwn-table-list.php"

    payload = "{\r\n    \"accesskey\":\"LTIwMjIxMjIwMDc2ODg1\",\r\n    \"name\":\"LEVEL\"\r\n}"
    headers = {
        'Content-Type': 'text/plain'
    }
    response4 = requests.request("GET", url, headers=headers, data=payload)
    data3 = response4.json()
    print(data3)
    level_list = data3['itemmasterlist']

    for i in level_list:
        level_list = Level(id=i['sno'], name=i['displayname'])
        level_list.save()
        all_data3 = Level.objects.all().order_by('-id')

    if request.method == "POST":
        url = "http://13.235.112.1/ziva/mobile-api/create-user.php"

        payload = {
            "accesskey": "MDExNjczMjAyMi0xMi0xNyAwNjoxNzo1Nw==",
            "username": request.POST.get('username'),
            "mobile": request.POST.get('mobile'),
            "userid": request.POST.get('uid'),
            "emailid": request.POST.get('email'),
            "region": request.POST.get('region'),
            "level": request.POST.get('level'),
            "role": request.POST.get('role'),
            "userattachfilename": request.FILES.get("image").name,
            "designation": request.POST.get('designation'),
            "userimage": base64.b64encode(request.FILES.get("image").file.read()),
        }
        headers = {
            'Content-Type': 'application/json'
        }
        payload = json.dumps(payload, cls=BytesEncoder)
        response = requests.request("GET", url, headers=headers, data=payload)
        print(response)
        print(payload)
        r = response.json()
        if response.status_code == 200:
            messages.success(request, r['message'])
            return redirect('user_list')
        else:

            messages.error(request, r['message'])
            return redirect('user_add')

    return render(request, 'user/user_add.html',
                  {'all_data': all_data, 'all_data1': all_data1, 'all_data2': all_data2, 'all_data3': all_data3})


def user_list(request):
    url = "http://13.235.112.1/ziva/mobile-api/user-list.php"

    payload = json.dumps({
        "accesskey": "MDExNjczMjAyMi0xMi0xNyAwNjoxNzo1Nw=="
    })
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("GET", url, headers=headers, data=payload)

    data = response.json()
    print(data)
    user_list = data['userlist']

    return render(request, 'user/user_list.html', {"list": user_list})


def user_status_active(request, id):
    url = "http://13.235.112.1/ziva/mobile-api/status-change.php"

    payload = json.dumps({
        "accesskey": "LTIwMjIxMjE5MjIyMzcy",
        "sno": id,
        "type": "Logins",
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
        return redirect('user_list')
    else:
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


def item_edit(request, id):
    url = "http://13.235.112.1/ziva/mobile-api/dropdwn-table-list.php"

    payload = "{\r\n    \"accesskey\":\"LTIwMjIxMjIwMDc2ODg1\",\r\n    \"name\":\"CATEGORY\"\r\n}"
    headers = {
        'Content-Type': 'text/plain'
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    data = response.json()
    print(data)
    category_list = data['itemmasterlist']

    url = "http://13.235.112.1/ziva/mobile-api/dropdwn-table-list.php"

    payload = "{\r\n    \"accesskey\":\"LTIwMjIxMjIwMDc2ODg1\",\r\n    \"name\":\"UOM\"\r\n}"
    headers = {
        'Content-Type': 'text/plain'
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    data = response.json()
    print(data)
    uom_list = data['itemmasterlist']

    if request.method == "POST":
        url = "http://13.235.112.1/ziva/mobile-api/edit-itemmaster.php"

        payload = json.dumps({
            "accesskey": "MDY5MjAyMDIyLTEyLTE3IDA2OjE1OjU4",
            "itemname": request.POST.get('nameitem'),
            "hsncode": request.POST.get('hsn1'),
            "lpp": request.POST.get('latestpurchase'),
            "gst": request.POST.get('gst'),
            "category": request.POST.get('category'),
            "mrp": request.POST.get('mrp'),
            "manufacturername": request.POST.get('manufacture'),
            "uom": request.POST.get('uom'),
            "sno": request.POST.get('sno')
        })
        headers = {
            'Content-Type': 'application/json'
        }

        response = requests.request("GET", url, headers=headers, data=payload)

        data = response.json()
        print(data)
        if response.status_code == 200:
            messages.success(request, data['message'])
            return redirect('/item_list')
        else:
            messages.error(request, data['message'])
            return redirect('/item_edit')

    else:

        url = "http://13.235.112.1/ziva/mobile-api/itemmaster-search.php"

        payload = json.dumps({
            "accesskey": "MDY5MjAyMDIyLTEyLTE3IDA2OjE1OjU4",
            "itemcode": id

        })

        headers = {
            'Content-Type': 'application/json'
        }

        response = requests.request("POST", url, headers=headers, data=payload)
        data = response.json()
        data = data['itemmasterlist']

        return render(request, 'Item_master/item_edit.html', {'data': data[0], 'uom': uom_list, 'categ': category_list})


def vendor_edit(request):
    pass


def get_warehouse(request,id):
    url = "http://13.235.112.1/ziva/mobile-api/warehousemaster-list.php"

    payload = "{\r\n    \"accesskey\":\"MDY5MjAyMDIyLTEyLTE3IDA2OjE1OjU4\"\r\n   \r\n}"
    headers = {
        'Content-Type': 'text/plain'
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    data = response.json()
    print(data)
    wh_masterlist = data['warehouselist']



    url = "http://13.235.112.1/ziva/mobile-api/search-warehousemaster.php"

    payload = json.dumps({
        "accesskey": "MDY5MjAyMDIyLTEyLTE3IDA2OjE1OjU4",
        "warehouseid": id
    })

    headers = {
        'Content-Type': 'application/json'
    }

    data = requests.request("POST", url, headers=headers, data=payload)
    data2 = data.json()
    data2=data2['warehouselist']
    return render(request,'warehouse/warehouse_list.html',{'data':data2[0],'all_data':wh_masterlist})



def warehouse_edit(request):
    if request.method == 'POST':
        url = "http://13.235.112.1/ziva/mobile-api/edit-warehousemaster.php"

        payload = json.dumps({
            "accesskey": "MDY5MjAyMDIyLTEyLTE3IDA2OjE1OjU4",
            "warehouseid": request.POST.get('txtHdnWhId'),
            "warehousename": request.POST.get('warehousename1'),
            "gstnumber": request.POST.get('gstwh'),
            "licenseno": request.POST.get('licnumwh'),
            "panno": request.POST.get('panwh'),
            "address": request.POST.get('addresswh'),
            "wh_manager":request.POST.get('manager'),
            "location": request.POST.get('txtHdnWhId'),
            "wh_contact_no": request.POST.get('mobilewh')
        })
        headers = {
            'Content-Type': 'application/json'
        }

        response = requests.request("GET", url, headers=headers, data=payload)
        data=response.json()
        print(data)
        if response.status_code == 200:
            messages.success(request, data['message'])
            return redirect('/item_list')
        else:
            messages.error(request, data['message'])
            return redirect('/item_edit')
def des_edit(request):
    pass


def region_edit(request, id):
    if request.method == "POST":
        url = "http://13.235.112.1/ziva/mobile-api/edit-regionmaster.php"

        payload = json.dumps({

            "accesskey": "MDY5MjAyMDIyLTEyLTE3IDA2OjE1OjU4",
            "regionid": request.POST.get('regionid'),
            "regionname": request.POST.get('regionname'),
            "gstnumber": request.POST.get('gstnumber'),
            "address": request.POST.get('address'),
            "region_manager": request.POST.get('regionmanager'),
            "location": request.POST.get('loacation'),
            "region_contact_no": request.POST.get('mobileno')

        })
        headers = {
            'Content-Type': 'application/json'
        }

        response = requests.request("GET", url, headers=headers, data=payload)

        data = response.json()
        print(data)
        if response.status_code == 200:
            messages.success(request, data['message'])
            return redirect('region_list')
        else:
            messages.error(request, data['message'])
            return redirect('region_list')

    else:

        url = "http://13.235.112.1/ziva/mobile-api/region-search.php"

        payload = json.dumps({
            "accesskey": "MDgxNzcyMDIyLTExLTA5IDE1OjI0OjQ2",
            "regionid": id
        })
        headers = {
            'Content-Type': 'application/json'
        }

        response = requests.request("GET", url, headers=headers, data=payload)
        data = response.json()
        data = data['regionlist']

        return render(request, 'region/region_edit.html', {'data': data[0]})


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

def region_search(request):
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