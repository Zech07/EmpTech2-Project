from django import forms
from .models import Delivery

class Change_Status(forms.ModelForm):
    class Meta:
<<<<<<< HEAD
        model = models.Order
        fields = ['jug_status']

class Update_Customer(froms.ModelForm):
    class Meta:
        model = models.Order
        fields = ['first_name', 'last_name', 'phone_number', 'jug_tag']
=======
        model = Delivery
        # Only include fields that actually exist in Delivery
        fields = ['order', 'status']  # 'order' links to the customer/order
>>>>>>> b774a21d51044f5960c809fe83a88f852e9bfce8
