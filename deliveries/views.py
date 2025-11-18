# deliveries/views.py
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import user_passes_test
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Delivery
from .forms import DeliveryStatusForm

def if_staff(user):
    return user.groups.filter(name__in=['staff', 'admin']).exists()

from django.shortcuts import render
from django.contrib.auth.decorators import user_passes_test
from .models import Delivery

def if_driver(user):
    return user.groups.filter(name='driver').exists()

@user_passes_test(if_driver, login_url='/')
def delivery_list(request):
    """
    Show the latest delivery per customer, grouped by status.
    """

    # Get all deliveries (most recent first)
    all_deliveries = Delivery.objects.select_related('customer').order_by('-date')

    # Keep ONLY the latest delivery per customer
    latest_by_customer = {}
    for delivery in all_deliveries:
        if delivery.customer_id not in latest_by_customer:
            latest_by_customer[delivery.customer_id] = delivery

    # Group deliveries by status
    grouped = {
        'delivered': [],
        'transporting': [],
        'picked_up': []
    }
    for delivery in latest_by_customer.values():
        status = delivery.status.lower()
        if status in grouped:
            grouped[status].append(delivery)

    return render(request, "delivery_list.html", grouped)


@user_passes_test(if_driver, login_url='/')
def update_delivery(request, order_id):
    """Update the latest delivery linked to an order"""
    order = get_object_or_404(Order, id=order_id)

    # Get or create a delivery for this order
    delivery, created = Delivery.objects.get_or_create(
        order=order,
        defaults={
            'customer': order.customer,
            'customer_name': order.customer.name if order.customer else "Walk-in",
            'address': order.customer.address if order.customer else "",
            'contact_number': order.customer.phone if order.customer else "",
            'amount': order.total,
            'status': 'transporting',
        }
    )

    form = DeliveryStatusForm(request.POST or None, instance=delivery)

    if request.method == 'POST' and form.is_valid():
        form.save()

        # Optional: also update order.delivery_status
        order.delivery_status = delivery.status
        order.save()

        # WebSocket notification
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "staff_admin_group",
            {
                "type": "delivery_update",
                "order_id": order.id,
                "delivery_status": delivery.status,
            }
        )

        return redirect('orders_table')  # or wherever the table is

    return render(request, 'update_delivery.html', {'form': form, 'order': order})
