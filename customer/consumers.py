import json
from channels.generic.websocket import AsyncWebsocketConsumer

class CustomerConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Grab the user_id from the URL
        self.user_id = self.scope['url_route']['kwargs']['user_id']
        self.group_name = f"customer_{self.user_id}"

        # Join the personalized group
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave the group
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    # Receive notification from the group
    async def send_notification(self, event):
        await self.send(text_data=json.dumps({
            "title": event['title'],
            "message": event['message']
        }))
