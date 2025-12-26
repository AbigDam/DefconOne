from django.urls import path
from .consumers import RefreshConsumer

websocket_urlpatterns = [
    path("ws/refresh/", RefreshConsumer.as_asgi()),
]
