
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models import Sum
from django.core.exceptions import ValidationError
import re

class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, default=None, null=True, blank=True, related_name='customer')
    phone = models.CharField(max_length=50, blank=True)
    address = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    jug_tag = models.CharField(max_length=100, blank=True)
    amount_due = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    @property
    def name(self):
        if self.user:
            return f"{self.user.first_name} {self.user.last_name}".strip()
        return "Unknown Customer"

    def __str__(self):
        return f"{self.name} ({self.phone})"

    def clean(self):
        if not self.user and not self.phone:
            raise ValidationError("Either a user account or phone number is required.")
        
        # Validate phone format
        if self.phone and not re.match(r'^\+?[\d\s\-\(\)]{10,}$', self.phone):
            raise ValidationError("Please enter a valid phone number.")
        
        if self.amount_due < 0:
            raise ValidationError("Amount due cannot be negative.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

class Staff(models.Model):
    POSITION_CHOICES = [
        ('admin', 'Administrator'),
        ('driver', 'Driver'),
        ('staff', 'General Staff'),
        ('manager', 'Manager'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='staff')
    phone = models.CharField(max_length=50, blank=True)
    position = models.CharField(max_length=20, choices=POSITION_CHOICES, default='staff')
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    @property
    def full_name(self):
        return f"{self.user.first_name} {self.user.last_name}"

    def __str__(self):
        return f"{self.full_name} ({self.get_position_display()})"

    def is_admin(self):
        return self.position == 'admin'
    
    def is_driver(self):
        return self.position == 'driver'

    def clean(self):
        if self.phone and not re.match(r'^\+?[\d\s\-\(\)]{10,}$', self.phone):
            raise ValidationError("Please enter a valid phone number.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

# Remove separate Admin and Driver models - use Staff with positions instead
# class Admin(models.Model):  # ❌ Remove this
# class Driver(models.Model): # ❌ Remove this

class Order(models.Model):
    JUG_STATUS_CHOICES = [
        ('picked_up', 'Picked Up'),
        ('transporting', 'Transporting'),
        ('delivered', 'Delivered'),
        ('refilling', 'Refilling'),
    ]

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='orders')
    order_date = models.DateTimeField(default=timezone.now)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    paid_status = models.BooleanField(default=False)
    jug_status = models.CharField(
        max_length=20,
        choices=JUG_STATUS_CHOICES,
        default='picked_up'
    )
    assigned_driver = models.ForeignKey(
        Staff, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        limit_choices_to={'position': 'driver', 'is_active': True}
    )
    
    @property
    def total_amount(self):
        return self.amount

    @property
    def jug_tag(self):
        """Get jug_tag from the associated customer"""
        return self.customer.jug_tag

    def __str__(self):
        return f"Order #{self.id} - {self.customer.name} - {self.order_date.strftime('%Y-%m-%d')}"

    def clean(self):
        if self.amount <= 0:
            raise ValidationError("Order amount must be greater than zero.")
        
        if self.assigned_driver and not self.assigned_driver.is_driver():
            raise ValidationError("Assigned staff member must be a driver.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-order_date']
        indexes = [
            models.Index(fields=['order_date']),
            models.Index(fields=['paid_status']),
            models.Index(fields=['jug_status']),
        ]

class Sales(models.Model):
    date = models.DateField(default=timezone.now, unique=True)
    daily_sales = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    @property
    def weekly_sales(self):
        return get_weekly_sales(self.date)

    @property
    def monthly_sales(self):
        return get_monthly_sales(self.date)

    @property
    def yearly_sales(self):
        return get_yearly_sales(self.date)

    def __str__(self):
        return f"Sales for {self.date}"

    def clean(self):
        if self.daily_sales < 0:
            raise ValidationError("Daily sales cannot be negative.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name_plural = "Sales"
        ordering = ['-date']
        indexes = [
            models.Index(fields=['date']),
        ]

# Utility functions for sales calculations
def get_weekly_sales(date=None):
    """Get weekly sales for a given date (defaults to today)"""
    if date is None:
        date = timezone.now().date()
    
    start_of_week = date - timezone.timedelta(days=date.weekday())
    end_of_week = start_of_week + timezone.timedelta(days=6)
    
    return Sales.objects.filter(
        date__range=[start_of_week, end_of_week]
    ).aggregate(total=Sum('daily_sales'))['total'] or 0

def get_monthly_sales(date=None):
    """Get monthly sales for a given date (defaults to today)"""
    if date is None:
        date = timezone.now().date()
    
    start_of_month = date.replace(day=1)
    if date.month == 12:
        end_of_month = date.replace(year=date.year + 1, month=1, day=1)
    else:
        end_of_month = date.replace(month=date.month + 1, day=1)
    end_of_month = end_of_month - timezone.timedelta(days=1)
    
    return Sales.objects.filter(
        date__range=[start_of_month, end_of_month]
    ).aggregate(total=Sum('daily_sales'))['total'] or 0

def get_yearly_sales(date=None):
    """Get yearly sales for a given date (defaults to today)"""
    if date is None:
        date = timezone.now().date()
    
    start_of_year = date.replace(month=1, day=1)
    end_of_year = date.replace(month=12, day=31)
    
    return Sales.objects.filter(
        date__range=[start_of_year, end_of_year]
    ).aggregate(total=Sum('daily_sales'))['total'] or 0

class Staff(models.Model):
    user_id = models.OneToOneField(User, on_delete=models.CASCADE, default=None, null=True, blank=True)
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    phone = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.full_name} ({self.position})"
    
class Admin(models.Model):
    user_id = models.OneToOneField(User, on_delete=models.CASCADE, default=None, null=True, blank=True)
    phone = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.full_name} (Admin)"
    
class Driver(models.Model):
    user_id = models.OneToOneField(User, on_delete=models.CASCADE, default=None, null=True, blank=True)
    phone = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.full_name} (Admin)"