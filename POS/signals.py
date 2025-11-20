from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.db.models import Sum
from .models import Order, Sales

@receiver(post_save, sender=Order)
def update_sales_on_order_save(sender, instance, created, **kwargs):
    """
    Update sales records when an order's paid_status changes
    """
    if instance.paid_status:
        sales_date = instance.order_date.date()
        
        try:
            # Get or create sales record for the date
            sales_obj, created = Sales.objects.get_or_create(date=sales_date)
            
            # Calculate daily sales by summing all paid orders for that date
            daily_total = Order.objects.filter(
                paid_status=True,
                order_date__date=sales_date
            ).aggregate(total=Sum('amount'))['total'] or 0
            
            # Only update if the value has changed
            if sales_obj.daily_sales != daily_total:
                sales_obj.daily_sales = daily_total
                sales_obj.save()
                
        except Exception as e:
            # Log the error in production
            print(f"Error updating sales for date {sales_date}: {e}")

@receiver(pre_save, sender=Order)
def update_customer_amount_due(sender, instance, **kwargs):
    """
    Update customer's amount_due when order paid_status changes
    """
    if instance.pk:  # Only for existing orders
        try:
            old_order = Order.objects.get(pk=instance.pk)
            if old_order.paid_status != instance.paid_status:
                customer = instance.customer
                if instance.paid_status:
                    # Order was just paid, reduce amount_due
                    customer.amount_due -= instance.amount
                else:
                    # Order was unpaid, increase amount_due
                    customer.amount_due += instance.amount
                
                # Ensure amount_due doesn't go negative
                if customer.amount_due < 0:
                    customer.amount_due = 0
                    
                customer.save()
        except Order.DoesNotExist:
            pass  # New order, no need to update

@receiver(post_save, sender=Order)
def handle_new_order_amount_due(sender, instance, created, **kwargs):
    """
    Handle amount_due for newly created orders
    """
    if created and not instance.paid_status:
        # New unpaid order, add to customer's amount_due
        customer = instance.customer
        customer.amount_due += instance.amount
        customer.save()

from django.db.models.signals import post_delete

@receiver(post_delete, sender=Order)
def update_sales_on_order_delete(sender, instance, **kwargs):
    """
    Update sales when an order is deleted
    """
    if instance.paid_status:
        sales_date = instance.order_date.date()
        try:
            sales_obj = Sales.objects.get(date=sales_date)
            # Recalculate without the deleted order
            daily_total = Order.objects.filter(
                paid_status=True,
                order_date__date=sales_date
            ).aggregate(total=Sum('amount'))['total'] or 0
            
            sales_obj.daily_sales = daily_total
            sales_obj.save()
        except Sales.DoesNotExist:
            pass