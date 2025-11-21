from django.urls import path
from . import views
app_name = 'login'
urlpatterns = [
path('', views.login_user, name='login'),  # Homepage
path('login/', views.login_user, name='login_alt'),
path('register/', views.register_user, name='register'),
path('logout/', views.logout_user, name='logout'),  # Make sure this exists
]