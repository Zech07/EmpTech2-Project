"""
ASGI config for project.

Exposes the ASGI callable as a module-level variable named `application`.
"""

import os
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.core.asgi import get_asgi_application

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')

# Import websocket routing from apps