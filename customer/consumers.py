from channels.generic.websocket import AsyncWebsocketConsumer
import json

class POSConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Group for staff and admin to receive updates
        await self.channel_layer.group_add("staff_group", self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("staff_group", self.channel_name)

    async def send_notification(self, event):
        await self.send(text_data=json.dumps({
            "title": event['title'],
            "message": event['message']
        }))