from django.urls import path
from . import views
app_name = 'customer'

urlpatterns = [
    path('profile/', views.customer, name='profile'),
    path('order/', views.order, name='order'),
]
