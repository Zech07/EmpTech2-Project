from django.apps import AppConfig

class PosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'pos'

<<<<<<< HEAD
    def ready(self):
        import pos.signals  # This imports the signals
=======
>>>>>>> b774a21d51044f5960c809fe83a88f852e9bfce8
