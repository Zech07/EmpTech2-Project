from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Q, Sum
from django.http import JsonResponse
from django.utils import timezone
from .models import Order, Customer, Sales, Staff
from .forms import ChangeStatusForm, UpdateCustomerForm
from django.contrib.auth.models import User
import logging

logger = logging.getLogger(__name__)

# Helper functions for permission checks
def is_admin(user):
    """Check if user is admin staff"""
    try:
        return Staff.objects.get(user=user).is_admin()
    except Staff.DoesNotExist:
        return False

def is_driver(user):
    """Check if user is driver staff"""
    try:
        return Staff.objects.get(user=user).is_driver()
    except Staff.DoesNotExist:
        return False

def is_customer(user):
    """Check if user has customer profile"""
    return hasattr(user, 'customer')

def is_staff(user):
    """Check if user is any type of staff"""
    return hasattr(user, 'staff')

def can_edit_orders(user):
    """Check if user can edit orders (staff and admin)"""
    return is_staff(user) or is_admin(user)

# Order Management Views
@login_required
def order_list(request):
    """View all orders with ability to change status and paid status"""
    try:
        # Start with base queryset
        orders = Order.objects.all().select_related('customer', 'assigned_driver__user')
        
        # Initialize filter variables
        search_query = ''
        jug_status_filter = ''
        paid_status_filter = ''
        
        # Handle search and filter parameters
        if request.method == 'GET':
            search_query = request.GET.get('search', '').strip()
            jug_status_filter = request.GET.get('jug_status', '')
            paid_status_filter = request.GET.get('paid_status', '')
            
            # Apply search filter
            if search_query:
                orders = orders.filter(
                    Q(customer__user__first_name__icontains=search_query) |
                    Q(customer__user__last_name__icontains=search_query) |
                    Q(customer__phone__icontains=search_query) |
                    Q(customer__jug_tag__icontains=search_query) |
                    Q(id__icontains=search_query)
                )
            
            # Apply jug_status filter
            if jug_status_filter:
                orders = orders.filter(jug_status=jug_status_filter)
            
            # Apply paid_status filter
            if paid_status_filter:
                if paid_status_filter.lower() == 'paid':
                    orders = orders.filter(paid_status=True)
                elif paid_status_filter.lower() == 'unpaid':
                    orders = orders.filter(paid_status=False)
        
        # Filter based on user role (after search/filters)
        if is_driver(request.user):
            # Driver can see all orders (since there's only one driver)
            pass  # No filtering needed - driver sees all orders
        elif is_customer(request.user):
            # Customers can only see their own orders
            try:
                customer = Customer.objects.get(user=request.user)
                orders = orders.filter(customer=customer)
            except Customer.DoesNotExist:
                orders = Order.objects.none()
        
        # Handle status updates via AJAX
        if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return handle_ajax_order_update(request)
        
        context = {
            'orders': orders,
            'is_admin': is_admin(request.user),
            'is_staff': is_staff(request.user),
            'is_driver': is_driver(request.user),
            'is_customer': is_customer(request.user),
            # Search and filter context
            'search_query': search_query,
            'jug_status_filter': jug_status_filter,
            'paid_status_filter': paid_status_filter,
            'jug_status_choices': Order.JUG_STATUS_CHOICES,
            'paid_status_choices': [
                ('', 'All Payments'),
                ('paid', 'Paid'),
                ('unpaid', 'Unpaid')
            ],
        }
        return render(request, 'orders/order_list.html', context)
    
    except Exception as e:
        logger.error(f"Error in order_list view: {e}")
        messages.error(request, 'An error occurred while loading orders.')
        return redirect('home')

def handle_ajax_order_update(request):
    """Handle AJAX order updates separately for cleaner code"""
    order_id = request.POST.get('order_id')
    field = request.POST.get('field')
    value = request.POST.get('value')
    
    try:
        order = Order.objects.get(id=order_id)
        
        # Permission checks - Driver, Staff and Admin can update both fields
        if field == 'jug_status' and not can_edit_orders(request.user):
            return JsonResponse({'success': False, 'error': 'Permission denied'})
        
        if field == 'paid_status' and not can_edit_orders(request.user):
            return JsonResponse({'success': False, 'error': 'Permission denied'})
        
        # Update field
        if field == 'jug_status':
            order.jug_status = value
        elif field == 'paid_status':
            order.paid_status = (value.lower() == 'true')
        
        order.save()
        return JsonResponse({'success': True})
        
    except Order.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Order not found'})
    except Exception as e:
        logger.error(f"Error updating order {order_id}: {e}")
        return JsonResponse({'success': False, 'error': 'Server error'})

@login_required
@user_passes_test(lambda u: is_admin(u) or is_staff(u))
def create_order(request):
    """Staff and Admin can manually create new orders"""
    if request.method == 'POST':
        customer_id = request.POST.get('customer')
        amount = request.POST.get('amount')
        jug_status = request.POST.get('jug_status', 'picked_up')
        
        try:
            customer = Customer.objects.get(id=customer_id)
            order = Order.objects.create(
                customer=customer,
                amount=amount,
                jug_status=jug_status,
                order_date=timezone.now()
            )
            messages.success(request, f'Order #{order.id} created successfully!')
            return redirect('order_list')
        except Customer.DoesNotExist:
            messages.error(request, 'Customer not found!')
        except Exception as e:
            messages.error(request, f'Error creating order: {str(e)}')
    
    customers = Customer.objects.all()
    context = {
        'customers': customers,
        'jug_status_choices': Order.JUG_STATUS_CHOICES,
    }
    return render(request, 'orders/create_order.html', context)

@login_required
@user_passes_test(lambda u: is_driver(u) or is_admin(u) or is_staff(u))
def update_order_status(request, order_id):
    """Driver, Staff and Admin can update jug status and payment status"""
    order = get_object_or_404(Order, id=order_id)
    
    if request.method == 'POST':
        form = ChangeStatusForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            messages.success(request, f'Order #{order.id} status updated successfully!')
            return redirect('order_list')
    else:
        form = ChangeStatusForm(instance=order)
    
    context = {
        'form': form,
        'order': order,
        'title': 'Update Order Status'
    }
    return render(request, 'orders/update_status.html', context)

@login_required
@user_passes_test(is_customer)
def customer_profile(request):
    """Customers can update their own profile"""
    try:
        customer = Customer.objects.get(user=request.user)
    except Customer.DoesNotExist:
        messages.error(request, 'Customer profile not found.')
        return redirect('home')
    
    if request.method == 'POST':
        form = UpdateCustomerForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('customer_profile')
    else:
        form = UpdateCustomerForm(instance=customer)
    
    # Get customer's orders
    orders = Order.objects.filter(customer=customer).order_by('-order_date')
    
    context = {
        'form': form,
        'customer': customer,
        'orders': orders,
        'title': 'My Profile'
    }
    return render(request, 'customers/profile.html', context)

@login_required
@user_passes_test(lambda u: is_admin(u) or is_staff(u))
def sales_dashboard(request):
    """Staff and Admin sales dashboard with date filtering"""
    # Get filter parameters
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    period = request.GET.get('period', '')  # quick period filter
    
    # Base sales data
    sales_data = Sales.objects.all().order_by('-date')
    
    # Apply date filters
    if date_from:
        sales_data = sales_data.filter(date__gte=date_from)
    if date_to:
        sales_data = sales_data.filter(date__lte=date_to)
    
    # Apply quick period filters
    if period == 'today':
        today = timezone.now().date()
        sales_data = sales_data.filter(date=today)
    elif period == 'week':
        week_ago = timezone.now().date() - timezone.timedelta(days=7)
        sales_data = sales_data.filter(date__gte=week_ago)
    elif period == 'month':
        month_ago = timezone.now().date() - timezone.timedelta(days=30)
        sales_data = sales_data.filter(date__gte=month_ago)
    
    # Calculate totals based on filtered data
    total_daily_sales = sum(sale.daily_sales for sale in sales_data) if sales_data else 0
    
    # For weekly and monthly, calculate from orders for accuracy
    if sales_data:
        # Weekly sales (last 7 days)
        week_start = timezone.now().date() - timezone.timedelta(days=7)
        weekly_orders = Order.objects.filter(
            paid_status=True,
            order_date__date__gte=week_start
        )
        total_weekly_sales = weekly_orders.aggregate(total=Sum('amount'))['total'] or 0
        
        # Monthly sales (last 30 days)
        month_start = timezone.now().date() - timezone.timedelta(days=30)
        monthly_orders = Order.objects.filter(
            paid_status=True,
            order_date__date__gte=month_start
        )
        total_monthly_sales = monthly_orders.aggregate(total=Sum('amount'))['total'] or 0
    else:
        total_weekly_sales = 0
        total_monthly_sales = 0
    
    # Get recent paid orders for the table
    recent_orders = Order.objects.filter(paid_status=True).select_related('customer').order_by('-order_date')[:10]
    
    # Get order statistics
    total_orders = Order.objects.count()
    paid_orders_count = Order.objects.filter(paid_status=True).count()
    unpaid_orders_count = Order.objects.filter(paid_status=False).count()
    
    context = {
        'sales_data': sales_data,
        'recent_orders': recent_orders,
        'total_daily_sales': total_daily_sales,
        'total_weekly_sales': total_weekly_sales,
        'total_monthly_sales': total_monthly_sales,
        'total_orders': total_orders,
        'paid_orders_count': paid_orders_count,
        'unpaid_orders_count': unpaid_orders_count,
        # Filter context
        'date_from': date_from,
        'date_to': date_to,
        'period': period,
        'title': 'Sales Dashboard'
    }
    return render(request, 'admin/sales_dashboard.html', context)

@login_required
@user_passes_test(lambda u: is_admin(u) or is_staff(u) or is_driver(u))
def update_paid_status(request, order_id):
    """Admin, Staff, and Driver can update paid status"""
    order = get_object_or_404(Order, id=order_id)
    
    if request.method == 'POST':
        paid_status = request.POST.get('paid_status') == 'true'
        order.paid_status = paid_status
        order.save()
        
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'paid_status': order.paid_status})
        
        messages.success(request, f'Order #{order.id} payment status updated!')
        return redirect('order_list')
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})

# API endpoints for AJAX updates
@login_required
def update_order_field(request):
    """Handle AJAX updates for order fields"""
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        order_id = request.POST.get('order_id')
        field = request.POST.get('field')
        value = request.POST.get('value')
        
        try:
            order = Order.objects.get(id=order_id)
            
            # Permission checks - Driver, Staff and Admin can update both fields
            if field == 'jug_status' and not can_edit_orders(request.user):
                return JsonResponse({'success': False, 'error': 'Permission denied'})
            
            if field == 'paid_status' and not can_edit_orders(request.user):
                return JsonResponse({'success': False, 'error': 'Permission denied'})
            
            # Update field
            if field == 'jug_status':
                order.jug_status = value
            elif field == 'paid_status':
                order.paid_status = (value.lower() == 'true')
            
            order.save()
            return JsonResponse({'success': True})
            
        except Order.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Order not found'})
        except Exception as e:
            logger.error(f"Error updating order {order_id}: {e}")
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})

@login_required
def clear_filters(request):
    """Clear all filters and return to default order list"""
    return redirect('order_list')