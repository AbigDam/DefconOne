from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

def refresh_all():
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        "refresh_page",
        {
            "type": "refresh"
        }
    )
