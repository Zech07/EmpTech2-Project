from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Q, Sum
from django.http import JsonResponse
from django.utils import timezone
from django.contrib.auth.models import User
import logging
from decimal import Decimal, InvalidOperation

logger = logging.getLogger(__name__)

# Import models at FUNCTION LEVEL to avoid circular imports
def get_models():
    """Lazy import models to avoid circular imports"""
    from .models import Order, Customer, Sales, Staff
    return Order, Customer, Sales, Staff

def get_forms():
    """Lazy import forms to avoid circular imports"""
    from .forms import ChangeStatusForm, UpdateCustomerForm
    return ChangeStatusForm, UpdateCustomerForm

# Helper functions for permission checks
def is_admin(user):
    """Check if user is admin staff"""
    Order, Customer, Sales, Staff = get_models()
    try:
        staff = Staff.objects.get(user=user)
        return staff.position == 'admin'
    except Staff.DoesNotExist:
        return False

def is_driver(user):
    """Check if user is driver staff"""
    Order, Customer, Sales, Staff = get_models()
    try:
        staff = Staff.objects.get(user=user)
        return staff.position == 'driver'
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

def can_update_jug_status(user):
    """Check if user can update jug status (driver, staff, admin)"""
    return is_driver(user) or is_staff(user) or is_admin(user)

def can_update_payment_status(user):
    """Check if user can update payment status (staff, admin)"""
    return is_staff(user) or is_admin(user)

# Order Management Views
@login_required
def order_list(request):
    """View all orders with ability to change status and paid status"""
    Order, Customer, Sales, Staff = get_models()
    
    try:
        # Handle AJAX requests FIRST
        if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return handle_ajax_order_update(request)
        
        # FIXED: Add proper select_related to avoid template errors
        orders = Order.objects.all().select_related(
            'customer', 
            'customer__user',  # CRITICAL FIX
            'assigned_driver', 
            'assigned_driver__user'
        ).order_by('-order_date')  # FIXED: Add ordering
        
        # Initialize filter variables
        search_query = ''
        jug_status_filter = ''
        paid_status_filter = ''
        
        # Handle search and filter parameters (GET requests only)
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
        user = request.user
        if is_driver(user):
            # Driver can see all orders
            pass
        elif is_customer(user):
            # Customers can only see their own orders
            try:
                customer = Customer.objects.get(user=user)
                orders = orders.filter(customer=customer)
            except Customer.DoesNotExist:
                orders = Order.objects.none()
                messages.error(request, 'Customer profile not found.')
        
        # DEBUG: Log order count
        logger.info(f"Order list loaded: {orders.count()} orders for user {user.username}")
        
        context = {
            'orders': orders,
            'is_admin': is_admin(user),
            'is_staff': is_staff(user),
            'is_driver': is_driver(user),
            'is_customer': is_customer(user),
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
        logger.error(f"Error in order_list view: {str(e)}", exc_info=True)
        messages.error(request, 'An error occurred while loading orders.')
        context = {
            'orders': Order.objects.none(),
            'is_admin': is_admin(request.user),
            'is_staff': is_staff(request.user),
            'is_driver': is_driver(request.user),
            'is_customer': is_customer(request.user),
            'search_query': '',
            'jug_status_filter': '',
            'paid_status_filter': '',
            'jug_status_choices': Order.JUG_STATUS_CHOICES,
            'paid_status_choices': [
                ('', 'All Payments'),
                ('paid', 'Paid'),
                ('unpaid', 'Unpaid')
            ],
        }
        return render(request, 'orders/order_list.html', context)

def handle_ajax_order_update(request):
    """Handle AJAX order updates separately for cleaner code"""
    Order, Customer, Sales, Staff = get_models()
    
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Method not allowed'})
    
    order_id = request.POST.get('order_id')
    field = request.POST.get('field')
    value = request.POST.get('value')
    
    if not all([order_id, field, value]):
        return JsonResponse({'success': False, 'error': 'Missing required fields'})
    
    try:
        order = Order.objects.get(id=order_id)
        user = request.user
        
        # Improved permission checks with specific functions
        if field == 'jug_status' and not can_update_jug_status(user):
            return JsonResponse({'success': False, 'error': 'Permission denied'})
        
        if field == 'paid_status' and not can_update_payment_status(user):
            return JsonResponse({'success': False, 'error': 'Permission denied'})
        
        # Update field
        if field == 'jug_status':
            order.jug_status = value
            action = f"Jug status updated to {value}"
        elif field == 'paid_status':
            order.paid_status = (value.lower() == 'true')
            action = "Payment status updated"
        else:
            return JsonResponse({'success': False, 'error': 'Invalid field'})
        
        order.save()
        logger.info(f"Order {order_id} {action} by user {user.username}")
        return JsonResponse({'success': True})
        
    except Order.DoesNotExist:
        logger.warning(f"Order {order_id} not found for update by user {request.user.username}")
        return JsonResponse({'success': False, 'error': 'Order not found'})
    except Exception as e:
        logger.error(f"Error updating order {order_id}: {str(e)}")
        return JsonResponse({'success': False, 'error': 'Server error'})

@login_required
@user_passes_test(lambda u: is_admin(u) or is_staff(u))
def create_order(request):
    """Staff and Admin can manually create new orders"""
    Order, Customer, Sales, Staff = get_models()
    ChangeStatusForm, UpdateCustomerForm = get_forms()
    
    customers = Customer.objects.all()
    
    if request.method == 'POST':
        customer_id = request.POST.get('customer')
        amount = request.POST.get('amount')
        jug_status = request.POST.get('jug_status', 'picked_up')
        
        # Enhanced validation
        errors = []
        
        if not customer_id:
            errors.append('Please select a customer.')
        
        try:
            customer = Customer.objects.get(id=customer_id)
        except Customer.DoesNotExist:
            errors.append('Customer not found!')
        
        # Amount validation
        try:
            amount = Decimal(str(amount).strip())
            if amount <= Decimal('0'):
                errors.append('Amount must be greater than 0!')
        except (ValueError, TypeError, InvalidOperation):
            errors.append('Invalid amount format! Please enter a valid number.')
        
        if errors:
            for error in errors:
                messages.error(request, error)
        else:
            try:
                # Create order - FIXED: Added more fields for completeness
                order = Order.objects.create(
                    customer=customer,
                    amount=amount,
                    jug_status=jug_status,
                    order_date=timezone.now(),
                    # Add default values for required fields if they exist in your model
                    paid_status=False  # Default to unpaid
                )
                
                logger.info(f"Order #{order.id} created for customer {customer.id} by user {request.user.username}")
                messages.success(request, f'Order #{order.id} created successfully!')
                
                # FIXED: Add debug logging
                total_orders = Order.objects.count()
                logger.info(f"Total orders in system: {total_orders}")
                
                return redirect('pos:order_list')
                
            except Exception as e:
                logger.error(f"Error creating order: {str(e)}", exc_info=True)
                messages.error(request, f'Error creating order: {str(e)}')
    
    context = {
        'customers': customers,
        'jug_status_choices': Order.JUG_STATUS_CHOICES,
    }
    return render(request, 'orders/create_order.html', context)

@login_required
@user_passes_test(lambda u: is_driver(u) or is_admin(u) or is_staff(u))
def update_order_status(request, order_id):
    """Driver, Staff and Admin can update jug status and payment status"""
    Order, Customer, Sales, Staff = get_models()
    ChangeStatusForm, UpdateCustomerForm = get_forms()
    
    order = get_object_or_404(Order, id=order_id)
    
    if request.method == 'POST':
        form = ChangeStatusForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            logger.info(f"Order #{order.id} status updated via form by user {request.user.username}")
            messages.success(request, f'Order #{order.id} status updated successfully!')
            return redirect('pos:order_list')
        else:
            messages.error(request, 'Please correct the errors below.')
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
    Order, Customer, Sales, Staff = get_models()
    ChangeStatusForm, UpdateCustomerForm = get_forms()
    
    try:
        customer = Customer.objects.get(user=request.user)
    except Customer.DoesNotExist:
        messages.error(request, 'Customer profile not found.')
        return redirect('pos:order_list')
    
    if request.method == 'POST':
        form = UpdateCustomerForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('pos:customer_profile')
        else:
            messages.error(request, 'Please correct the errors below.')
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
    Order, Customer, Sales, Staff = get_models()
    
    try:
        # Get filter parameters
        date_from = request.GET.get('date_from', '')
        date_to = request.GET.get('date_to', '')
        period = request.GET.get('period', '')
        
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
        
        # Calculate totals safely
        total_daily_sales = Decimal('0')
        for sale in sales_data:
            if hasattr(sale.daily_sales, '__add__'):
                total_daily_sales += Decimal(str(sale.daily_sales))
        
        # For weekly and monthly, calculate from orders for accuracy
        week_start = timezone.now().date() - timezone.timedelta(days=7)
        month_start = timezone.now().date() - timezone.timedelta(days=30)
        
        weekly_orders = Order.objects.filter(
            paid_status=True,
            order_date__date__gte=week_start
        )
        total_weekly_sales = weekly_orders.aggregate(total=Sum('amount'))['total'] or Decimal('0')
        
        monthly_orders = Order.objects.filter(
            paid_status=True,
            order_date__date__gte=month_start
        )
        total_monthly_sales = monthly_orders.aggregate(total=Sum('amount'))['total'] or Decimal('0')
        
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
    
    except Exception as e:
        logger.error(f"Error in sales_dashboard view: {str(e)}")
        messages.error(request, 'An error occurred while loading the sales dashboard.')
        return redirect('pos:order_list')

@login_required
@user_passes_test(lambda u: is_admin(u) or is_staff(u) or is_driver(u))
def update_paid_status(request, order_id):
    """Admin, Staff, and Driver can update paid status"""
    Order, Customer, Sales, Staff = get_models()
    
    order = get_object_or_404(Order, id=order_id)
    
    if request.method == 'POST':
        try:
            paid_status = request.POST.get('paid_status') == 'true'
            order.paid_status = paid_status
            order.save()
            
            logger.info(f"Order #{order.id} payment status set to {paid_status} by user {request.user.username}")
            
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'paid_status': order.paid_status})
            
            messages.success(request, f'Order #{order.id} payment status updated!')
            return redirect('pos:order_list')
        
        except Exception as e:
            logger.error(f"Error updating paid status for order {order_id}: {str(e)}")
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': str(e)})
            messages.error(request, f'Error updating payment status: {str(e)}')
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})

@login_required
def clear_filters(request):
    """Clear all filters and return to default order list"""
    return redirect('pos:order_list')