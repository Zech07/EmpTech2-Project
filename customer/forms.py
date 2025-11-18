from pos.models import OrderItem
from django import forms

class OrderForm(forms.ModelForm):
    class Meta:
        model = OrderItem
        fields = ['quantity']