from django.db import models

# Create your models here.
class CarBrand(models.Model):
    name=models.CharField(max_length=100)
class StoreList(models.Model):

    store_name = models.CharField(max_length=50, blank = True, null = True)
    gst_No = models.CharField(max_length=16)
    pan=models.CharField(max_length=16)
    trade_licence = models.CharField(max_length=10)
    food_licence = models.CharField(max_length=10)
    store_location = models.CharField(max_length=10)
    store_code = models.CharField(max_length=10)
    gst_attach = models.ImageField(null=True, default=None, blank=True)
    pan_attach = models.ImageField(null=True, default=None, blank=True)
    store_attach=models.ImageField(null=True, default=None, blank=True)
    trade_attach=models.ImageField(null=True, default=None, blank=True)
    food_attach=models.ImageField(null=True, default=None, blank=True)
    address=models.CharField(max_length=10)
    contact_person=models.CharField(max_length=10)
    status = models.BooleanField(default=False)
    deleted = models.BooleanField(default=False)


class Region(models.Model):
    code = models.CharField(max_length=50)
    name = models.CharField(max_length=10)
    region_manager = models.CharField(max_length=50)
    contact_no = models.CharField(max_length=50)
    address = models.CharField(max_length=50)
    gst = models.CharField(max_length=50)
    licence = models.CharField(max_length=50)
    status= models.CharField(max_length=10)
    image = models.ImageField()
    gst_image = models.ImageField()
    lic_image = models.ImageField()

class UOM(models.Model):
    id = models.CharField(max_length=50, primary_key='True')
    code = models.CharField(max_length=50)
    name = models.CharField(max_length=10)
    status = models.BooleanField(default=False)


class GST(models.Model):
    id = models.CharField(max_length=50, primary_key='True')
    code = models.CharField(max_length=50)
    name = models.CharField(max_length=10)
    status = models.BooleanField(default=False)

class Category(models.Model):
    id = models.CharField(max_length=50, primary_key='True')
    code = models.CharField(max_length=50)
    name = models.CharField(max_length=10)
    status = models.BooleanField(default=False)

class Designation(models.Model):
    id=models.CharField(max_length=50,primary_key='True')
    code = models.CharField(max_length=50)
    name = models.CharField(max_length=10)
    status = models.BooleanField(default=False)

class Role(models.Model):
    id=models.CharField(max_length=50,primary_key='True')
    code = models.CharField(max_length=50)
    name = models.CharField(max_length=10)
    status = models.BooleanField(default=False)

class Level(models.Model):
    id=models.CharField(max_length=50,primary_key='True')
    code = models.CharField(max_length=50)
    name = models.CharField(max_length=10)
    status = models.BooleanField(default=False)
class City(models.Model):
    id=models.CharField(max_length=50,primary_key='True')
    code = models.CharField(max_length=50)
    name = models.CharField(max_length=10)
    status = models.BooleanField(default=False)

class State(models.Model):
    id=models.CharField(max_length=50,primary_key='True')
    code = models.CharField(max_length=50)
    name = models.CharField(max_length=10)
    status = models.BooleanField(default=False)


class Warehouse(models.Model):
    code = models.CharField(max_length=50)
    name = models.CharField(max_length=10)

class ItemList(models.Model):
    item_code = models.CharField(max_length=50)
    item_name = models.CharField(max_length=50)
    hsn = models.CharField(max_length=50)
    gst = models.CharField(max_length=50)
    category = models.CharField(max_length=50)
    manufacture = models.CharField(max_length=50)
    uom = models.CharField(max_length=50)
    free_quantity = models.CharField(max_length=50)
    lpp= models.CharField(max_length=50)
    mrp=models.IntegerField(max_length=10,null=True )
    sno=models.IntegerField(null=True)

class WarehouseList(models.Model):
    wh_id = models.CharField(max_length=50)
    wh_manager = models.CharField(max_length=50)
    wh_name = models.CharField(max_length=50)
    contact_no = models.CharField(max_length=50)
    address = models.CharField(max_length=50)
    gst = models.CharField(max_length=50)
    licence = models.CharField(max_length=50)
    pan = models.CharField(max_length=50)
    image = models.ImageField()
    pan_image = models.ImageField()
    gst_image = models.ImageField()
    lic_image = models.ImageField()



class VendorList(models.Model):
    vendor_code = models.CharField(max_length=50)
    vendor_name = models.CharField(max_length=50)
    pan = models.CharField(max_length=50)
    gst = models.CharField(max_length=50)
    gstattach=models.ImageField(null=True, default=None, blank=True)
    pan_attach = models.ImageField(null=True, default=None, blank=True)
    contact_name = models.CharField(max_length=50)
    email = models.CharField(max_length=50)
    address = models.CharField(max_length=50)
    contact_no = models.IntegerField()

class Filter(models.Model):
    des = models.CharField(max_length=50)
    roles = models.CharField(max_length=10)
    category = models.CharField(max_length=10)
    states = models.CharField(max_length=10)
    levels = models.CharField(max_length=10)
    city= models.CharField(max_length=10)
    GST = models.CharField(max_length=10)

class Store(models.Model):
    Store_name=models.CharField(max_length=50, blank = True, null = True)
    store_file = models.ImageField(null=True, default=None, blank=True)
    legal_name = models.CharField(max_length=50, blank = True, null = True)
    select_region = models.CharField(max_length=50, blank = True, null = True)
    gst_No = models.CharField(max_length=50, blank = True, null = True)
    gst_attach = models.ImageField(null=True, default=None, blank=True)
    pan_card = models.CharField(max_length=50, blank = True, null = True)
    pan_attach = models.ImageField(null=True, default=None, blank=True)
    food_licence = models.CharField(max_length=50, blank = True, null = True)
    food_attach = models.ImageField(null=True, default=None, blank=True)
    trade_licence = models.CharField(max_length=50, blank = True, null = True)
    trade_attach = models.ImageField(null=True, default=None, blank=True)
    store_location = models.CharField(max_length=50, blank = True, null = True)
    address = models.CharField(max_length=50, blank = True, null = True)
    pincode = models.ImageField(max_length=10)
    state = models.CharField(max_length=50, blank = True, null = True)
    contact_person = models.CharField(max_length=50, blank = True, null = True)
    mobile = models.ImageField(max_length=10)
    remarks = models.CharField(max_length=50, blank = True, null = True)
    #region = models.CharField(max_length=50)
    region =  models.ForeignKey(Region, null=True, blank=True, on_delete=models.SET_NULL, related_name='regions')

class Grn(models.Model):
    vendor_name = models.CharField(max_length=50, blank=True, null=True)
    inv_id = models.IntegerField()
    inv_date = models.DateField(null=True, blank=True, auto_now=True)
    inv_amount = models.IntegerField()
    grn = models.CharField(max_length=50)
    quantity = models.IntegerField()
    mrp = models.IntegerField()
    status=models.CharField(max_length=50)


class Grn_item_list(models.Model):
    item_name = models.CharField(max_length=50, blank = True, null = True)
    hsn = models.CharField(max_length=50, blank = True, null = True)
    UOM = models.CharField(max_length=50, blank = True, null = True)
    expiry_date =models.DateField(null=True,blank=True,auto_now=True)
    image = models.ImageField(max_length=10)
    quantity = models.IntegerField()
    mrp=models.IntegerField()

class InventoryList(models.Model):
    cp_sno =  models.IntegerField()
    itemcode =  models.CharField(max_length=50, blank = True, null = True)
    itemname =  models.CharField(max_length=50, blank = True, null = True)
    qty = models.IntegerField()
    freeqty =  models.IntegerField()
   #netqty =  models.IntegerField()
    manufacturername =  models.CharField(max_length=50, blank = True, null = True)
    batchcode =  models.CharField(max_length=50, blank = True, null = True)
    expirydate = models.DateField(null=True,blank=True,auto_now=True)
    displayexpiry=models.DateField(null=True,blank=True,auto_now=True)
    mrp =  models.IntegerField(null=True,blank=True)
    margin =  models.IntegerField(null=True,blank=True)

class user(models.Model):
    user_Id = models.IntegerField()
    user_name = models.CharField(max_length=50)
    mobile = models.CharField(max_length=50)
    email = models.EmailField()
    designation=models.CharField(max_length=50)
    role=models.CharField(max_length=50)
    level=models.CharField(max_length=50)
    region=models.CharField(max_length=50)
    image=models.ImageField(max_length=10)
class SaleItemList(models.Model):
    code=models.CharField(max_length=50, blank = True, null = True)
    name=models.CharField(max_length=10, blank = True, null = True)
    batch=models.CharField(max_length=10, blank = True, null = True)
    expdate=models.DateField(null=True,blank=True,auto_now=True)
    hsn=models.CharField(max_length=50, blank = True, null = True)
    mrp=models.DecimalField(max_digits = 5,decimal_places = 2)
    manufacture=models.CharField(max_length=50, blank = True, null = True)
    qty=models.IntegerField()
    img=models.ImageField(max_length=10)

class DeliveryChallan(models.Model):
        id = models.AutoField(auto_created = True,primary_key = True)
        storename = models.CharField(max_length=50, blank=True, null=True)
        sonumber =models.CharField(max_length=50, blank = True, null = True)
        itemcount = models.IntegerField()
        date = models.DateField(null=True,blank=True,auto_now=True)
        dcnumber = models.CharField(max_length=50, blank = True, null = True)
        total =models.DecimalField(max_digits = 5,decimal_places = 2)
        status = models.CharField(max_length=50, blank = True, null = True)


class Indent_Item_List(models.Model):
    sno = models.IntegerField()
    indent_no= models.CharField(max_length=50, blank = True, null = True)
    item_name= models.CharField(max_length=50, blank = True, null = True)
    item_code= models.CharField(max_length=50, blank = True, null = True)
    qty=models.IntegerField()
    mrp= models.IntegerField()
    status= models.CharField(max_length=50, blank = True, null = True)
    dispatch_qty=models.IntegerField()
    batch_code= models.CharField(max_length=50, blank = True, null = True)
    expirydate= models.DateField(null=True,blank=True,auto_now=True)
    remarks= models.CharField(max_length=50, blank = True, null = True)

class Indent_List(models.Model):
    sno=models.IntegerField(),
    indent_no=models.CharField(max_length=50, blank = True, null = True),
    warehouse_name=models.CharField(max_length=50, blank = True, null = True),
    warehouse_id=models.CharField(max_length=50, blank = True, null = True),
    region_name=models.CharField(max_length=50, blank = True, null = True),
    region_id=models.CharField(max_length=50, blank = True, null = True),
    remarks=models.CharField(max_length=50, blank = True, null = True),
    createdby=models.DateField(null=True,blank=True,auto_now=True),
    createdon =models.DateField(null=True,blank=True,auto_now=True)








