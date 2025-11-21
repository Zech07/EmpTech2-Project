from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse

def home(request):
    return HttpResponse("Welcome to Water Delivery Management System!")

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('login.urls')),                      # Login app       # Deliveries app
    path('pos/', include('pos.urls')),                      # POS app              # customer app
]
