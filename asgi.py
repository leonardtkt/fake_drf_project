# ordering of imports, etc matters here - change the following at your own peril

from django.core.asgi import get_asgi_application

asgi_app = get_asgi_application()

from channels.auth import AuthMiddlewareStack  # noqa
from channels.routing import ProtocolTypeRouter, URLRouter  # noqa
from contrib.urls import websocket_urls  # noqa

websocket_router = URLRouter(websocket_urls)

application = ProtocolTypeRouter({
    'http': asgi_app,
    'websocket': AuthMiddlewareStack(websocket_router),
})
