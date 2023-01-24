from django.conf import settings
from django.conf.urls import include
from django.urls import path
from django.contrib import admin
from django.conf.urls.static import static

from rest_framework import permissions
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from drf_yasg.views import get_schema_view
from drf_yasg import openapi
import os

from users.urls import router as user_router
from users.views import me, password_reset, password_reset_confirm
from contrib.views import global_settings
from contrib.urls import router as contrib_router
from conf.router import Router

schema_view = get_schema_view(
    openapi.Info(
        title="new_fake_drf_project API",
        default_version='v1',
        description="Interface for New Fake DRF project application.",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

# need this to get rid of sidebar:
# https://stackoverflow.com/questions/63286591/django-3-1-admin-page-appearance-issue
admin.autodiscover()
admin.site.enable_nav_sidebar = False

router = Router()
router.extend(user_router)
router.extend(contrib_router)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('drf-auth/', include('rest_framework.urls'), name='rest_framework'),
    path('auth/token/', TokenObtainPairView.as_view(), name='token-obtain-pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('auth/password-reset/', password_reset, name='password-reset'),
    path('auth/password-reset/confirm/', password_reset_confirm, name='password-reset-confirm'),
    path('me/', me, name='me'),
    path('global-settings/', global_settings, name='globals'),
    path('', include(router.urls)),
]

# add api docs everywhere, but not for prod
# (note: DEBUG == False conditional also works here, but would cause testing problems for swagger docs)
if os.environ.get('DJANGO_SETTINGS_MODULE') != 'conf.settings.prod':
    urlpatterns += [
        path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
        path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
        path('admin/doc/', include('django.contrib.admindocs.urls')),
    ]

# serve static/media files if they aren't being served by nginx (i.e. local only not staging, prod, etc.)
if os.environ.get('DJANGO_SETTINGS_MODULE') == 'conf.settings.dev':
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
