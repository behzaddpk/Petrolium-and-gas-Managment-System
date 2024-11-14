from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from app.models import *
from app.froms import *

# Create your views here.


def signin(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')


        user = authenticate(request, email=email, password=password)

        if not user:
            messages.error(request, 'Invalid username or password')
        else:
            login(request, user)
            return redirect('dashboard')


    return render(request, 'sign-in.html')




def dashboard(request):
    return render(request, 'dashboard.html')


def station(request):
    stations = Station.objects.all()

    return render(request, 'station/station.html', {'stations': stations})



def add_station(request):
    if request.method == 'POST':
        name = request.POST['name']
        address = request.POST['address']
        contact = request.POST['contact']
        capacity = request.POST['capacity']



        if not name or not address or not contact or not capacity:
            messages.error(request, "All fields are required.")
            return redirect('station')  # Redirect back to the station page

        # Create and save the new station
        station = Station(name=name, location=address, contact_number=contact, capacity=capacity)
        station.save()

        # Return a success message or JSON response
        messages.success(request, "Station added successfully.")
        return redirect('station') 

        
    