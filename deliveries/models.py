from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

class Delivery(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='deliveries')
    customer_name = models.CharField(max_length=100)
    address = models.TextField()
    contact_number = models.CharField(max_length=20, blank=True)
    date = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=50, default='Pending')
    amount = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)

    def __str__(self):
        return f"{self.customer.username} - {self.status}"
