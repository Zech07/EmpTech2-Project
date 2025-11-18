from django.urls import path
from . import views
app_name = 'deliveries'

urlpatterns = [
    path('delivery_list/', views.delivery_list, name='delivery_list'),
    path('update/', views.update_delivery, name='update_delivery'),
]
