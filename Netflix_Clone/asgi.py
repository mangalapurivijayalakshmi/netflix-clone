import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Netflix_Clone.settings')

from django.core.asgi import get_asgi_application
from django.urls import re_path

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

import app.routing


django_asgi_app = get_asgi_application()


application = ProtocolTypeRouter({
    "http": django_asgi_app,

    "websocket": AuthMiddlewareStack(
        URLRouter(
            app.routing.websocket_urlpatterns
        )
    ),
})