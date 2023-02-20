from django.contrib import admin

# Register your models here.
from .models import UOM, Region, Category, ItemList, VendorList, WarehouseList, Designation, StoreList, SaleItemList, \
    CarBrand

admin.site.register(UOM)

admin.site.register(Region)

admin.site.register(Category)

admin.site.register(ItemList)

admin.site.register(VendorList)

admin.site.register(WarehouseList)

admin.site.register(Designation)

admin.site.register(StoreList)

admin.site.register(SaleItemList)

admin.site.register(CarBrand)
