from django.shortcuts import render, redirect
from django.utils import timezone
from django.db.models import Sum
from django.contrib.auth.decorators import user_passes_test

from .models import (
    Product,
    Customer,
    Order,
    OrderItem,
    Driver,
)

# ---------------------------
# ROLE CHECKS
# ---------------------------
def if_staff(user):
    return user.groups.filter(name__in=['staff', 'admin']).exists()

def if_admin(user):
    return user.groups.filter(name='admin').exists()

def is_customer_or_staff(user):
    return user.groups.filter(name__in=['customer', 'staff']).exists()


# ---------------------------
# VIEWS
# ---------------------------
@user_passes_test(if_staff, login_url='/')
def cashier(request):
    products = Product.objects.all()
    return render(request, 'pos/cashier.html', {'products': products})


@user_passes_test(if_staff, login_url='/')
def customers(request):
    customers = Customer.objects.all()
    return render(request, 'pos/customers.html', {'customers': customers})


@user_passes_test(if_staff, login_url='/')
def deliveries(request):
    """
    Deliveries are now part of the Order model.
    Show orders with delivery statuses.
    """
    orders = Order.objects.select_related('customer').order_by('-delivery_scheduled_at')
    drivers = Driver.objects.all()   # You said keep driver info
    return render(request, 'pos/deliveries.html', {
        'orders': orders,
        'drivers': drivers
    })


@user_passes_test(if_admin, login_url='/')
def reports(request):
    """Basic sales report since Inventory + Payment models no longer exist."""
    sales_today = Order.objects.filter(
        created_at__date=timezone.now().date()
    ).aggregate(total=Sum('total'))

    return render(request, 'pos/reports.html', {
        'sales_today': sales_today,
        'low_stock': None  # removed Inventory
    })


def orders_table(request):
    """Show all orders with delivery info in a single table."""
    orders = Order.objects.select_related('customer').order_by('-created_at')
    return render(request, 'pos/orders_table.html', {'orders': orders})
