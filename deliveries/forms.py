from . import models
from django import forms

class TrackForm(forms.ModelForm):
    class Meta:
        model = models.Delivery
        fields = ['customer','status' ]
