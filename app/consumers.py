import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.core.cache import cache


class NotificationConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        if self.scope["user"].is_anonymous:
            await self.close()
            return

        self.group_name = f"user_{self.scope['user'].id}_notifications"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def send_notification(self, event):
        await self.send(text_data=json.dumps({
            "message": event["message"]
        }))


class MovieRoomConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.movie_id = self.scope['url_route']['kwargs']['movie_id']
        self.group_name = f"movie_{self.movie_id}"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

        current = cache.get(f"watching_{self.movie_id}", 0)
        current += 1
        cache.set(f"watching_{self.movie_id}", current, timeout=None)

        await self.channel_layer.group_send(self.group_name, {
            "type": "watching_count_update",
            "count": current,
        })

        # Home page trending badges కి కూడా broadcast చేయడం
        await self.channel_layer.group_send("trending_updates", {
            "type": "trending_update",
            "movie_id": self.movie_id,
            "count": current,
        })

    async def disconnect(self, close_code):
        current = cache.get(f"watching_{self.movie_id}", 1)
        current = max(0, current - 1)
        cache.set(f"watching_{self.movie_id}", current, timeout=None)
        await self.channel_layer.group_send(self.group_name, {
            "type": "watching_count_update",
            "count": current,
        })

        await self.channel_layer.group_send("trending_updates", {
            "type": "trending_update",
            "movie_id": self.movie_id,
            "count": current,
        })

        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        print("MOVIE RECEIVE:", text_data)
        data = json.loads(text_data)
        msg_type = data.get("type")

        if msg_type == "new_comment":
            username = self.scope["user"].username
            await self.channel_layer.group_send(self.group_name, {
                "type": "comment_broadcast",
                "username": username,
                "text": data["text"],
            })

        elif msg_type == "typing":
            username = self.scope["user"].username
            print("TYPING from:", username, "group:", self.group_name)
            await self.channel_layer.group_send(self.group_name, {
                "type": "typing_broadcast",
                "username": username,
                "sender_channel": self.channel_name,
            })

    async def typing_broadcast(self, event):
        print("typing_broadcast called, this channel:", self.channel_name, "sender:", event["sender_channel"])
        if event["sender_channel"] == self.channel_name:
            print("skipping (this is the sender)")
            return
        await self.send(text_data=json.dumps({
            "type": "typing",
            "username": event["username"],
        }))
        print("typing message sent to client")

    async def watching_count_update(self, event):
        await self.send(text_data=json.dumps({
            "type": "watching_count",
            "count": event["count"],
        }))

    async def comment_broadcast(self, event):
        await self.send(text_data=json.dumps({
            "type": "new_comment",
            "username": event["username"],
            "text": event["text"],
        }))


class WatchPartyConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        if self.scope["user"].is_anonymous:
            await self.close()
            return
        self.room_code = self.scope['url_route']['kwargs']['room_code']
        self.group_name = f"watchparty_{self.room_code}"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        await self.channel_layer.group_send(self.group_name, {
            "type": "sync_playback",
            "action": data.get("action"),
            "time": data.get("time", 0),
            "sender_channel": self.channel_name,
        })

    async def sync_playback(self, event):
        if event["sender_channel"] == self.channel_name:
            return
        await self.send(text_data=json.dumps({
            "action": event["action"],
            "time": event["time"],
        }))


class DashboardConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        if self.user.is_anonymous:
            await self.close()
        else:
            self.group_name = f"dashboard_{self.user.id}"
            await self.channel_layer.group_add(self.group_name, self.channel_name)
            await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def dashboard_update(self, event):
        await self.send(text_data=json.dumps(event["data"]))


class PresenceConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        if self.user.is_anonymous:
            await self.close()
        else:
            cache.set(f"online_user_{self.user.id}", True, timeout=None)
            await self.accept()
            await self.send(text_data=json.dumps({"status": "online"}))

    async def disconnect(self, close_code):
        if hasattr(self, "user") and not self.user.is_anonymous:
            cache.delete(f"online_user_{self.user.id}")


class TrendingConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_name = "trending_updates"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def trending_update(self, event):
        await self.send(text_data=json.dumps({
            "movie_id": event["movie_id"],
            "count": event["count"],
        }))