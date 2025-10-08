from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='deliveries_index'),
    path('list/', views.list_deliveries, name='list_deliveries'),
]
