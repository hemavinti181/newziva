# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models



class AndroidPermissions(models.Model):
    sno = models.AutoField(primary_key=True)
    menu = models.CharField(max_length=100)
    submenu = models.CharField(max_length=100)
    tsubmenu = models.CharField(max_length=90)
    titlename = models.CharField(max_length=90)
    dashboardtitle = models.CharField(max_length=100)
    weblinks = models.CharField(max_length=60)
    packagename = models.CharField(max_length=200)
    classname = models.CharField(max_length=90)
    classtype = models.CharField(max_length=50)
    substatus = models.CharField(max_length=30)
    d_icons = models.CharField(db_column='d-icons', max_length=50)  # Field renamed to remove unsuitable characters.
    side_icons = models.CharField(db_column='side-icons', max_length=50)  # Field renamed to remove unsuitable characters.
    status = models.CharField(max_length=30)
    ioscontrollers = models.CharField(max_length=50)
    web_icons = models.CharField(max_length=50)

    class Meta:
        managed = False
        db_table = 'android_permissions'


class BusstationInventory(models.Model):
    sno = models.AutoField(primary_key=True)
    indent_transferid = models.CharField(max_length=50)
    indentaccept_date = models.DateTimeField()
    vendorcode = models.CharField(max_length=20)
    vendor_name = models.CharField(max_length=25)
    itemcode = models.CharField(max_length=20)
    itemname = models.CharField(max_length=200)
    original_qty = models.FloatField()
    original_freeqty = models.FloatField()
    original_uom = models.CharField(max_length=20)
    original_pf = models.IntegerField()
    original_purchaseprice = models.FloatField()
    original_purchasevalue = models.FloatField()
    original_mrp = models.FloatField()
    original_mrpvalue = models.FloatField()
    sale_qty = models.FloatField()
    sale_freeqty = models.FloatField()
    sale_uom = models.CharField(max_length=20)
    sale_pf = models.FloatField()
    purchase_price = models.FloatField()
    purchase_value = models.FloatField()
    margin = models.FloatField()
    mrp = models.FloatField()
    hsn = models.CharField(max_length=10)
    gst_per = models.FloatField()
    batchcode = models.CharField(max_length=20)
    expiry_date = models.DateField()
    createdon = models.DateTimeField()
    createdby = models.CharField(max_length=10)
    modifiedon = models.DateTimeField()
    modifiedby = models.CharField(max_length=10)
    ipaddress = models.CharField(max_length=20)
    busstation_id = models.CharField(max_length=20)
    is_active = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'busstation_inventory'


class BusstationMaster(models.Model):
    sno = models.AutoField(primary_key=True)
    busatation_id = models.CharField(max_length=40)
    busstationname = models.CharField(max_length=35)
    depoid = models.CharField(max_length=50)
    deponame = models.CharField(max_length=35)
    region_id = models.CharField(max_length=50)
    regionname = models.CharField(max_length=50)
    warehouseid = models.CharField(max_length=50)
    warehousename = models.CharField(max_length=60)
    busstation_manager = models.CharField(max_length=50)
    busstation_contact_no = models.CharField(max_length=35)
    created_by = models.CharField(max_length=20)
    created_on = models.DateTimeField()
    modified_by = models.CharField(max_length=35)
    modified_on = models.DateTimeField()
    status = models.CharField(max_length=20)

    class Meta:
        managed = False
        db_table = 'busstation_master'


class Cashvoucher(models.Model):
    sno = models.AutoField(primary_key=True)
    voucher_id = models.CharField(unique=True, max_length=30)
    amount = models.FloatField()
    branch = models.CharField(max_length=40)
    expense_type_ref = models.IntegerField()
    expense_cat_ref = models.IntegerField()
    expense_details = models.CharField(max_length=150)
    is_approved = models.IntegerField()
    approved_by = models.CharField(max_length=20)
    is_audited = models.IntegerField()
    audited_by = models.CharField(max_length=20)
    is_finance_approved = models.IntegerField()
    finance_approved_by = models.CharField(max_length=20)
    approval_remarks = models.CharField(max_length=150)
    audit_remarks = models.CharField(max_length=150)
    finance_remarks = models.CharField(max_length=150)
    created_on = models.DateTimeField()
    created_by = models.CharField(max_length=20)
    status = models.TextField()
    modified_on = models.DateTimeField()
    modified_by = models.CharField(max_length=20)
    receivied_by = models.CharField(max_length=20)
    receivid_on = models.DateTimeField()
    approved_on = models.DateTimeField()
    auditapproved_on = models.DateTimeField()
    financeapproved_on = models.DateTimeField()
    pay_mode = models.CharField(max_length=10)

    class Meta:
        managed = False
        db_table = 'cashvoucher'


class DcGenerate(models.Model):
    sno = models.AutoField(primary_key=True)
    so_number = models.CharField(max_length=20)
    dc_number = models.CharField(max_length=20)
    del_agent_name = models.CharField(max_length=30)
    contactno = models.CharField(max_length=20)
    vehicle_details = models.CharField(max_length=50)
    remarks = models.CharField(max_length=200)
    created_by = models.CharField(max_length=20)
    created_on = models.DateTimeField()
    modified_by = models.CharField(max_length=20)
    modified_on = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'dc_generate'


class DepoCodes(models.Model):
    sno = models.AutoField(primary_key=True)
    depocode = models.CharField(max_length=20)
    ordanization_code = models.CharField(max_length=20)
    deponame = models.CharField(max_length=20)

    class Meta:
        managed = False
        db_table = 'depo_codes'


class DepoInventory(models.Model):
    sno = models.AutoField(primary_key=True)
    indent_transferid = models.CharField(max_length=50)
    indentaccept_date = models.DateTimeField()
    vendorcode = models.CharField(max_length=20)
    vendor_name = models.CharField(max_length=25)
    itemcode = models.CharField(max_length=20)
    itemname = models.CharField(max_length=200)
    original_qty = models.FloatField()
    original_freeqty = models.FloatField()
    original_uom = models.CharField(max_length=20)
    original_pf = models.IntegerField()
    original_purchaseprice = models.FloatField()
    original_purchasevalue = models.FloatField()
    original_mrp = models.FloatField()
    original_mrpvalue = models.FloatField()
    sale_qty = models.FloatField()
    sale_freeqty = models.FloatField()
    sale_uom = models.CharField(max_length=20)
    sale_pf = models.FloatField()
    purchase_price = models.FloatField()
    purchase_value = models.FloatField()
    margin = models.FloatField()
    mrp = models.FloatField()
    hsn = models.CharField(max_length=10)
    gst_per = models.FloatField()
    batchcode = models.CharField(max_length=20)
    expiry_date = models.DateField()
    createdon = models.DateTimeField()
    createdby = models.CharField(max_length=10)
    modifiedon = models.DateTimeField()
    modifiedby = models.CharField(max_length=10)
    ipaddress = models.CharField(max_length=20)
    region_id = models.CharField(max_length=10)
    is_active = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'depo_inventory'



class DepoMaster(models.Model):
    sno = models.AutoField(primary_key=True)
    depoid = models.CharField(max_length=50)
    depocode = models.CharField(max_length=20)
    org_code = models.CharField(max_length=20)
    depo_name = models.CharField(max_length=50)
    deponame = models.CharField(max_length=50)
    regionid = models.CharField(max_length=10)
    regionname = models.TextField()
    location = models.CharField(max_length=40)
    warehouse = models.CharField(max_length=35)
    warehouseid = models.CharField(max_length=50)
    depo_manager = models.TextField()
    depo_contact_no = models.CharField(max_length=35)
    address = models.CharField(max_length=25)
    gst_no = models.CharField(max_length=30)
    gstattach = models.TextField()
    licenseno = models.CharField(max_length=35)
    licenceattach = models.TextField()
    image = models.TextField()
    createdby = models.CharField(max_length=10)
    createdon = models.DateTimeField()
    modifiedby = models.CharField(max_length=10)
    modifiedon = models.DateTimeField()
    status = models.CharField(max_length=10)

    class Meta:
        managed = False
        db_table = 'depo_master'


class DepoQtyApril(models.Model):
    sno = models.AutoField(primary_key=True)
    region = models.CharField(max_length=40)
    depo = models.CharField(max_length=20)
    depoid = models.CharField(max_length=25)
    id = models.CharField(max_length=20)
    april = models.CharField(max_length=25)
    may = models.CharField(db_column='May', max_length=30)  # Field name made lowercase.
    june = models.CharField(max_length=20)

    class Meta:
        managed = False
        db_table = 'depo_qty_April'


class DepoVehiclesData(models.Model):
    sno = models.AutoField(primary_key=True)
    deponame = models.CharField(max_length=50)
    vehicleno = models.CharField(max_length=50)
    department = models.CharField(max_length=20)

    class Meta:
        managed = False
        db_table = 'depo_vehicles_data'


class DjangoContentType(models.Model):
    name = models.CharField(max_length=100)
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'


class DjangoMigrations(models.Model):
    id = models.BigAutoField(primary_key=True)
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DropdownFilter(models.Model):
    filtername = models.CharField(max_length=50)

    class Meta:
        managed = False
        db_table = 'dropdown_filter'


class Dropdownmaster(models.Model):
    sno = models.AutoField(primary_key=True)
    ddcode = models.CharField(max_length=15)
    category = models.CharField(max_length=30)
    displayname = models.CharField(max_length=60)
    isactive = models.IntegerField()
    createdon = models.DateTimeField()
    createdby = models.CharField(max_length=10)
    modifiedon = models.DateTimeField()
    modifiedby = models.CharField(max_length=10)

    class Meta:
        managed = False
        db_table = 'dropdownmaster'


class ExpenseCatMaster(models.Model):
    sno = models.AutoField(primary_key=True)
    expense_category = models.CharField(max_length=50)
    created_on = models.DateTimeField()
    created_by = models.CharField(max_length=20)
    is_active = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'expense_cat_master'


class ExpenseTypeMaster(models.Model):
    sno = models.AutoField(primary_key=True)
    expense_type = models.CharField(max_length=50)
    created_on = models.DateTimeField()
    created_by = models.CharField(max_length=20)
    is_active = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'expense_type_master'


class GenerateIndent(models.Model):
    sno = models.AutoField(primary_key=True)
    indent_no = models.CharField(max_length=30)
    to_name = models.CharField(max_length=60)
    to_id = models.CharField(max_length=30)
    from_name = models.CharField(max_length=60)
    from_id = models.CharField(max_length=30)
    remarks = models.CharField(max_length=60)
    createdby = models.CharField(max_length=10)
    to_loginid = models.CharField(max_length=20)
    orderdate = models.DateField()
    createdon = models.DateTimeField()
    modifiedby = models.CharField(max_length=10)
    modifiedon = models.DateTimeField()
    status = models.CharField(max_length=20)
    acceptedby = models.CharField(max_length=10)
    aceptedon = models.DateTimeField()
    acknowledgement_on = models.DateTimeField()
    acknowledgement_by = models.CharField(max_length=10)

    class Meta:
        managed = False
        db_table = 'generate_indent'


class Grn(models.Model):
    warehouse_id = models.CharField(max_length=20)
    grn = models.CharField(unique=True, max_length=20)
    vendor_id = models.IntegerField()
    vendorname = models.CharField(max_length=60)
    invoice_id = models.CharField(max_length=25)
    invoice_date = models.DateField()
    invoice_amount = models.FloatField()
    round_off = models.FloatField()
    created_by = models.CharField(max_length=25)
    created_on = models.DateTimeField()
    modified_by = models.CharField(max_length=20)
    modified_on = models.DateTimeField()
    grn_remarks = models.CharField(max_length=500)
    audit_apr = models.TextField()
    audit_by = models.CharField(max_length=20)
    audit_on = models.DateTimeField()
    audit_remarks = models.CharField(max_length=500)
    grn_approval = models.CharField(max_length=5)
    approved_by = models.CharField(max_length=15)
    approved_on = models.DateTimeField()
    comments = models.CharField(max_length=100)
    inventory_stat = models.CharField(max_length=25)
    status = models.CharField(max_length=10)
    source = models.IntegerField()
    stockpoint = models.CharField(max_length=40)
    itemcount = models.BigIntegerField()
    total = models.FloatField()

    class Meta:
        managed = False
        db_table = 'grn'


class GrnItem(models.Model):
    grn = models.CharField(max_length=15)
    item_code = models.CharField(max_length=25)
    hsn = models.CharField(max_length=10)
    item_name = models.CharField(max_length=150)
    quantity = models.FloatField()
    uom = models.CharField(max_length=30)
    freestock = models.FloatField()
    purchase_price = models.FloatField()
    afterdis = models.FloatField()
    purchase_value = models.FloatField()
    sales_price = models.FloatField()
    sales_value = models.FloatField()
    mrp = models.FloatField()
    gst_type = models.CharField(max_length=10)
    gst_percent = models.FloatField()
    gst_val = models.FloatField()
    sgst = models.FloatField()
    igst = models.FloatField()
    cgst = models.FloatField()
    total = models.FloatField()
    base_total = models.FloatField()
    created_by = models.CharField(max_length=25)
    created_on = models.DateTimeField()
    batch_no = models.CharField(max_length=20)
    expiry_date = models.DateField()
    manufacturer = models.CharField(max_length=25)
    inv_sno = models.IntegerField()
    modified_by = models.CharField(max_length=10)
    modified_on = models.DateTimeField()
    status = models.CharField(max_length=15)
    source = models.IntegerField()
    reject_status = models.IntegerField()
    reject_reason = models.CharField(max_length=300)

    class Meta:
        managed = False
        db_table = 'grn_item'


class IndentDc(models.Model):
    sno = models.AutoField(primary_key=True)
    indentno = models.CharField(max_length=50)
    dc_number = models.CharField(max_length=20)
    from_name = models.CharField(max_length=30)
    from_id = models.CharField(max_length=50)
    to_name = models.CharField(max_length=50)
    to_id = models.CharField(max_length=50)
    remarks = models.CharField(max_length=200)
    created_by = models.CharField(max_length=20)
    to_loginid = models.CharField(max_length=20)
    created_on = models.DateTimeField()
    modified_by = models.CharField(max_length=20)
    modified_on = models.DateTimeField()
    status = models.CharField(max_length=20)
    type = models.CharField(max_length=20)

    class Meta:
        managed = False
        db_table = 'indent_dc'


class IndentDcitem(models.Model):
    sno = models.AutoField(primary_key=True)
    dc_number = models.CharField(max_length=50)
    indent_no = models.CharField(max_length=30)
    item_name = models.CharField(max_length=50)
    item_code = models.CharField(max_length=30)
    qty = models.BigIntegerField()
    uom = models.CharField(max_length=20)
    mrp = models.BigIntegerField()
    status = models.CharField(max_length=50)
    dispatch_qty = models.BigIntegerField()
    dispatched_by = models.CharField(max_length=10)
    dispatched_on = models.DateTimeField()
    batch_code = models.CharField(max_length=30)
    expiry_date = models.DateField()
    remarks = models.CharField(max_length=50)
    createdby = models.CharField(max_length=10)
    to_loginid = models.CharField(max_length=20)
    createdon = models.DateTimeField()
    modifiedby = models.CharField(max_length=10)
    modifiedon = models.DateTimeField()
    type = models.CharField(max_length=20)

    class Meta:
        managed = False
        db_table = 'indent_dcitem'


class IndentItem(models.Model):
    sno = models.AutoField(primary_key=True)
    indent_no = models.CharField(max_length=30)
    item_name = models.CharField(max_length=50)
    item_code = models.CharField(max_length=30)
    qty = models.BigIntegerField()
    mrp = models.BigIntegerField()
    status = models.CharField(max_length=50)
    dispatch_qty = models.BigIntegerField()
    dispatched_by = models.CharField(max_length=10)
    dispatched_on = models.DateTimeField()
    batch_code = models.CharField(max_length=30)
    expiry_date = models.DateField()
    orderdate = models.DateField()
    remarks = models.CharField(max_length=50)
    createdby = models.CharField(max_length=10)
    to_loginid = models.CharField(max_length=20)
    createdon = models.DateTimeField()
    modifiedby = models.CharField(max_length=10)
    modifiedon = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'indent_item'


class IndentLogs(models.Model):
    sno = models.AutoField(primary_key=True)
    indent_no = models.CharField(max_length=30)
    remarks = models.CharField(max_length=100)
    status = models.CharField(max_length=50)
    outpass_num = models.CharField(max_length=50)
    created_by = models.CharField(max_length=50)
    created_byname = models.CharField(max_length=50)
    created_on = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'indent_logs'


class Inventory(models.Model):
    sno = models.AutoField(primary_key=True)
    grn_no = models.CharField(max_length=20)
    grn_date = models.DateTimeField()
    vendorcode = models.CharField(max_length=20)
    vendor_name = models.CharField(max_length=25)
    itemcode = models.CharField(max_length=20)
    itemname = models.CharField(max_length=200)
    original_qty = models.FloatField()
    original_freeqty = models.FloatField()
    original_uom = models.CharField(max_length=20)
    original_pf = models.IntegerField()
    original_purchaseprice = models.FloatField()
    original_purchasevalue = models.FloatField()
    original_mrp = models.FloatField()
    original_mrpvalue = models.FloatField()
    sale_qty = models.FloatField()
    sale_freeqty = models.FloatField()
    sale_uom = models.CharField(max_length=20)
    sale_pf = models.FloatField()
    purchase_price = models.FloatField()
    purchase_value = models.FloatField()
    margin = models.FloatField()
    mrp = models.FloatField()
    hsn = models.CharField(max_length=10)
    gst_per = models.FloatField()
    batchcode = models.CharField(max_length=20)
    expiry_date = models.DateField()
    createdon = models.DateTimeField()
    createdby = models.CharField(max_length=10)
    modifiedon = models.DateTimeField()
    modifiedby = models.CharField(max_length=10)
    ipaddress = models.CharField(max_length=20)
    storecode = models.CharField(max_length=10)
    is_active = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'inventory'


class Itemmaster(models.Model):
    sno = models.AutoField(primary_key=True)
    itemcode = models.CharField(max_length=20)
    item_code_org = models.CharField(max_length=20)
    itemname = models.CharField(max_length=200)
    hsncode = models.CharField(max_length=20)
    lpp = models.IntegerField()
    gst = models.IntegerField()
    mrp = models.IntegerField()
    category = models.CharField(max_length=20)
    manufacturername = models.CharField(max_length=50)
    isactive = models.IntegerField()
    createdon = models.DateTimeField()
    createdby = models.CharField(max_length=10)
    modifiedon = models.DateTimeField()
    modifiedby = models.CharField(max_length=10)
    inactive_by = models.CharField(max_length=35)
    inactive_on = models.DateTimeField()
    uom = models.CharField(max_length=20)
    image = models.CharField(max_length=500)

    class Meta:
        managed = False
        db_table = 'itemmaster'


class LoginPermissions(models.Model):
    sno = models.AutoField(primary_key=True)
    type = models.CharField(max_length=100)
    sidemenupermissions = models.CharField(max_length=100)
    dashboardpermissions = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'login_permissions'


class Logins(models.Model):
    sno = models.AutoField(primary_key=True)
    userid = models.CharField(max_length=10)
    username = models.CharField(max_length=50)
    mobile = models.BigIntegerField()
    emailid = models.CharField(max_length=150)
    region = models.CharField(max_length=30)
    regionid = models.CharField(max_length=50)
    warehouseid = models.CharField(max_length=50)
    warehousename = models.CharField(max_length=50)
    depoid = models.CharField(max_length=25)
    deponame = models.CharField(max_length=40)
    busstationid = models.CharField(max_length=20)
    busstationname = models.CharField(max_length=50)
    level = models.CharField(max_length=30)
    designation = models.CharField(max_length=30)
    image = models.CharField(max_length=200)
    role = models.CharField(max_length=20)
    role2 = models.CharField(max_length=50)
    accesskey = models.CharField(max_length=150)
    password = models.CharField(max_length=150)
    otp = models.CharField(max_length=6)
    isactive = models.IntegerField()
    createdon = models.DateTimeField()
    createdby = models.CharField(max_length=10)
    modifiedon = models.DateTimeField()
    modifiedby = models.CharField(max_length=10)
    lastlogin = models.DateTimeField()
    dummy1 = models.CharField(max_length=50)
    tokenid = models.CharField(max_length=150)
    udid = models.CharField(max_length=60)
    androidversion = models.CharField(max_length=20)
    sidemenupermissions = models.CharField(max_length=150)
    web_submenu = models.CharField(max_length=70)
    dashboardpermissions = models.CharField(max_length=50)
    id = models.CharField(max_length=35)

    class Meta:
        managed = False
        db_table = 'logins'


class Logs(models.Model):
    sno = models.AutoField(primary_key=True)
    so_number = models.CharField(max_length=30)
    paymentmode = models.CharField(max_length=20)
    remarks = models.CharField(max_length=150)
    stauts = models.CharField(max_length=50)
    createdby = models.CharField(max_length=10)
    createdon = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'logs'


class Nationality(models.Model):
    sno = models.AutoField(primary_key=True)
    category = models.CharField(max_length=20)
    sub_category = models.CharField(max_length=30)
    country = models.CharField(max_length=30)
    nationality = models.CharField(max_length=40)
    status = models.CharField(max_length=10)

    class Meta:
        managed = False
        db_table = 'nationality'


class OutpassGenerate(models.Model):
    sno = models.AutoField(primary_key=True)
    indent_no = models.CharField(max_length=50)
    dc_number = models.CharField(max_length=50)
    outpass_number = models.CharField(max_length=20)
    warehouse_name = models.CharField(max_length=30)
    warehouseid = models.CharField(max_length=50)
    regionid = models.CharField(max_length=50)
    region_name = models.CharField(max_length=50)
    remarks = models.CharField(max_length=200)
    vehiclenumber = models.CharField(max_length=20)
    drivername = models.CharField(max_length=50)
    created_by = models.CharField(max_length=20)
    to_loginid = models.CharField(max_length=20)
    created_on = models.DateTimeField()
    modified_by = models.CharField(max_length=20)
    modified_on = models.DateTimeField()
    status = models.CharField(max_length=20)
    type = models.CharField(max_length=20)

    class Meta:
        managed = False
        db_table = 'outpass_generate'


class OutpassItem(models.Model):
    sno = models.AutoField(primary_key=True)
    outpass_number = models.CharField(max_length=50)
    dc_number = models.CharField(max_length=50)
    indent_no = models.CharField(max_length=30)
    item_name = models.CharField(max_length=50)
    item_code = models.CharField(max_length=30)
    qty = models.BigIntegerField()
    remaining_qty = models.CharField(max_length=20)
    mrp = models.BigIntegerField()
    status = models.CharField(max_length=50)
    dispatch_qty = models.BigIntegerField()
    dispatched_by = models.CharField(max_length=10)
    dispatched_on = models.DateTimeField()
    batch_code = models.CharField(max_length=30)
    expiry_date = models.DateField()
    remarks = models.CharField(max_length=50)
    vehiclenumber = models.CharField(max_length=20)
    drivername = models.CharField(max_length=50)
    createdby = models.CharField(max_length=10)
    to_loginid = models.CharField(max_length=20)
    createdon = models.DateTimeField()
    modifiedby = models.CharField(max_length=10)
    modifiedon = models.DateTimeField()
    type = models.CharField(max_length=20)

    class Meta:
        managed = False
        db_table = 'outpass_item'


class PharmacyCustomers(models.Model):
    sno = models.AutoField(primary_key=True)
    id_number = models.CharField(max_length=20)
    customer_name = models.CharField(max_length=50)
    customer_mobile = models.CharField(max_length=20)
    customer_mail = models.CharField(max_length=50)
    createdby = models.CharField(max_length=50)
    createdon = models.DateTimeField()
    modifiedby = models.CharField(max_length=50)
    modifiedon = models.DateTimeField()
    ipaddress = models.CharField(max_length=20)
    status = models.CharField(max_length=20)

    class Meta:
        managed = False
        db_table = 'pharmacy_customers'


class PriceMaster(models.Model):
    sno = models.AutoField(primary_key=True)
    price_code = models.CharField(max_length=30)
    region_name = models.CharField(max_length=50)
    region_code = models.CharField(max_length=50)
    item_code = models.CharField(max_length=50)
    item_name = models.CharField(max_length=50)
    mrp = models.FloatField()
    created_by = models.CharField(max_length=25)
    created_on = models.DateTimeField()
    modified_by = models.CharField(max_length=25)
    modified_on = models.DateTimeField()
    status = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'price_master'


class RegionMaster(models.Model):
    sno = models.AutoField(primary_key=True)
    region_id = models.CharField(max_length=40)
    region_code = models.CharField(max_length=20)
    regionname = models.CharField(max_length=35)
    warehouseid = models.CharField(max_length=50)
    warehousename = models.CharField(max_length=35)
    region_manager = models.CharField(max_length=50)
    region_contact_no = models.CharField(max_length=35)
    created_by = models.CharField(max_length=20)
    created_on = models.DateTimeField()
    modified_by = models.CharField(max_length=35)
    modified_on = models.DateTimeField()
    status = models.CharField(max_length=20)

    class Meta:
        managed = False
        db_table = 'region_master'


class SaleBillingTrack(models.Model):
    sno = models.AutoField(primary_key=True)
    cp_sno = models.IntegerField()
    inv_item_sno = models.IntegerField()
    tax_invovice = models.CharField(max_length=20)
    itemcode = models.CharField(max_length=20)
    itemname = models.CharField(max_length=150)
    quantity = models.FloatField()
    saleprice = models.FloatField()
    salevalue = models.FloatField()
    createdby = models.CharField(max_length=25)
    createdon = models.DateTimeField()
    modifiedby = models.CharField(max_length=25)
    modifiedon = models.DateTimeField()
    credit_debit = models.CharField(max_length=20)
    status = models.CharField(max_length=30)

    class Meta:
        managed = False
        db_table = 'sale_billing_track'


class SaleItem(models.Model):
    inventory_id = models.IntegerField()
    so_number = models.CharField(max_length=15)
    item_code = models.CharField(max_length=25)
    hsn = models.CharField(max_length=25)
    item_name = models.CharField(max_length=150)
    quantity = models.FloatField()
    free_qty = models.IntegerField()
    return_qty = models.FloatField()
    margin = models.FloatField()
    original_mrp = models.FloatField()
    purchase_price = models.FloatField()
    purchase_value = models.FloatField()
    after_dis_pur_price = models.FloatField()
    after_dis_pur_value = models.FloatField()
    saleprice = models.FloatField()
    salevalue = models.FloatField()
    disper = models.FloatField()
    disprice = models.FloatField()
    disvalue = models.FloatField()
    mrp = models.FloatField()
    mrpvalue = models.FloatField()
    uom = models.CharField(max_length=20)
    packing = models.CharField(max_length=30)
    gst_percent = models.FloatField()
    gst_price = models.FloatField()
    total_gst = models.FloatField()
    total = models.FloatField()
    orderdate = models.DateField()
    created_on = models.DateTimeField()
    created_by = models.CharField(max_length=15)
    batch_no = models.CharField(max_length=15)
    expiry_date = models.DateField()
    manufacturer = models.CharField(max_length=25)
    modified_on = models.DateTimeField()
    modified_by = models.CharField(max_length=25)
    item_status = models.CharField(max_length=10)
    order_status = models.CharField(max_length=15)
    txin_status = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'sale_item'


class Sales(models.Model):
    inv_no = models.CharField(max_length=20)
    dc_number = models.CharField(max_length=35)
    to_id = models.CharField(max_length=50)
    to_name = models.CharField(max_length=60)
    from_name = models.CharField(max_length=70)
    from_id = models.CharField(max_length=50)
    patient_name = models.CharField(max_length=30)
    mobile = models.BigIntegerField()
    item_count = models.IntegerField()
    qty_count = models.IntegerField()
    purchase_value = models.FloatField()
    after_dis_pur_value = models.FloatField()
    item_val = models.FloatField()
    gst_val = models.CharField(max_length=10)
    item_dis_val = models.FloatField()
    discount = models.FloatField()
    discount_val = models.FloatField()
    net_val = models.FloatField()
    after_val = models.FloatField()
    avg_margin = models.FloatField()
    receivedamt = models.FloatField()
    returnamt = models.FloatField()
    customer_type = models.CharField(max_length=20)
    doctorname = models.CharField(max_length=50)
    doctorno = models.CharField(max_length=20)
    paymenttype = models.CharField(max_length=20)
    paymentmode = models.CharField(max_length=20)
    referenceno = models.CharField(max_length=100)
    saletype = models.CharField(max_length=20)
    staffname = models.CharField(max_length=30)
    spelloftheday = models.CharField(max_length=20)
    created_on = models.DateTimeField()
    created_by = models.CharField(max_length=25)
    modified_on = models.DateTimeField()
    modified_by = models.CharField(max_length=25)
    status = models.CharField(max_length=30)
    remarks = models.CharField(max_length=140)
    delivery_date = models.DateField()

    class Meta:
        managed = False
        db_table = 'sales'


class StockTransfer(models.Model):
    sno = models.AutoField(primary_key=True)
    transitid = models.CharField(max_length=35)
    storeid = models.CharField(max_length=30)
    from_stock = models.CharField(max_length=35)
    from_stockid = models.CharField(max_length=30)
    to_stock = models.CharField(max_length=30)
    to_stockid = models.CharField(max_length=30)
    quantity = models.IntegerField()
    itemcount = models.IntegerField()
    totalvalue = models.IntegerField()
    created_by = models.CharField(max_length=35)
    to_loginid = models.CharField(max_length=20)
    created_on = models.DateTimeField()
    modified_by = models.CharField(max_length=20)
    modified_on = models.DateTimeField()
    status = models.CharField(max_length=30)
    remarks = models.CharField(max_length=140)
    approved_by = models.CharField(max_length=50)
    approvedon = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'stock_transfer'


class StockTransferTrack(models.Model):
    sno = models.IntegerField()
    cp_sno = models.IntegerField()
    inv_item_sno = models.IntegerField()
    tax_invovice = models.CharField(max_length=20)
    itemcode = models.CharField(max_length=20)
    itemname = models.CharField(max_length=150)
    quantity = models.FloatField()
    createdby = models.CharField(max_length=25)
    createdon = models.DateTimeField()
    modifiedby = models.CharField(max_length=25)
    modifiedon = models.DateTimeField()
    status = models.CharField(max_length=30)

    class Meta:
        managed = False
        db_table = 'stock_transfer_track'


class StocktranferItem(models.Model):
    sno = models.AutoField(primary_key=True)
    transit_id = models.CharField(max_length=20)
    inventory_id = models.IntegerField()
    item_code = models.CharField(max_length=20)
    hsn = models.CharField(max_length=20)
    item_name = models.CharField(max_length=20)
    quantity = models.CharField(max_length=30)
    free_qty = models.CharField(max_length=30)
    return_qty = models.IntegerField()
    total = models.IntegerField()
    created_on = models.DateTimeField()
    created_by = models.CharField(max_length=20)
    batch_no = models.CharField(max_length=20)
    expiry_date = models.DateField()
    manufacturer = models.CharField(max_length=30)
    modified_on = models.DateTimeField()
    modified_by = models.CharField(max_length=20)
    item_status = models.CharField(max_length=20)
    order_status = models.CharField(max_length=30)

    class Meta:
        managed = False
        db_table = 'stocktranfer_item'


class Storemaster(models.Model):
    sno = models.AutoField(primary_key=True)
    storecode = models.CharField(max_length=10)
    storecodeid = models.CharField(max_length=20)
    storename = models.TextField()
    store_photo = models.TextField()
    legal_name = models.CharField(max_length=40)
    region = models.CharField(max_length=35)
    region_id = models.CharField(max_length=50)
    depoid = models.CharField(max_length=40)
    depo = models.CharField(max_length=35)
    warehouse = models.CharField(max_length=35)
    warehouseid = models.CharField(max_length=20)
    bus_station = models.CharField(max_length=40)
    busstation_id = models.CharField(max_length=20)
    contact_person = models.CharField(max_length=35)
    mobile_no = models.BigIntegerField()
    alternate_mobileno = models.CharField(max_length=20)
    gstnumber = models.CharField(max_length=15)
    gstattach = models.TextField()
    pancard = models.CharField(max_length=10)
    tradelicenceno = models.TextField()
    tlattach = models.TextField()
    foodlicence = models.TextField()
    flattach = models.TextField()
    storelocation = models.TextField()
    storeaddress = models.TextField()
    city = models.CharField(max_length=35)
    state = models.CharField(max_length=25)
    pincode = models.IntegerField()
    cluster = models.CharField(max_length=25)
    panattach = models.TextField()
    remarks = models.CharField(max_length=50)
    storetype = models.CharField(max_length=50)
    natureofbusiness = models.CharField(max_length=50)
    is_active = models.IntegerField()
    createdby = models.CharField(max_length=10)
    createdon = models.DateTimeField()
    modifiedby = models.CharField(max_length=10)
    modifiedon = models.DateTimeField()
    email_id = models.CharField(max_length=60)

    class Meta:
        managed = False
        db_table = 'storemaster'


class StoremasterBackup(models.Model):
    sno = models.AutoField(primary_key=True)
    storecode = models.CharField(max_length=10)
    storecodeid = models.CharField(max_length=20)
    storename = models.TextField()
    store_photo = models.TextField()
    legal_name = models.CharField(max_length=40)
    region = models.CharField(max_length=35)
    region_id = models.CharField(max_length=50)
    depoid = models.CharField(max_length=40)
    depo = models.CharField(max_length=35)
    warehouse = models.CharField(max_length=35)
    warehouseid = models.CharField(max_length=20)
    bus_station = models.CharField(max_length=40)
    busstation_id = models.CharField(max_length=20)
    contact_person = models.CharField(max_length=35)
    mobile_no = models.BigIntegerField()
    alternate_mobileno = models.CharField(max_length=20)
    gstnumber = models.CharField(max_length=15)
    gstattach = models.TextField()
    pancard = models.CharField(max_length=10)
    tradelicenceno = models.TextField()
    tlattach = models.TextField()
    foodlicence = models.TextField()
    flattach = models.TextField()
    storelocation = models.TextField()
    storeaddress = models.TextField()
    city = models.CharField(max_length=35)
    state = models.CharField(max_length=25)
    pincode = models.IntegerField()
    cluster = models.CharField(max_length=25)
    panattach = models.TextField()
    remarks = models.CharField(max_length=50)
    storetype = models.CharField(max_length=50)
    natureofbusiness = models.CharField(max_length=50)
    is_active = models.IntegerField()
    createdby = models.CharField(max_length=10)
    createdon = models.DateTimeField()
    modifiedby = models.CharField(max_length=10)
    modifiedon = models.DateTimeField()
    email_id = models.CharField(max_length=60)

    class Meta:
        managed = False
        db_table = 'storemaster_backup'


class SubmitCall(models.Model):
    sno = models.AutoField(primary_key=True)
    store_id = models.CharField(max_length=50)
    storename = models.CharField(max_length=100)
    remarks = models.CharField(max_length=200)
    mobile = models.BigIntegerField()
    latitude = models.FloatField()
    longitude = models.FloatField()
    location = models.CharField(max_length=200)
    created_by = models.CharField(max_length=50)
    created_on = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'submit_call'


class TaxInvoice(models.Model):
    sno = models.AutoField(primary_key=True)
    client_id = models.CharField(max_length=20)
    legal_name = models.CharField(max_length=30)
    tax_invoice_number = models.CharField(max_length=30)
    dc_number = models.CharField(max_length=20)
    so_number = models.CharField(max_length=20)
    paymentmode = models.CharField(max_length=20)
    created_by = models.CharField(max_length=10)
    created_on = models.DateTimeField()
    modified_by = models.CharField(max_length=10)
    modified_on = models.DateTimeField()
    status = models.CharField(max_length=10)

    class Meta:
        managed = False
        db_table = 'tax_invoice'


class Vendormaster(models.Model):
    sno = models.AutoField(primary_key=True)
    vendorcode = models.CharField(max_length=20)
    vendorname = models.CharField(max_length=100)
    warehouseid = models.CharField(max_length=20)
    warehousename = models.CharField(max_length=20)
    region = models.CharField(max_length=20)
    region_id = models.CharField(max_length=20)
    depo = models.CharField(max_length=20)
    depoid = models.CharField(max_length=20)
    bus_station = models.CharField(max_length=20)
    busstation_id = models.CharField(max_length=20)
    druglicenseno = models.TextField()
    dlattach = models.TextField()
    gstno = models.CharField(max_length=15)
    gstattach = models.TextField()
    pancardno = models.CharField(max_length=10)
    panattach = models.TextField()
    contactperson = models.CharField(max_length=50)
    contactno = models.BigIntegerField()
    emailid = models.CharField(max_length=150)
    address = models.TextField()
    pincode = models.CharField(max_length=6)
    state = models.CharField(max_length=20)
    city = models.CharField(max_length=25)
    fssai = models.CharField(max_length=20)
    storecode = models.CharField(max_length=10)
    isactive = models.IntegerField()
    createdon = models.DateTimeField()
    createdby = models.CharField(max_length=10)
    modifiedon = models.DateTimeField()
    modifiedby = models.CharField(max_length=10)
    approvedby = models.CharField(max_length=10)
    approvedon = models.DateTimeField()
    isapproved = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'vendormaster'


class WarehouseInventory(models.Model):
    sno = models.AutoField(primary_key=True)
    indent_transferid = models.CharField(max_length=50)
    indentaccept_date = models.DateTimeField()
    vendorcode = models.CharField(max_length=20)
    vendor_name = models.CharField(max_length=25)
    itemcode = models.CharField(max_length=20)
    itemname = models.CharField(max_length=200)
    original_qty = models.FloatField()
    original_freeqty = models.FloatField()
    original_uom = models.CharField(max_length=20)
    original_pf = models.IntegerField()
    original_purchaseprice = models.FloatField()
    original_purchasevalue = models.FloatField()
    original_mrp = models.FloatField()
    original_mrpvalue = models.FloatField()
    sale_qty = models.FloatField()
    sale_freeqty = models.FloatField()
    sale_uom = models.CharField(max_length=20)
    sale_pf = models.FloatField()
    purchase_price = models.FloatField()
    purchase_value = models.FloatField()
    margin = models.FloatField()
    mrp = models.FloatField()
    hsn = models.CharField(max_length=10)
    gst_per = models.FloatField()
    batchcode = models.CharField(max_length=20)
    expiry_date = models.DateField()
    createdon = models.DateTimeField()
    createdby = models.CharField(max_length=10)
    modifiedon = models.DateTimeField()
    modifiedby = models.CharField(max_length=10)
    ipaddress = models.CharField(max_length=20)
    warehouse_id = models.CharField(max_length=10)
    is_active = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'warehouse_inventory'


class WarehouseMaster(models.Model):
    sno = models.AutoField(primary_key=True)
    warehouseid = models.CharField(max_length=10)
    warehouse_code_org = models.CharField(max_length=20)
    organization_code = models.CharField(max_length=20)
    warehousename = models.TextField()
    location = models.CharField(max_length=40)
    wh_manager = models.TextField()
    wh_contact_no = models.CharField(max_length=35)
    address = models.CharField(max_length=25)
    gst_no = models.CharField(max_length=30)
    gstattach = models.TextField()
    panattach = models.TextField()
    panno = models.CharField(max_length=30)
    licenseno = models.CharField(max_length=35)
    licenceattach = models.TextField()
    image = models.TextField()
    createdby = models.CharField(max_length=10)
    createdon = models.DateTimeField()
    modifiedby = models.CharField(max_length=10)
    modifiedon = models.DateTimeField()
    status = models.CharField(max_length=10)

    class Meta:
        managed = False
        db_table = 'warehouse_master'

