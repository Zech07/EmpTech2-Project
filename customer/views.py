# customers/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import user_passes_test
from pos.models import Customer, Order, OrderItem, Product
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


# Check if the user is in the 'customer' group
def if_customer(user):
    return user.groups.filter(name='customer').exists()

def customer(request):
    """
    Display the logged-in customer's profile along with their CustomerProfile details.
    """
    # Get the Customer instance for the logged-in user
    customer_instance = Customer.objects.get(user=request.user)

    context = {
        'customer': customer_instance
    }
    return render(request, 'customer.html', context)



# Check if user is a customer
def if_customer(user):
    return user.groups.filter(name='customer').exists()

@user_passes_test(if_customer, login_url='/')
def order(request):
    """Create a new order for the logged-in customer with selected products"""
    customer_instance = Customer.objects.get(user=request.user)
    products = Product.objects.all()  # For product selection

    if request.method == 'POST':
        # Example: expecting POST data like {'product_id': 1, 'quantity': 2}
        product_id = request.POST.get('product_id')
        quantity = int(request.POST.get('quantity', 1))

        product = Product.objects.get(id=product_id)

        # Create Order
        order_instance = Order.objects.create(customer=customer_instance, total=0)

        # Create OrderItem
        order_item = OrderItem.objects.create(
            order=order_instance,
            product=product,
            quantity=quantity,
            unit_price=product.price  # assuming Product has a price field
        )

        # Update total
        order_instance.total = order_item.line_total()
        order_instance.save()

        # Optional: notify staff/admin
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "staff_admin_group",
            {
                "type": "send_notification",
                "title": "New Order",
                "message": f"Customer {request.user.username} placed a new order!",
            }
        )

        return redirect('customer:profile')

    return render(request, 'customer/order.html', {'products': products})
