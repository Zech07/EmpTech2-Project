
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
    
class Customer(models.Model):
        user = models.OneToOneField(User, on_delete=models.CASCADE, default=None, null=True, blank=True)
        name = models.CharField(max_length=200)
        phone = models.CharField(max_length=50, blank=True)
        address = models.TextField(blank=True)
        created_at = models.DateTimeField(auto_now_add=True)
    
        def __str__(self):
            return f"{self.name} ({self.phone})"
    
    
class Product(models.Model):
        name = models.CharField(max_length=200)
        sku = models.CharField(max_length=100, blank=True)
        price = models.DecimalField(max_digits=10, decimal_places=2)
        created_at = models.DateTimeField(auto_now_add=True)
    
        def __str__(self):
            return self.name
    
    
class Inventory(models.Model):
        product = models.OneToOneField(Product, on_delete=models.CASCADE)
        quantity = models.IntegerField(default=0)
        low_threshold = models.IntegerField(default=5)
    
        def __str__(self):
            return f"{self.product.name}: {self.quantity}"
    
    
class Driver(models.Model):
        name = models.CharField(max_length=200)
        phone = models.CharField(max_length=50, blank=True)
    
        def __str__(self):
            return self.name
    
    
class Delivery(models.Model):
        STATUS_CHOICES = [
            ('pending', 'Pending'),
            ('in_transit', 'In Transit'),
            ('delivered', 'Delivered'),
            ('cancelled', 'Cancelled'),
        ]
        order = models.OneToOneField('Order', on_delete=models.CASCADE, related_name='delivery')
        scheduled_at = models.DateTimeField(default=timezone.now)
        driver = models.ForeignKey(Driver, on_delete=models.SET_NULL, null=True, blank=True)
        status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
        notes = models.TextField(blank=True)
    
        def __str__(self):
            return f"Delivery for Order #{self.order.id} - {self.status}"
    
class Order(models.Model):
        customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)
        created_at = models.DateTimeField(auto_now_add=True)
        total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
        paid = models.BooleanField(default=False)
    
        def __str__(self):
            return f"Order #{self.id} - {self.customer or 'Walk-in'}"
    
    
class OrderItem(models.Model):
        order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
        product = models.ForeignKey(Product, on_delete=models.PROTECT)
        quantity = models.IntegerField(default=1)
        unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    
        def line_total(self):
            return self.quantity * self.unit_price
    
        def __str__(self):
            return f"{self.product.name} x{self.quantity}"
    
    
class Payment(models.Model):
        PAYMENT_METHODS = [
            ('cash', 'Cash'),
            ('card', 'Card'),
            ('other', 'Other'),
        ]
        order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='payments')
        amount = models.DecimalField(max_digits=12, decimal_places=2)
        method = models.CharField(max_length=20, choices=PAYMENT_METHODS, default='cash')
        recorded_at = models.DateTimeField(auto_now_add=True)
    
        def __str__(self):
            return f"{self.method} {self.amount} on Order #{self.order.id}"
    
class Staff(models.Model):
        user = models.OneToOneField(User, on_delete=models.CASCADE, default=None, null=True, blank=True)
        full_name = models.CharField(max_length=200)
        phone = models.CharField(max_length=50, blank=True)
        position = models.CharField(max_length=100, blank=True)
        created_at = models.DateTimeField(auto_now_add=True)
    
        def __str__(self):
            return f"{self.full_name} ({self.position})"
            
class Admin(models.Model):
        user = models.OneToOneField(User, on_delete=models.CASCADE, default=None, null=True, blank=True)
        full_name = models.CharField(max_length=200)
        phone = models.CharField(max_length=50, blank=True)
        created_at = models.DateTimeField(auto_now_add=True)
    
        def __str__(self):
            return f"{self.full_name} (Admin)"