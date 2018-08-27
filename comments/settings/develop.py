from . import *  # NOQA

ALLOWED_HOSTS = ['*']

SITE_ID = 1

DEBUG = True

COMPRESS_ENABLED = not DEBUG

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

INSTALLED_APPS += (  # NOQA
    'debug_toolbar',
)

MIDDLEWARE = (
    'debug_toolbar.middleware.DebugToolbarMiddleware',
) + MIDDLEWARE  # NOQA

DEBUG_TOOLBAR_CONFIG = {
    'SHOW_TOOLBAR_CALLBACK': lambda request: True,
}
