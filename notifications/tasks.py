from celery import shared_task
from django.core.mail import send_mail
from django.contrib.auth.models import User

@shared_task
def send_delivery_notification(user_id, message):
    user = User.objects.get(id=user_id)
    send_mail(
        subject="Water Delivery Update",
        message=message,
        from_email="yourwaterstation@example.com",
        recipient_list=[user.email],
    )
    return "Notification sent"
