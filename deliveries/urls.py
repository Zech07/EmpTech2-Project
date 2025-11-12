from django.urls import path
from . import views

urlpatterns = [
    path('delivery_list/', views.delivery_list, name='delivery_list'),
    path('form/', views.tracking_form, name='tracking_form'),
    path('form_success/', views.tracking_success, name='tracking_success'),

]
