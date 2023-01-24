from django.urls import path

from rest_framework.routers import DefaultRouter

from . import views
from . import consumers

router = DefaultRouter()


router.register(
    'langs',
    views.LanguageViewSet,
    basename='langs',
)

router.register(
    '_health',
    views.HealthViewSet,
    basename='health',
)


# These are our sync/async websocket routes which will be picked up by asgi.py
websocket_urls = [
    path('ws/user-watcher/', consumers.UserConsumer.as_asgi(), name='ws-user'),
]
