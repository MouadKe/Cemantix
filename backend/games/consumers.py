from channels.generic.websocket import AsyncWebsocketConsumer
import json

class EchoConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        if self.scope["user"].is_anonymous:
            await self.close()
        else:
            await self.accept()

    async def receive(self, text_data):
        data = json.loads(text_data)

        await self.send(text_data=json.dumps({
            "user": self.scope["user"].username,
            "echo": data
        }))
