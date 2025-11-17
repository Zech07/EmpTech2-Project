from django.apps import AppConfig
from django.contrib.auth.models import Group

class PosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'pos'

    def ready(self):
        self.create_default_groups()
