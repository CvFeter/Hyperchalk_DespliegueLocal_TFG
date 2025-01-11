"""
Django settings for draw project.

Generated by 'django-admin startproject' using Django 3.2.12.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""
from pathlib import Path
from typing import Any, Dict, List, Union

from django.core.exceptions import ImproperlyConfigured
from django.utils.log import DEFAULT_LOGGING

from draw.utils import StrLike, TrustedOrigins, deepmerge

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False #CAMBIAR OTRA VEZ A FALSE

ALLOWED_HOSTS: List[str] = ['localhost', '127.0.0.1']

INTERNAL_IPS = ['127.0.0.1']

# Configure https reverse proxy
# https://docs.djangoproject.com/en/4.0/ref/settings/#secure-proxy-ssl-header

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Application definition

INSTALLED_APPS = [
    'collab',
    'ltiapi',
    'pylti1p3.contrib.django.lti1p3_tool_config',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'channels'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

WS_MIDDLEWARE = [
    'channels.security.websocket.AllowedHostsOriginValidator',
    'channels.auth.AuthMiddlewareStack',
    'channels.sessions.SessionMiddlewareStack',
]

ROOT_URLCONF = 'draw.urls'
CHANNELS_URLCONF = 'draw.urls_ws'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'draw' / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.template.context_processors.media',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'draw.wsgi.application'
ASGI_APPLICATION = 'draw.asgi.application'

# Logging
# https://docs.djangoproject.com/en/3.2/topics/logging/

LOGGING = deepmerge(DEFAULT_LOGGING, {
    'formatters': {
        'draw.websocket': {
            '()': 'draw.utils.WebSocketFormatter',
            'format': '[{server_time}] {message}',
            'style': '{',
        },
    },
    'handlers': {
        'draw.websocket': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'draw.websocket',
        },
    },
    'loggers': {
        'draw.websocket': {
            'handlers': ['draw.websocket'],
            'level': 'INFO',
            'propagate': False,
        }
    }
})

# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES: Dict[str, Dict[str, Union[StrLike, Dict[str, StrLike]]]] = {}
DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

# Channel Layers
# https://channels.readthedocs.io/en/latest/topics/channel_layers.html

CHANNEL_LAYERS: Dict[str, Dict[str, Any]]

# Session Engine
# https://docs.djangoproject.com/en/dev/topics/http/sessions/#configuring-the-session-engine

SESSION_ENGINE = 'django.contrib.sessions.backends.signed_cookies'

# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# https://docs.djangoproject.com/en/3.2/topics/auth/customizing/#auth-custom-user
AUTH_USER_MODEL = 'ltiapi.CustomUser'

# https://docs.djangoproject.com/en/3.2/ref/settings/#csrf-trusted-origins

CSRF_TRUSTED_ORIGINS = TrustedOrigins()

# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'de-DE'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = '/static/'

STATIC_ROOT = BASE_DIR / 'static_copy'

STATICFILES_DIRS = [
    BASE_DIR / 'client' / 'dist',
    BASE_DIR / 'draw' / 'static',
    #BASE_DIR / 'collab' / 'static',
]

# Media Uploads

MEDIA_URL = '/media/'

MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

# DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Settings for LTI ToolConfig
# see lti.tool_config.py

LTI_CONFIG = {
    'title': 'Hyperchalk',
    'description': 'Make drawing assignments for your students. Supports single and group work.',
    'vendor_name': 'EduTec@DIPF',
    'vendor_url': 'https://www.edutec.science/',
    'vendor_contact_name': 'Sebastian Gombert',
    'vendor_contact_email': 'gombert@dipf.de',
}

# Create custom room when user visits the index page
SHOW_CREATE_ROOM_PAGE = False

IMPRINT_URL = None

# Allow the creation of rooms when the user visits the index page without a room query (?room=...)
ALLOW_AUTOMATIC_ROOM_CREATION = False

# If set to false, users will need to be logged in.
ALLOW_ANONYMOUS_VISITS = False

# This sets the default value for complete pointer and element tracking (Log Records)
ENABLE_TRACKING_BY_DEFAULT = True
ENABLE_TRACKING_BY_DEFAULT_FOR_LTI = True

# how often the clients are going to broadcast updates on change (milliseconds)
BROADCAST_RESOLUTION_THROTTLE_MSEC = 100

# how many seconds after a change clients will wait before issuing a save command (milliseconds)
SAVE_ROOM_MAX_WAIT_MSEC = 15_000

# how many groups there are allowd in a group assignment
MAX_GROUPS = 50

# call this from your custom settings
def finalize_settings(final_locals: Dict[str, Any]):
    required_vars = {'SECRET_KEY', 'DATABASES', 'TIME_ZONE', 'LINK_BASE'}
    missing = required_vars.difference(final_locals.keys())
    if missing:
        raise ImproperlyConfigured(
            f'The following mandatory keys are missing from your config: {missing}')
