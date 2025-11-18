from django import forms
from .models import Delivery

class TrackForm(forms.ModelForm):
    class Meta:
        model = Delivery
        # Only include fields that actually exist in Delivery
        fields = ['order', 'status']  # 'order' links to the customer/order
