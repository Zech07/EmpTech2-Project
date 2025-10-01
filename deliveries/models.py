from django.db import models
from users.models import User

class Status(models.TextChoices):
    DELIVERED = "Delivered", "Delivered"
    REFILLING = "Refilling", "Refilling"
    TRANSPORTING = "Transporting", "Transporting"

class WaterJugs(models.Model):
    customer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    water_tag = models.AutoField(primary_key=True)
    status = models.TextField(choices=Status.choices)

    def __str__(self):
        return f"Jug {self.water_tag} - {self.status}"
