# notifications/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.apps import apps
from .models import Notification
from .tasks import send_delivery_notification

def connect_delivery_signals():
    Delivery = apps.get_model("deliveries", "Delivery")  # resolves at runtime
    @receiver(post_save, sender=Delivery)
    def notify_delivery_update(sender, instance, created, **kwargs):
        # only on updates
        if not created:
            user = instance.customer
            message = f"Your order #{instance.id} is now {instance.status}."
            Notification.objects.create(user=user, message=message)
            # send async email / SMS
            send_delivery_notification.delay(user.id, message)

# Call this at import in apps.ready() (see NotificationsConfig.ready)
connect_delivery_signals()
