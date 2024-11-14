from django.urls import path
from .views import *

urlpatterns = [
    path('sign-in/', signin, name='signin'),
    path('dashboard/', dashboard, name='dashboard'),



    path('station/', station, name='station'),
    path('add-station/', add_station, name='add_station')
]