"""
from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, Customer, Inventory, Order, OrderItem, Delivery, Payment, Driver
from django.utils import timezone
from django.db.models import Sum


def cashier(request):
    products = Product.objects.all()
    return render(request, 'pos/cashier.html', {'products': products})


def customers(request):
    customers = Customer.objects.all()
    return render(request, 'pos/customers.html', {'customers': customers})


def inventory(request):
    items = Inventory.objects.select_related('product').all()
    return render(request, 'pos/inventory.html', {'items': items})


def deliveries(request):
    deliveries = Delivery.objects.select_related('order', 'driver').all()
    drivers = Driver.objects.all()
    return render(request, 'pos/deliveries.html', {'deliveries': deliveries, 'drivers': drivers})


def payments(request):
    payments = Payment.objects.select_related('order').all()
    return render(request, 'pos/payments.html', {'payments': payments})


def reports(request):
    sales_today = Order.objects.filter(created_at__date=timezone.now().date()).aggregate(total=Sum('total'))
    low_stock = Inventory.objects.filter(quantity__lte=models.F('low_threshold')).select_related('product')
    return render(request, 'pos/reports.html', {'sales_today': sales_today, 'low_stock': low_stock})
"""