from django.contrib.admin.sites import AdminSite

from pathlib import Path
from datetime import timedelta
import os

AdminSite.site_header = "New Fake DRF project"
AdminSite.site_title = "New Fake DRF project"

BASE_DIR = Path(__file__).resolve(strict=True).parent.parent.parent
DEBUG = True
SECRET_KEY = "ii=67x7zie8b*1xxz0_-t+^_vwk8_72!i6g_(o0pk@s-@)%a"

ALLOWED_HOSTS = ["*"]

INSTALLED_APPS = [
    "admin_interface",  # django-admin-interface - position is important
    "colorfield",  # django-admin-interface - position is important
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.admindocs",
    "corsheaders",
    "rest_framework",
    "drf_yasg",
    "solo",
    "admin_reorder",
    "django_code_generator",
    "channels",
    # our apps
    "users",
    "contrib",
    "django_filters",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "admin_reorder.middleware.ModelAdminReorder",
]

ROOT_URLCONF = "conf.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": ["templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# WSGI_APPLICATION = 'wsgi.application'
ASGI_APPLICATION = "asgi.application"

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

LANGUAGE_CODE = "fr"
TIME_ZONE = "Europe/Paris"
USE_I18N = True
USE_L10N = True
USE_TZ = True

LANGUAGES = (
    ("fr", "Français"),
    ("en", "English"),
)

CACHES = {
    "default": {
        "LOCATION": "redis://127.0.0.1:6379/1",
        "BACKEND": "django_redis.cache.RedisCache",
        "TIMEOUT": None,
        "OPTIONS": {
            "DB": 1,
            "PARSER_CLASS": "redis.connection.HiredisParser",
            "CONNECTION_POOL_CLASS": "redis.BlockingConnectionPool",
            "CONNECTION_POOL_CLASS_KWARGS": {
                "max_connections": 50,
                "timeout": 20,
            },
            "MAX_CONNECTIONS": 1000,
            "PICKLE_VERSION": -1,
        },
    }
}

# we need this to be able to send messages from django to specific groups/users on instance save, etc.
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [("127.0.0.1", 6379)],
        },
    },
}

REST_FRAMEWORK = {
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticated"],
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ),
    "DEFAULT_METADATA_CLASS": "rest_framework.metadata.SimpleMetadata",
    "PAGE_SIZE": 10,
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.LimitOffsetPagination",
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.ScopedRateThrottle",
    ],
    "DEFAULT_FILTER_BACKENDS": ["django_filters.rest_framework.DjangoFilterBackend"],
}
HEALTH_RATE_THROTTLE = "120/hour"

AUTH_USER_MODEL = "users.User"
SITE_ID = 1
INTERNAL_IPS = ["127.0.0.1", "::1"]

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "static"
MEDIA_URL = "/upload/"
MEDIA_ROOT = BASE_DIR / "upload"

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
CORS_ORIGIN_ALLOW_ALL = True

ADMIN_REORDER = (
    {"app": "admin_interface"},
    {
        "app": "users",
        "label": "Utilisateurs",
        "models": ({"model": "users.User", "label": "Utilisateurs"},),
    },
    {
        "app": "contrib",
        "label": "Configuration",
        "models": (
            {
                "model": "contrib.PublicGlobalSettings",
                "label": "Paramètres globaux publics",
            },
            {
                "model": "contrib.PrivateGlobalSettings",
                "label": "Paramètres globaux privés",
            },
        ),
    },
)


# SOCIAL LOGIN STUFF - YOU CAN DELETE ALL THIS IF NOT USING SOCIAL AUTH #

AUTHENTICATION_BACKENDS = (
    # Facebook OAuth2
    "social_core.backends.facebook.FacebookAppOAuth2",
    "social_core.backends.facebook.FacebookOAuth2",
    # Google OAuth2
    "social_core.backends.google.GoogleOAuth2",
    # Django
    "django.contrib.auth.backends.ModelBackend",
)

X_FRAME_OPTIONS = "SAMEORIGIN"  # needed for django-admin-interface

MIDDLEWARE += [
    "social_django.middleware.SocialAuthExceptionMiddleware",
]

SOCIAL_AUTH_FACEBOOK_KEY = os.environ.get("FACEBOOK_APP_ID")
SOCIAL_AUTH_FACEBOOK_SECRET = os.environ.get("FACEBOOK_SECRET_KEY")
SOCIAL_AUTH_LOGIN_REDIRECT_URL = "/"

SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = os.environ.get("GOOGLE_OAUTH_KEY")
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = os.environ.get("GOOGLE_OAUTH_SECRET")

SOCIAL_AUTH_FACEBOOK_SCOPE = ["email"]
SOCIAL_AUTH_FACEBOOK_PROFILE_EXTRA_PARAMS = {"fields": "id, name, email"}
FACEBOOK_EXTENDED_PERMISSIONS = ["email"]
SOCIAL_AUTH_ADMIN_USER_SEARCH_FIELDS = ["username", "first_name", "email"]
SOCIAL_AUTH_USERNAME_IS_FULL_EMAIL = True

SOCIAL_AUTH_PIPELINE = (
    "social_core.pipeline.social_auth.social_details",
    "social_core.pipeline.social_auth.social_uid",
    "social_core.pipeline.social_auth.auth_allowed",
    "social_core.pipeline.social_auth.social_user",
    "social_core.pipeline.user.get_username",
    "social_core.pipeline.social_auth.associate_by_email",
    "social_core.pipeline.social_auth.associate_user",
    "social_core.pipeline.social_auth.load_extra_data",
    "social_core.pipeline.user.user_details",
)


# Swagger/Redoc settings

SWAGGER_SETTINGS = {
    "SECURITY_DEFINITIONS": {
        "JWT": {
            "type": "apiKey",
            "description": 'Add to Authorization header - example: "Bearer eyJ0eXAiOiJKV1QiLCJ..."',
            "name": "Authorization",
            "in": "header",
        }
    }
}

# JWT Stuff

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=5),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
    "ROTATE_REFRESH_TOKENS": False,
    "BLACKLIST_AFTER_ROTATION": True,
    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY,
    "VERIFYING_KEY": None,
    "AUDIENCE": None,
    "ISSUER": None,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
    "TOKEN_TYPE_CLAIM": "token_type",
    "JTI_CLAIM": "jti",
    "SLIDING_TOKEN_REFRESH_EXP_CLAIM": "refresh_exp",
    "SLIDING_TOKEN_LIFETIME": timedelta(minutes=5),
    "SLIDING_TOKEN_REFRESH_LIFETIME": timedelta(days=1),
}

DEFAULT_FROM_EMAIL = (
    "admin@wertkt.com"  # fallback - normally set by client via back office
)

HEALTH_ENDPOINT_VERSION = "2020.9.26"


# override all of these in prod.py, etc.!
# should be something like 'https://frontend-thing.werkt.com/autologin'
# frontend needs to be able to handle the access token being passed, etc.
FRONTEND_LOGIN_URL = ""
FRONT_URL = ""
BACK_URL = ""

BACKUP_PATH = None  # must be set in dev.py, staging.py, etc. -- for json export of db
MAXIMUM_BACKUP_COUNT = (
    5  # autodelete old backups for this project so we don't exceed this value
)
