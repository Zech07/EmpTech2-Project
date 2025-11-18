# deliveries/forms.py
from django import forms
from .models import Delivery

class DeliveryStatusForm(forms.ModelForm):
    class Meta:
        model = Delivery
        fields = ['status']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'})
        }
