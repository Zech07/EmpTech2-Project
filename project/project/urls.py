from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse

def home(request):
    return HttpResponse("Welcome to Water Delivery Management System!")

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),  # Homepage
    path('notifications/', include('notifications.urls')),  # Notifications app
    path('deliveries/', include('deliveries.urls')),        # Deliveries app
    path('pos/', include('POS.urls')),                      # POS app
]
