import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import django
import AWSDefcon1App.routing 

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "AWSDefcon1.settings")
django.setup()

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            AWSDefcon1App.routing.websocket_urlpatterns
        )
    ),
})
