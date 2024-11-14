from django.contrib import admin
from .models import Station, FuelType, FuelInventory, Supplier, Sale, Purchase, Report

admin.site.register(Station)
admin.site.register(FuelType)
admin.site.register(FuelInventory)
admin.site.register(Supplier)
admin.site.register(Sale)
admin.site.register(Purchase)
admin.site.register(Report)
