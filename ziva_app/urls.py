from django.urls import path,include
from ziva_app import views

urlpatterns = [
    path('',views.index,name='index_page'),
    path('login', views.login, name='login'),
    path('logout',views.logout,name='logout'),
    path('store_master',views.store_master,name='store_master'),
    path('add_store',views.add_store,name='add_store'),
    path('store_status_active',views.store_status_active,name='store_status_active'),
    path('store_status_inactive/<int:id>/',views.store_status_inactive,name='store_status_inactive'),
    path('store_edit',views.store_edit,name='store_edit'),
    path('item_list',views.item_list,name='item_master'),
    path('item_add',views.item_add,name='item_add'),
    path('item_edit',views.item_edit,name='item_edit'),
    path('item_status_active',views.item_status_active,name='item_status_active'),
    path('item_status_inactive',views.item_status_inactive,name='item_status_inactive'),
    path('des_add',views.des_add,name='des_add'),
    path('role', views.role, name='role'),
    path('level', views.level, name='level'),
    path('city', views.city, name='city'),
    path('state', views.state, name='state'),
    path('gst', views.gst, name='gst'),
    path('uom', views.uom, name='uom'),
    path('category',views.category,name='category'),
    path('des_list',views.des_list,name='des_list'),
    path('des_edit/<str:id>/',views.des_edit,name='des_edit'),
    path('role_list', views.role_list, name='role_list'),
    path('role_edit/<str:id>/',views.des_edit,name='role_edit'),
    path('level_list',views.level_list,name='level_list'),
    path('level_edit/<str:id>/', views.level_edit, name='level_edit'),
    path('city_list',views.city_list,name='city_list'),
    path('state_list',views.state_list,name='state_list'),
    path('gst_list',views.gst_list,name='gst_list'),
    path('uom_list',views.uom_list,name='uom_list'),
    path('category_list', views.category_list, name='category_list'),
    path('depo_list',views.depo_list,name='depo_list'),
    path('depo_add',views.depo_add,name='depo_add'),
    path('get_depo',views.get_depo,name='get_depo'),
    path('depo_edit', views.depo_edit, name='depo_edit'),
    path('depo_status_active',views.depo_status_active,name='depo_status_active'),
    path('depo_status_inactive',views.depo_status_inactive,name='depo_status_inactive'),
    path('get_region',views.get_region,name='get_region'),
    path('region_list',views.region_list,name='region_list'),
    path('region_add',views.region_add,name='region_add'),
    path('region_edit', views.region_edit, name='region_edit'),
    path('bus_list',views.bus_list,name='bus_list'),
    path('bus_add',views.bus_add,name='bus_add'),
    path('get_bus',views.get_bus,name='get_bus'),
    path('bus_edit', views.bus_edit, name='bus_edit'),
    path('bus_status_active',views.bus_status_active,name='depo_status_active'),
    path('depo_status_inactive',views.bus_status_inactive,name='depo_status_inactive'),
    path('warehouse_list',views.warehouse_list,name='warehouse_list'),
    path('warehouse_add1',views.warehouse_add,name='warehouse_add'),
    path('warehouse_edit',views.warehouse_edit,name='warehouse_edit'),
    path('warehouse_status_active',views.warehouse_status_active,name='warehouse_status_active'),
    path('warehouse_status_inactive',views.warehouse_status_inactive,name='warehouse_status_inactive'),
    path('vendor_add',views.vendor_add,name='vendor_add'),
    path('vendor_list',views.vendor_list,name='vendor_list'),
    path('vendor_edit/<str:id>',views.vendor_edit,name='vendor_edit'),
    path('vendor_status_active/<str:id>/',views.vendor_status_active,name='vendor_status_active'),
    path('vendor_status_inactive/<str:id>/',views.vendor_status_inactive,name='vendor_status_inactive'),
    path('user_add',views.user_add,name='user_add'),
    path('user_list',views.user_list,name='user_list'),
    path('user_status_active',views.user_status_active,name='vendor_status_active'),
    path('user_status_inactive',views.user_status_inactive,name='vendor_status_inactive'),
    path('add_grn',views.add_grn,name='add_grn'),
    path('add_grnitem', views.add_grnitem,name='add_grnitem'),
    #path('add_grnitem_list', views.add_grnitem_list,name='add_grnitem_list'),
    path('add_grn_inventory',views.add_grn_inventory,name='add_grn_inventory'),
    path('grn_list',views.grn_list,name='grn_list'),
    path('sales_item_add',views.sales_item_add,name='sales_item_add'),
    path('sale_item_list',views.sale_item_list,name='sale_item_list'),
    path('complete_sale',views.complete_sale,name='complete_sale'),
    path('deliver_challan',views.deliver_challan,name='deliver_challan'),
    path('create_indent',views.create_indent,name='create_indent'),
    path('indent_item_list/<str:id>/',views.indent_item_list,name='indent_item_list'),
    path('get_grn_item_data',views.get_grn_item_data,name='get_grn_item_data'),
    path('get_sale_item_data',views.get_sale_item_data,name='get_sale_item_data'),
    path('grn_pending_status',views.grn_pending_status,name='grn_pending_status'),
    path('grn_verified_status',views.grn_verified_status,name='grn_verified_status'),
    path('add_pending_grn_inventory',views.add_pending_grn_inventory,name='add_pending_grn_inventory'),
    path('get_item_data',views.get_item_data,name='get_item_data'),
    path('pending_indent_ack',views.pending_indent_ack,name='pending_indent_ack'),
    path('pending_indent_pending',views.pending_indent_pending,name='pending_indent_pending'),
    path('sales_list',views.sales_list,name='sales_list'),
    path('sales_list_outpass',views.sales_list_outpass,name='sales_list_outpass'),
    path('deliver_challan_status',views.deliver_challan_status,name='deliver_challan_status'),
    path('pending_ind_status',views.pending_ind_status,name='pending_ind_status'),
    path('dc_pending',views.dc_pending,name='dc_pending'),
    path('stock_transfer',views.stock_transfer,name='stock_transfer'),
    path('depo_search',views.depo_search,name='depo_search'),
    path('wh_search', views.wh_search, name='wh_search'),
    path('wh_item_add',views.wh_item_add,name='wh_item_add'),
    path('wh_item_list',views.wh_item_list,name='wh_item_list'),
    path('get_wh_item',views.get_wh_item,name='get_wh_item'),
    path('search', views.autocompleteModel,name='search'),
    path('get_warehouse',views.get_warehouse,name='get_warehouse'),
    path('get_store_data',views.get_store_data,name='get_store_data'),
    path('get_store',views.get_store,name='get_store'),
    path('store_search',views.store_search,name='store_search'),
    path('proformainvoice',views.proformainvoice,name='proformainvoice'),
    path('grn',views.grn,name='grn'),
    path('get_depregion',views.get_depregion,name='get_depregion'),
    path('get_dependent_depo',views.get_dependent_depo,name='get_dependent_depo'),
    path('get_dependent_bus',views.get_dependent_bus,name='get_dependent_bus'),
    path('indent_list',views.indent_list,name='indent_list'),
    path('readyto_ship',views.readyto_ship,name='readyto_ship'),
    path('partially_supplied',views.partially_supplied,name='partially_supplied'),
    path('indent_item_list1/<str:id>/',views.indent_item_list1,name='indent_item_list1'),
    path('update_ack',views.update_ack,name='update_ack'),
    path('generate_gate_pass',views.generate_gate_pass,name='generate_gate_pass'),
    path('indent_item_list2/<str:id>/',views.indent_item_list2,name='indent_item_list2'),
    path('out_passlist',views.out_passlist,name='out_passlist'),
    path('out_pass_itemlist/<str:id>/',views.out_pass_itemlist,name='out_pass_itemlist'),
    path('out_pass_scanner',views.out_pass_scanner,name='out_pass_scanner'),
    path('indent_item_list_ack/<str:id>/',views.indent_item_list_ack,name='indent_item_list_ack'),
    path('approved_indlist_pending',views.approved_indlist_pending,name='approved_indlist_pending'),
    path('approved_indlist_accept', views.approved_indlist_accept, name='approved_indlist_accept'),
    path('approve_item_list/<str:id>/',views.approve_item_list,name='approve_item_list'),
    path('des_status_inactive',views.des_status_inactive,name='des_status_inactive'),
    path('gst_status_inactive',views.gst_status_inactive,name='gst_status_inactive'),
    path('uom_status_inactive', views.uom_status_inactive, name='uom_status_inactive'),
    path('role_status_inactive', views.role_status_inactive, name='role_status_inactive'),
    path('level_status_inactive', views.level_status_inactive, name='level_status_inactive'),
    path('city_status_inactive', views.city_status_inactive, name='city_status_inactive'),
    path('state_status_inactive', views.state_status_inactive, name='state_status_inactive'),
    path('category_status_inactive', views.category_status_inactive, name='category_status_inactive'),
    path('approve_accept',views.approve_accept,name='approve_accept'),
    path('storetype_list',views.storetype_list,name='storetype_list'),
    path('storetype',views.storetype,name='storetype'),
    path('store_status_inactive',views.store_status_inactive,name='store_status_inactive'),
    path('get_storeregion',views.get_storeregion,name='get_storeregion'),
    path('get_storedepo',views.get_storedepo,name='get_storedepo'),
    path('get_storebus',views.get_storebus,name='get_storebus'),
    path('region_status_active',views.region_status_active,name='region_status_active'),
    path('taxinvoice_list',views.taxinvoice_list,name='taxinvoice_list'),
    path('sales_item_list_pending/<str:id>/',views.sales_item_list_pending,name='sales_item_list_pending'),
    path('depo_add_stf',views.depo_add_stf,name='depo_add_stf'),
    path('get_depo_item',views.get_depo_item,name='get_depo_item'),
    path('depo_item_add',views.depo_item_add,name='depo_item_add'),
    path('depo_item_list',views.depo_item_list,name='depo_item_list'),
    path('complete_depoinv',views.complete_depoinv,name='complete_depoinv'),
    path('complete_whinv',views.complete_whinv,name='complete_whinv'),
    path('wh_add_stf',views.wh_add_stf,name='wh_add_stf'),
    path('busstation_search',views.busstation_search,name='busstation_search'),
    path('busstation_item_add', views.busstation_item_add, name='busstation_item_add'),
    path('busstation_item_list', views.busstation_item_list, name='busstation_item_list'),
    path('busstation_depoinv', views.complete_depoinv, name='complete_depoinv'),
    path('busstation_add_stf',views.busstation_add_stf,name='busstation_add_stf'),
    path('get_busstation_item',views.get_busstation_item,name='get_busstation_item'),
    path('complete_businv',views.complete_businv,name='complete_businv'),
    path('get_proformabus',views.get_proformabus,name='get_proformabus'),
    path('get_proformastore',views.get_proformastore,name='get_proformastore'),
    path('delete_sale_item/<int:id>/',views.delete_sale_item,name='delete_sale_item'),
    path('deliver_challan_update',views.deliver_challan_update,name='deliver_challan_update')

]