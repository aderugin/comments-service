import os

# ==============================================================================
# Django
# ==============================================================================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PROJECT_DIR = os.path.dirname(BASE_DIR)

SECRET_KEY = 'q#mwg8gyaq4y0wk7h5h3bitr8)ca+a4i2ztr%zk!xoj!dlj%x^'

DEBUG = True

ALLOWED_HOSTS = []

SITE_ID = 1

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
)

MIDDLEWARE = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
)

ROOT_URLCONF = 'comments.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates')
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages'
            ],
        },
    },
]

WSGI_APPLICATION = 'comments.wsgi.application'


# Internationalization

LANGUAGE_CODE = 'ru'

TIME_ZONE = 'Asia/Yekaterinburg'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files

STATIC_URL = '/static/'

MEDIA_URL = '/media/'

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
)

MEDIA_ROOT = os.path.join(PROJECT_DIR, 'public', 'media')

STATIC_ROOT = os.path.join(PROJECT_DIR, 'public', 'static')

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder'
)


# Session

SESSION_COOKIE_AGE = 60 * 60 * 24 * 7 * 4

SESSION_COOKIE_DOMAIN = None


# Installed apps

INSTALLED_APPS += (
    'rest_framework',
    'comments.base'
)


# ==============================================================================
# Celery
# ==============================================================================

CELERY_BROKER_URL = 'redis://redis:6379/0'


# ==============================================================================
# REST
# ==============================================================================

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.AllowAny',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 100
}


# ==============================================================================
# Logging
# ==============================================================================

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': os.path.join(PROJECT_DIR, 'debug.log'),
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'comments.apps': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'comments.base': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}

# ==============================================================================
# Databases
# ==============================================================================

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'comments',
        'USER': os.getenv('POSTGRES_USER', 'postgres'),
        'PASSWORD': os.getenv('POSTGRES_PASSWORD', 'postgres'),
        'HOST': os.getenv('POSTGRES_HOST', 'postgres'),
        'PORT': 5432,
    }
}

# ==============================================================================
# Settings imports
# ==============================================================================

# Production settings
if os.environ.get('ENV') == 'production':
    from .production import *  # NOQA

# Develop settings
elif os.environ.get('ENV') == 'develop':
    from .develop import *  # NOQA

# Staging settings
elif os.environ.get('ENV') == 'staging':
    from .staging import *  # NOQA

# Default choice
else:
    from .develop import *  # NOQA

# Local settings
try:
    from .local import *  # NOQA
except ImportError:
    pass
