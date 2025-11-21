from django import forms
from .models import Order, Customer
from django.contrib.auth.models import User

class ChangeStatusForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['jug_status', 'paid_status']
        widgets = {
            'jug_status': forms.Select(attrs={'class': 'form-control'}),
            'paid_status': forms.Select(attrs={'class': 'form-control'})
        }

class UpdateCustomerForm(forms.ModelForm):
    # User fields
    first_name = forms.CharField(max_length=150, required=True)
    last_name = forms.CharField(max_length=150, required=True)
    email = forms.EmailField(required=True)
    
    class Meta:
        model = Customer
        fields = ['phone', 'address', 'jug_tag']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Pre-populate User fields if instance exists
        if self.instance and self.instance.user:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
            self.fields['email'].initial = self.instance.user.email
        
        # Add CSS classes
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': 'form-control'
            })
    
    def save(self, commit=True):
        customer = super().save(commit=False)
        
        # Update User model data
        if customer.user:
            customer.user.first_name = self.cleaned_data['first_name']
            customer.user.last_name = self.cleaned_data['last_name']
            customer.user.email = self.cleaned_data['email']
            if commit:
                customer.user.save()
        
        if commit:
            customer.save()
        
        return customer