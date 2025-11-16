from django.http import HttpResponse
from django.shortcuts import render, redirect
from .forms import TrackForm
from .models import Delivery
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

def index(request):
    return HttpResponse("Welcome to the Deliveries Home Page!")

from django.shortcuts import render
from .models import Delivery


@login_required
def delivery_list(request):
    all_deliveries = Delivery.objects.all().order_by('-date')

    unique_customers = {}
    for d in all_deliveries:
        if d.customer not in unique_customers:
            unique_customers[d.customer] = d  # keep the latest one only

    # Now separate by status
    delivered = [d for d in unique_customers.values() if d.status.lower() == "delivered"]
    transporting = [d for d in unique_customers.values() if d.status.lower() == "transporting"]
    picked_up = [d for d in unique_customers.values() if d.status.lower() == "picked_up"]

    state = {
        "delivered": delivered,
        "transporting": transporting,
        "picked_up": picked_up,
    }
    
    return render(request, "delivery_list.html", state)

def tracking_form(request):
    """Handle form submission"""
    if request.method == 'POST':
        channel_layer = get_channel_layer()
        form = TrackForm(request.POST)
        if form.is_valid():
            form.save()  # or assign to `status` if needed
            async_to_sync(channel_layer.group_send)(
                "admin_group",  # Only notify admin team
            {
            "type": "send_notification",
            "title": "Delivery Update",
            "message": "Order has been delivered!",
            }
    )
            return redirect('tracking_success')  
    else:
        form = TrackForm()

    return render(request, 'tracking_form.html', {'form': form})

def tracking_success(request):
    return render(request, 'tracking_success.html')

