from django.urls import path
from . import views

app_name = 'pos'

urlpatterns = [
    # Order management
    path('', views.order_list, name='order_list'),
    path('orders/', views.order_list, name='order_list'),
    path('orders/create/', views.create_order, name='create_order'),
    path('orders/<int:order_id>/update-status/', views.update_order_status, name='update_order_status'),
    path('orders/<int:order_id>/update-paid/', views.update_paid_status, name='update_paid_status'),
    path('orders/update-field/', views.update_order_field, name='update_order_field'),
    path('orders/clear-filters/', views.clear_filters, name='clear_filters'),
    
    # Customer profile
    path('profile/', views.customer_profile, name='customer_profile'),
    
    # Staff and Admin sales dashboard
    path('dashboard/sales/', views.sales_dashboard, name='sales_dashboard'),
    
    # Home page
    path('home/', views.order_list, name='home'),
]