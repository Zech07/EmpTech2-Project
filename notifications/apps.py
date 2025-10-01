from django.apps import AppConfig

class NotificationsConfig(AppConfig):
    name = "notifications"

    def ready(self):
        # ensures signals are imported/connected when Django starts
        import notifications.signals
