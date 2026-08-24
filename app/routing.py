from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/notifications/$', consumers.NotificationConsumer.as_asgi()),
    re_path(r'ws/movie/(?P<movie_id>[0-9a-f-]+)/$', consumers.MovieRoomConsumer.as_asgi()),
    re_path(r'ws/watchparty/(?P<room_code>\w+)/$', consumers.WatchPartyConsumer.as_asgi()),
    re_path(r'ws/dashboard/$', consumers.DashboardConsumer.as_asgi()),
    re_path(r'ws/presence/$', consumers.PresenceConsumer.as_asgi()),
    re_path(r'ws/trending/$', consumers.TrendingConsumer.as_asgi()),
]
