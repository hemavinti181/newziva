from django.urls import path,include

from ziva_app import views


urlpatterns = [
    path('',views.index,name='index_page'),
    path('login', views.login, name='login'),
    path('signout',views.signout,name='signout'),
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
    path('user_edit', views.user_edit, name='user_edit'),
    path('user_status_active',views.user_status_active,name='vendor_status_active'),
    path('user_status_inactive',views.user_status_inactive,name='vendor_status_inactive'),
    path('add_grn',views.add_grn,name='add_grn'),
    path('add_grnitem/<str:id>/', views.add_grnitem,name='add_grnitem'),
    path('add_grnitem_list/<str:id>/', views.add_grnitem_list,name='add_grnitem_list'),
    path("grn_reject",views.grn_reject,name='grn_reject'),
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
    path('grn_new_pending_status',views.grn_new_pending_status,name='grn_new_pending_status'),
    path('grn_new_verified_status', views.grn_new_verified_status, name='grn_new_verified_status'),
    path('grn_verified_status',views.grn_verified_status,name='grn_verified_status'),
    path('add_pending_grn_inventory',views.add_pending_grn_inventory,name='add_pending_grn_inventory'),
    path('get_item_data',views.get_item_data,name='get_item_data'),
    path('pending_indent_ack',views.pending_indent_ack,name='pending_indent_ack'),
    path('pending_indent_pending',views.pending_indent_pending,name='pending_indent_pending'),
    path('pending_indent_pending1',views.pending_indent_pending1,name='pending_indent_pending1'),
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
    path('readyto_ship1',views.readyto_ship1,name='readyto_ship1'),
    #path('partially_supplied',views.partially_supplied,name='partially_supplied'),
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
    path('deliver_challan_update',views.deliver_challan_update,name='deliver_challan_update'),
    path('taxinvoice/<str:id>/',views.taxinvoice,name='taxinvoice'),
    path('get_sale_item',views.get_sale_item,name='get_sale_item'),
    path('edit_sale_item',views.edit_sale_item,name='edit_sale_item'),
    path('deliver_challan_approve',views.deliver_challan_approve,name='deliver_challan_approve'),
    path('get_price',views.get_price,name='get_price'),
    path('deliver_challan_item_update',views.deliver_challan_item_update,name='deliver_challan_item_update'),
    path('medeliver_challan',views.medeliver_challan,name='medeliver_challan'),
    path('get_salebus',views.get_salebus,name='get_salebus'),
    path('medeliver_challan_pending',views.medeliver_challan_pending,name='medeliver_challan_pending'),
    path('live_inventory',views.live_inventory,name='live_inventory'),
    path('batch_codeexpry/<str:id>/',views.batch_codeexpry,name='batch_codeexpry'),
    path('batch_codeexpry1/<str:id>/',views.batch_codeexpry1,name='batch_codeexpry1'),
    path('add_apending_grn_inventory1',views.add_apending_grn_inventory1,name='add_apending_grn_inventory1'),
    path('grn_list1',views.grn_list1,name='grn_list1'),
    path('add_grnitem_list1/<str:id>/',views.add_grnitem_list1,name='add_grnitem_list1'),
    path('delete_stk_item/<str:id>/',views.delete_stk_item,name='delete_stk_item'),
    path('edit_stk_item',views.edit_stk_item,name='edit_stk_item'),
    path('qtyupdate_readytoship',views.qtyupdate_readytoship,name='qtyupdate_readytoship'),
    path('edit_stkbus_item',views.edit_stkbus_item,name='edit_stkbus_item'),
    path('edit_stkdepo_item',views.edit_stkdepo_item,name='edit_stkdepo_item'),
    path('delete_stkdepo_item/<str:id>/',views.delete_stkdepo_item,name='delete_stkdepo_item'),
    path('delete_stkbus_item/<str:id>/',views.delete_stkbus_item,name='delete_stkbus_item'),
    path('sales_admin_list',views.sales_admin_list,name='sales_admin_list'),
    path('sales_admin_approvelist',views.sales_admin_approvelist,name='sales_admin_approvelist'),
    path('get_storetype',views.get_storetype,name='get_storetype'),
    path('edit_storetype',views.edit_storetype,name='edit_storetype'),
    path('get_case', views.get_case, name='get_case'),
    path('edit_case', views.edit_case, name='edit_case'),
    path('get_category', views.get_category, name='get_category'),
    path('edit_category', views.edit_category, name='edit_category'),
    path('get_gst', views.get_gst, name='get_gst'),
    path('edit_gst', views.edit_gst, name='edit_gst'),
    path('get_city', views.get_city, name='get_city'),
    path('edit_city', views.edit_city, name='edit_city'),
    path('get_level', views.get_level, name='get_level'),
    path('edit_level', views.edit_level, name='edit_level'),
    path('get_role', views.get_role, name='get_role'),
    path('edit_role', views.edit_role, name='edit_role'),
    path('get_state', views.get_state, name='get_state'),
    path('edit_state', views.edit_state, name='edit_state'),
    path('get_pricelist', views.get_pricelist, name='get_pricelist'),
    path('edit_price', views.edit_price, name='edit_price'),
    path('payment_report',views.payment_report,name='payment_report'),
    path('depot_stock/<str:id>/',views.depot_stock,name='depot_stock'),
    path('depot_stock1',views.depot_stock1,name='depot_stock1'),
    path('Vendor_itemsply',views.Vendor_itemsply,name='Vendor_itemsply'),
    path('depot_indent_report',views.depot_indent_report,name='depot_indent_report'),
    path('busstation_stalls',views.busstation_stalls,name='busstation_stalls'),
    path('depot_qtyissued',views.depot_qtyissued,name='depot_qtyissued'),
    path('get_price1',views.get_price1,name='get_price1'),
    path('busstation_stock/<str:id>/',views.busstation_stock,name='busstation_stock'),
    path('warehouse_stock',views.warehouse_stock,name='warehouse_stock'),
    path('payment', views.payment, name='payment'),
    path('qr_response',views.qr_response,name='qr_response'),
    path('response/<str:order_id>/<str:paymentmode>/<str:sonumber>/<str:date>/<str:spelloftheday>/<str:remarks>/', views.response, name='response'),
    path('out_passlist1',views.out_passlist1,name='out_passlist1'),
    path('pending_indent_admin',views.pending_indent_admin,name='pending_indent_admin'),
    path('taxinvoice_list_admin',views.taxinvoice_list_admin,name='taxinvoice_list_admin'),
    path('depot_qtyissued1',views.depot_qtyissued1,name='depot_qtyissued1'),
    path('region_stock/<str:id>/',views.region_stock,name='region_stock'),
    path('region_stock1/<str:id>/',views.region_stock1,name='region_stock1'),
    path('ready_toship_admin',views.ready_toship_admin,name='ready_toship_admin'),
    path('outpass_list_admin',views.outpass_list_admin,name='outpass_list_admin'),
    path('approve_list_admin', views.approve_list_admin, name='approve_list_admin'),
    path('depot_stock_new/<str:id>/',views.depot_stock_new,name='depot_stock_new'),
    path('busstation_stock1/<str:id>/',views.busstation_stock1,name='busstation_stock1'),
    path('warehouse_stock1/<str:id>/',views.warehouse_stock1,name='warehouse_stock1'),
    path('deletetax_admin/<str:id>/',views.deletetax_admin,name='deletetax_admin'),
    path('dashboard',views.dashboard,name='dashboard'),
    path('region_payment',views.region_payment,name='region_payment'),
    path('warehouse_items',views.warehouse_items,name='warehouse_items'),
    path('depo_payment',views.depo_payment,name='depo_payment'),
    path('bus_payment',views.bus_payment,name='bus_payment'),
    path('region_items',views.region_items,name='region_items'),
    path('depo_items',views.depo_items,name='depo_items'),
    path('bus_items',views.bus_items,name='bus_items'),
    path('sales_dashboard',views.sales_dashboard,name='sales_dashboard'),
    path('indent_list_approve',views.indent_list_approve,name='indent_list_approve'),
    path('add_indentitem/<str:id>/',views.add_indentitem,name='add_indentitem'),
    path('get_indentitem',views.get_indentitem,name='get_indentitem'),
    path('pending_indent_item_list/<str:id>/',views.pending_indent_item_list,name='pending_indent_item_list'),
    path('qr_code',views.qr_code,name='qr_code'),
    path('location_map/<str:id>/',views.location_map,name='location_map'),
    path('sale_item_list_approve/<str:id>/',views.sale_item_list_approve,name='sale_item_list_approve'),
    path('indent_item_list_approve/<str:id>/',views.indent_item_list_approve,name='indent_item_list_approve'),
    path('internal_consumption',views.internal_consumption,name='internal_consumption'),
    path('delete_indent',views.delete_indent,name='delete_indent'),
    path('delete_indent_item',views.delete_indent_item,name='delete_indent_item'),
    path('add_bussupply',views.add_bussupply,name='add_bussupply'),
    path('return_bussupply',views.return_bussupply,name='return_bussupply'),
    path('depo_servicenum',views.depo_servicenum,name='depo_servicenum'),
    path('create_indent_admin',views.create_indent_admin,name='create_indent_admin'),
    path('service_details',views.service_details,name='service_details'),
    path('staffnumber', views.staffnumber, name='staffnumber'),
    path('staffname',views.staffname,name='staffname'),
    path('vehicallist',views.vehicallist,name='vehicallist'),
    path('producttype',views.producttype,name='producttype'),
    path('returnsconsumption',views.returnsconsumption,name='returnsconsumption'),
    path('create_depoindent',views.create_depoindent,name='create_depoindent'),
    path('create_busindent',views.create_busindent,name='create_busindent'),
    path('authorize_staffid',views.authorize_staffid,name='authorize_staffid'),
    path('depot_dashboard',views.depot_dashboard,name='depot_dashboard'),
    path('zonal_dashboard',views.zonal_dashboard,name='zonal_dashboard'),
    path('depot_dashboard_data',views.depot_dashboard_data,name='depot_dashboard_data'),
    path('depot_pendin_sales',views.depot_pendin_sales,name='depot_pendin_sales'),
    path('complete_sale_report',views.complete_sale_report,name='complete_sale_report'),
    path('bust_dashboard',views.bust_dashboard,name='bust_dashboard'),
    path('bust_dashboard_data', views.bust_dashboard_data, name='bust_dashboard_data'),
    path('bust_pendin_sales', views.bust_pendin_sales, name='bust_pendin_sales'),
    path('bust_complete_sale_report', views.bust_complete_sale_report, name='bust_complete_sale_report'),
    path('zonal_dashboard_data', views.zonal_dashboard_data, name='zonal_dashboard_data'),
    path('zonal_dashboard_data1', views.zonal_dashboard_data1, name='zonal_dashboard_data1'),
    path('zonal_grn_report', views.zonal_grn_report, name='zonal_grn_report'),
    path('zonal_depotwise_data', views.zonal_depotwise_data, name='zonal_depotwise_data'),
    path('admin_dashboard',views.admin_dashboard,name='admin_dashboard'),
    path('zonal_depotindent_data',views.zonal_depotindent_data,name='zonal_depotindent_data'),
    path('depot_dashboard_data1',views.depot_dashboard_data1,name='depot_dashboard_data1'),
    path('bust_dashboard_data1',views.bust_dashboard_data1,name='bust_dashboard_data1'),
    path('zonal_depotwise_data1',views.zonal_depotwise_data1,name='zonal_depotwise_data1'),
    path('stock_tranfer_admin',views.stock_tranfer_admin,name='stock_tranfer_admin'),
    path('intconsump_stocktransfer',views.intconsump_stocktransfer,name='intconsump_stocktransfer'),
    path('intconsump_report',views.intconsump_report,name='intconsump_report'),
    path('intconsump_dashboard',views.intconsump_dashboard,name='intconsump_dashboard'),
    path('intconsump_dashboard_data',views.intconsump_dashboard_data,name='intconsump_dashboard_data'),
    path('driverwise_shortage',views.driverwise_shortage,name='driverwise_shortage'),
    path('servicewise_shortage',views.servicewise_shortage,name='servicewise_shortage'),
    path('region_payment_new',views.region_payment_new,name='region_payment_new'),
    path('depot_payment_new',views.depot_payment_new,name='depot_payment_new'),
    path('bust_payment_new',views.bust_payment_new,name='bust_payment_new'),
    path('driverwise_sub_shortage',views.driverwise_sub_shortage,name='driverwise_sub_shortage'),
    path('get_whinventory',views.get_whinventory,name='get_whinventory'),
    path('service_wise_shortage',views.service_wise_shortage,name='service_wise_shortage'),
    path('internal_stktransfer',views.internal_stktransfer,name='internal_stktransfer'),
    path('approve_list_admin1',views.approve_list_admin1,name='approve_list_admin'),
    path('vehcals_list',views.vehcals_list,name='vehcals_list'),
    path('internal_consump_stock',views.internal_consump_stock,name='internal_consump_stock'),
    path('delete_sales',views.delete_sales,name='delete_sales'),
    path('delete_deliverchallan', views.delete_deliverchallan, name='delete_deliverchallan'),
    path('delete_pendindent',views.delete_pendindent,name='delete_pendindent'),
    path('edit_grn',views.edit_grn,name='edit_grn'),
    path('grn_search',views.grn_search,name='grn_search'),
    path('get_grn_item',views.get_grn_item,name='get_grn_item'),
    path('delete_salesitem',views.delete_salesitem,name='delete_salesitem'),
    path('delete_deliverchallanitem',views.delete_deliverchallanitem,name='delete_deliverchallanitem'),
    path('edit_grn_item',views.edit_grn_item,name='edit_grn_item'),
    path('delete_grn_item', views.delete_grn_item, name='delete_grn_item'),
    path('delete_intconsumption', views.delete_intconsumption, name='delete_intconsumption'),
    path('indent_item_update',views.indent_item_update,name='indent_item_update'),
    path('get_dclist',views.get_dclist,name='get_dclist'),
    path('get_consumption',views.get_consumption,name='get_consumption'),
    path('edit_consumption',views.edit_consumption,name='edit_consumption'),
    path('generate_transid',views.generate_transid,name='generate_transid'),
    path('generate_transid_bust',views.generate_transid_bust,name='generate_transid_bust'),
    path('stk_warehouse_list',views.stk_warehouse_list,name='stk_warehouse_list'),
    path('stk_depot_list',views.stk_depot_list,name='stk_depot_list'),
    path('stk_region_list',views.stk_region_list,name='stk_region_list'),
    path('stk_busstation_list',views.stk_busstation_list,name='stk_busstation_list'),
    path('warehouseinventory_search',views.warehouseinventory_search,name='warehouseinventory_search'),
    path('wh_item_add_admin',views.wh_item_add_admin,name='wh_item_add_admin'),
    path('wh_item_list_admin',views.wh_item_list_admin,name='wh_item_list_admin'),
    path('complete_stk_admin',views.complete_stk_admin,name='complete_stk_admin'),
    path('get_ps_stock',views.get_ps_stock,name='get_ps_stock'),
    path('get_user',views.get_user,name='get_user'),
    path('get_ps',views.get_ps,name='get_ps'),
    path('get_sms',views.get_sms,name='get_sms'),
    path('submit_sms',views.submit_sms,name='submit_sms'),
    path('submitreturn_sms', views.submitreturn_sms, name='submitreturn_sms'),
    path('businventory_search',views.businventory_search,name='businventory_search'),
    path('bus_item_list_admin',views.bus_item_list_admin,name='bus_item_list_admin'),
    path('bust_item_add_admin',views.bust_item_add_admin,name='bust_item_add_admin'),
    path('complete_busstk_admin',views.complete_busstk_admin,name='complete_busstk_admin'),
    path('service_master',views.service_master,name='service_master'),
    path('vehical_master',views.vehical_master,name='vehical_master'),
    path('driver_master',views.driver_master,name='driver_master'),
    path('add_driver_master',views.add_driver_master,name='add_driver_master'),
    path('get_driver',views.get_driver,name="get_driver"),
    path('edit_driver',views.edit_driver,name='edit_driver'),
    path('add_service_master',views.add_service_master,name='add_service_master'),
    path('add_vehical_master',views.add_vehical_master,name='add_vehical_master'),
    path('get_servicelist',views.get_servicelist,name='get_servicelist'),
    path('edit_service', views.edit_service, name='edit_service'),
    path('delete_driver',views.delete_driver,name='delete_driver'),
    path('delete_vehicle',views.delete_vehicle,name='delete_vehicle'),
    path('delete_service',views.delete_service,name='delete_service'),
    path('get_vehicle',views.get_vehicle,name='get_vehicle'),
    path('edit_vehcle',views.edit_vehcle,name='edit_vehcle'),
    path('intconsumption_report',views.intconsumption_report,name='intconsumption_report'),
    path('intconsumption_servicereport',views.intconsumption_servicereport,name='intconsumption_servicereport'),
    path('generate_transid_depo',views.generate_transid_depo,name='generate_transid_depo'),
    path('depot_item_add_admin',views.depot_item_add_admin,name='depot_item_add_admin'),
    path('depotinventory_search',views.depotinventory_search,name='depotinventory_search'),
    path('depot_item_list_admin',views.depot_item_list_admin,name='depot_item_list_admin'),
    path('complete_depostk_admin',views.complete_depostk_admin,name='complete_depostk_admin'),
    path('return_otp',views.return_otp,name='return_otp'),
    path('get_stocklist',views.get_stocklist,name='get_stocklist'),
    #path('internal_stktransfer_admin',views.internal_stktransfer_admin,name='internal_stktransfer'),
]


