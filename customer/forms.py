from . import models
from django import forms

class OrderForm(forms.ModelForm):
    class Meta:
        model = models.CustomerProfile
        fields = ['phone_number', 'address', 'order']