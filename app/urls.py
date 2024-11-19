from django.urls import path
from .views import *

urlpatterns = [
    path('sign-in/', signin, name='signin'),
    path('dashboard/', dashboard, name='dashboard'),
    path('sign_out/', sign_out, name='sign_out'),



    path('station/', station, name='station'),
    path('add-station/', add_station, name='add_station'),
    path('edit-station/<int:station_id>/', edit_station, name='edit_station'),
    path('delete-station/<int:station_id>/', delete_station, name='delete_station'),


     path('products/', product, name='products'),
    path('add-product/', add_product, name='add_product'),
    path('edit-product/<int:product_id>/', edit_product, name='edit_product'),
    path('delete-product/<int:product_id>/', delete_product, name='delete_product'),


    path('suppliers/', supplier_list, name='suppliers'),
    path('add-supplier/', add_supplier, name='add_supplier'),
    path('edit-supplier/<int:id>/', edit_supplier, name='edit_supplier'),
    path('delete-supplier/<int:id>/', delete_supplier, name='delete_supplier'),


    path('sales/', sale_list, name='sale'),
    path('get-category-price/<int:category_id>/', get_category_price, name='get_category_price'),
    path('add-sale/', add_sale, name='add_sale'),
    path('edit-sale/<int:sale_id>/', edit_sale, name='edit_sale'),
    path('receipt-sale/<int:sale_id>/',sale_receipt, name='sale_receipt'),
    path('delete-sale/<int:sale_id>/', delete_sale, name='delete_sale'),



    path('purchase/', purchase, name='purchase'),
    path('add-purchase/', add_purchase, name='add_purchase'),
    path('edit-purchase/<int:purchase_id>/', edit_purchase, name='edit_purchase'),
    path('receipt-purchase/<int:purchase_id>/', purchase_receipt, name='purchase_receipt'),
    path('delete-purchase/<int:purchase_id>/', delete_purchase, name='delete_purchase'),



    path('inventory/', fuel_inventory_list, name='inventory'),
    path('fuel-inventory/add/', add_fuel_inventory, name='add_fuel_inventory'),
    path('fuel-inventory/edit/<int:inventory_id>/', edit_fuel_inventory, name='edit_fuel_inventory'),
    path('fuel-inventory/delete/<int:inventory_id>/', delete_fuel_inventory, name='delete_fuel_inventory'),



    path('reports/', report_list, name='report_list'),
    path('reports/generate/', generate_report, name='generate_report'),
]