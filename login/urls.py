from django.urls import path
from . import views

urlpatterns = [
path('', views.login_user, name='login'),  # Homepage
path('register/', views.register_user, name='register'),
]