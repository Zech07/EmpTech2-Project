from django.shortcuts import render, redirect
from pos.models import Customer
from django.contrib.auth.decorators import user_passes_test
from .forms import OrderForm
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
# Create your views here.

def if_customer(user):
    return user.groups.filter(name='customer').exists()


@user_passes_test( if_customer, login_url='/')
def customer(request):

    customers = Customer.objects.all()
    return render(request, 'customer/customer.html', {'customers': customers})


def OrderForm(request):
    """Handle form submission"""
    if request.method == 'POST':
        channel_layer = get_channel_layer()
        form = OrderForm(request.POST)
        if form.is_valid():
            form.save()  # or assign to `status` if needed
            async_to_sync(channel_layer.group_send)(
                "staff_group",  # Only notify admin team
            {
            "type": "send_notification",
            "title": "Delivery Update",
            "message": "Order has been delivered!",
            }
    )
            return redirect('tracking_success')  
    else:
        form = OrderForm()

    return render(request, 'tracking_form.html', {'form': form})