from channels.generic.websocket import AsyncWebsocketConsumer
import json

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user = self.scope['user']
        # Only staff/admin can connect
        if user.is_anonymous or not user.groups.filter(name__in=['staff', 'admin']).exists():
            await self.close()
        else:
            self.group_name = "staff_admin_group"
            await self.channel_layer.group_add(self.group_name, self.channel_name)
            await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def send_notification(self, event):
        await self.send(text_data=json.dumps({
            "title": event['title'],
            "message": event['message']
        }))
