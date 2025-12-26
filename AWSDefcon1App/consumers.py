from channels.generic.websocket import AsyncWebsocketConsumer
import json

class RefreshConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add("refresh_page", self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("refresh_page", self.channel_name)

    async def refresh(self, event):
        await self.send(text_data=json.dumps({"refresh": True}))
