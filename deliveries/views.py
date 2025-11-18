from django.http import HttpResponse
from django.shortcuts import render, redirect
from .forms import TrackForm
from .models import Delivery
from django.contrib.auth.models import User
from django.contrib.auth.decorators import user_passes_test
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from django.shortcuts import render
from .models import Delivery


def if_driver(user):
    return user.groups.filter(name='driver').exists()

@user_passes_test(if_driver , login_url='/')
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

from django.shortcuts import render, redirect
from .forms import TrackForm
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

def tracking_form(request):
    """Handle form submission and send real-time notifications."""
    form = TrackForm(request.POST or None)  # Handles both GET and POST

    if request.method == 'POST' and form.is_valid():
        delivery = form.save()  # Save and get the instance
        channel_layer = get_channel_layer()

        # Count deliveries by status
        delivered_count = Delivery.objects.filter(status='delivered').count()
        transporting_count = Delivery.objects.filter(status='transporting').count()
        picked_up_count = Delivery.objects.filter(status='picked_up').count()

        # Notify POS staff/admin group
        async_to_sync(channel_layer.group_send)(
            "staff_admin_group",
            {
                "type": "send_notification",
                "title": "Delivery Update",
                "message": f"Delivery #{delivery.id} is now {delivery.status}",
                "delivered_count": delivered_count,
                "transporting_count": transporting_count,
                "picked_up_count": picked_up_count
            }
        )

        # Notify the specific customer
        customer_user_id = delivery.customer.user.id
        async_to_sync(channel_layer.group_send)(
            f"customer_{customer_user_id}",
            {
                "type": "send_notification",
                "title": "Your Order Status",
                "message": f"Your delivery #{delivery.id} is now {delivery.status}",
            }
        )

        return redirect('tracking_success')

    return render(request, 'tracking_form.html', {'form': form})



def tracking_success(request):
    return render(request, 'tracking_success.html')

