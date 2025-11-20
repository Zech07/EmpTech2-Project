from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    # Include the user_id in the URL so we can create a personal group
    re_path(r'ws/customer/(?P<user_id>\d+)/$', consumers.CustomerConsumer.as_asgi()),
]
