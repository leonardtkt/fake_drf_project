from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()

router.register(
    'auth/oauth/login',
    views.SocialViewSet,
    basename='oauth-login',
)

router.register(
    'users',
    views.UserViewSet,
    basename='users',
)
