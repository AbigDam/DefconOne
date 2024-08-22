from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'/message/(?P<game_id>\d+)/(?P<recipient_id>\d+)/$', consumers.ChatConsumer.as_asgi()),
]
