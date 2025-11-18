from django.db import models
from pos.models import Customer
# Create your models here.
class CustomerProfile(models.Model):
    user = models.OneToOneField(Customer, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    order = models.IntegerField(default=0)

    def __str__(self):
        return self.user.username