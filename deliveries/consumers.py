from channels.generic.websocket import AsyncWebsocketConsumer
import json

class DeliveryConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add("staff_group", self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("staff_group", self.channel_name)
