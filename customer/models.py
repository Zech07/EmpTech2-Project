from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import models
from pos.models import Customer
# Create your models here.

@receiver(post_save, sender=Customer)
def create_customer_profile(sender, instance, created, **kwargs):
    if created:
        
        CustomerProfile.objects.create(user=instance)

class CustomerProfile(models.Model):
    user = models.OneToOneField(Customer, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    jug_id = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.user.username