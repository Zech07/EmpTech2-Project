from django.urls import path
from . import views

app_name = 'pos'

urlpatterns = [
    # Order management - simplified without redirects
    path('', views.order_list, name='order_list'),
    path('orders/', views.order_list, name='order_list_alt'),  # ADD THIS LINE
    path('create/', views.create_order, name='create_order'),
    path('<int:order_id>/update-status/', views.update_order_status, name='update_order_status'),
    path('<int:order_id>/update-paid/', views.update_paid_status, name='update_paid_status'),
    path('clear-filters/', views.clear_filters, name='clear_filters'),
    # In urls.py - add this line
    path('update-field/', views.handle_ajax_order_update, name='update_order_field'),
    
    # Customer profile
    path('profile/', views.customer_profile, name='customer_profile'),
    
    # Staff and Admin sales dashboard
    path('dashboard/sales/', views.sales_dashboard, name='sales_dashboard'),
]