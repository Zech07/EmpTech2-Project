from . import models
from django import forms

class Change_Status(forms.ModelForm):
    class Meta:
        model = models.Order
        fields = ['jug_status']

class Update_Customer(froms.ModelForm):
    class Meta:
        model = models.Order
        fields = ['first_name', 'last_name', 'phone_number', 'jug_tag']
