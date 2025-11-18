
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
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

class Driver(models.Model):
    name = models.CharField(max_length=200)
    phone = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return self.name

# Combined Order + Delivery model
class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    paid = models.BooleanField(default=False)

    # Delivery info included in the same model
    delivery_scheduled_at = models.DateTimeField(default=timezone.now)
    delivery_status_choices = [
        ('pending', 'Pending'),
        ('in_transit', 'In Transit'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]
    delivery_status = models.CharField(max_length=20, choices=delivery_status_choices, default='pending')
    delivery_notes = models.TextField(blank=True)

    def __str__(self):
        return f"Order #{self.id} - {self.customer or 'Walk-in'}"
    def calculate_total(self):
        return sum([item.line_total() for item in self.items.all()])

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.IntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    def line_total(self):
        return self.quantity * self.unit_price

    def __str__(self):
        return f"{self.product.name} x{self.quantity}"

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