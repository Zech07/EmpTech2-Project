import json
from channels.generic.websocket import AsyncWebsocketConsumer

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user = self.scope["user"]

        if user.is_anonymous:
            await self.close()
        else:
            # Example: add user to group based on role or DB field
            if user.is_staff:
                self.group_name = "admin_group"
            elif hasattr(user, 'customer'):
                self.group_name = "customer_group"
            else:
                self.group_name = "general_group"

            # Join the correct group
            await self.channel_layer.group_add(self.group_name, self.channel_name)
            await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def send_notification(self, event):
        await self.send(text_data=json.dumps({
            "title": event["title"],
            "message": event["message"],
        }))
