
from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, Customer, Inventory, Order, OrderItem, Payment, Driver, Delivery
from django.utils import timezone
from django.db.models import Sum, F
from django.contrib.auth.decorators import user_passes_test

def if_staff(user):
    return user.groups.filter(name='staff').exists()


def if_customer(user):
    return user.groups.filter(name='customer').exists()

def if_admin(user):
    return user.groups.filter(name='admin').exists()

@user_passes_test(if_staff, login_url='/')
def cashier(request):
    products = Product.objects.all()
    return render(request, 'pos/cashier.html', {'products': products})

@user_passes_test(if_customer, login_url='/')
def customers(request):
    customers = Customer.objects.all()
    return render(request, 'pos/customers.html', {'customers': customers})

@user_passes_test(if_staff, login_url='/')
def inventory(request):
    items = Inventory.objects.select_related('product').all()
    return render(request, 'pos/inventory.html', {'items': items})

@user_passes_test(if_staff, login_url='/')
def deliveries(request):
    deliveries = Delivery.objects.select_related('order','driver').all()
    drivers = Driver.objects.all()
    return render(request, 'pos/deliveries.html', {'deliveries': deliveries, 'drivers': drivers})

@user_passes_test(if_staff , login_url='/')
def payments(request):
    payments = Payment.objects.select_related('order').all()
    return render(request, 'pos/payments.html', {'payments': payments})

@user_passes_test(if_staff , login_url='/') 
def reports(request):
    sales_today = Order.objects.filter(created_at__date=timezone.now().date()).aggregate(total=Sum('total'))
    low_stock = Inventory.objects.filter(quantity__lte=F('low_threshold')).select_related('product')
    return render(request, 'pos/reports.html', {'sales_today': sales_today, 'low_stock': low_stock})

