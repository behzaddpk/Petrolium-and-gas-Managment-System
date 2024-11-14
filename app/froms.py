# forms.py
from django import forms
from .models import Station

class StationForm(forms.ModelForm):
    class Meta:
        model = Station
        fields = ['name', 'location', 'capacity', 'contact_number']
        labels = {
            'name': 'Station Name',
            'location': 'Location',
            'capacity': 'Capacity (in liters)',
            'contact_number': 'Contact Number'
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter station name'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter location'}),
            'capacity': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter capacity'}),
            'contact_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter contact number'}),
        }
