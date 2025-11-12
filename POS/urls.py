from django.urls import path
from . import views

app_name = 'pos'

urlpatterns = [
    path('cashier/', views.cashier, name='cashier'),
    path('customers/', views.customers, name='customers'),
    path('inventory/', views.inventory, name='inventory'),
    path('deliveries/', views.deliveries, name='deliveries'),
    path('payments/', views.payments, name='payments'),
    path('reports/', views.reports, name='reports'),
]
