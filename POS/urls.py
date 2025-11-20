from django.urls import path
from . import views

app_name = 'pos'

urlpatterns = [
    path('cashier/', views.cashier, name='cashier'),
    path('customers/', views.customers, name='customers'),
    path('deliveries/', views.deliveries, name='deliveries'),
    path('reports/', views.reports, name='reports'),
    path('order_table/', views.orders_table, name='order_table'),
]
