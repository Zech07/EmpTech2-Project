from django.db import models

class Role(models.TextChoices):
    CUSTOMER = "Customer", "Customer"
    DELIVERY = "Delivery", "Delivery"
    REFILLER = "Refiller", "Refiller"

class User(models.Model):
    user_id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    role = models.TextField(choices=Role.choices, default=Role.CUSTOMER)

    def __str__(self):
        return f"{self.user_id} - {self.first_name} {self.last_name} - {self.role}"
