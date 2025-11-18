from django.db import models
from django.utils import timezone


class Delivery(models.Model):

    STATUS_CHOICES = [
        ('transporting', 'Transporting'),
        ('delivered','Delivered'),
        ('picked_up','Picked_up'),
    ]

    customer = models.ForeignKey('pos.Customer', on_delete=models.CASCADE, related_name='deliveries')
    order = models.ForeignKey(
        'pos.Order',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='deliveries'
        )

    customer_name = models.CharField(max_length=100)
    address = models.TextField()
    contact_number = models.CharField(max_length=20, blank=True)
    date = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    amount = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)

    def __str__(self):
        return f"{self.customer.name} - {self.status}"
