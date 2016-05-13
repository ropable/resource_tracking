"""
Django settings for resource_tracking project.
"""
from confy import env, database
import os


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# Application definition
DEBUG = env('DEBUG', False)
SECRET_KEY = env('SECRET_KEY')
CSRF_COOKIE_SECURE = env('CSRF_COOKIE_SECURE', False)
SESSION_COOKIE_SECURE = env('SESSION_COOKIE_SECURE', False)
if not DEBUG:
    # Localhost, UAT and Production hosts:
    ALLOWED_HOSTS = [
        'localhost',
        '127.0.0.1',
        'sss.dpaw.wa.gov.au',
        'sss.dpaw.wa.gov.au.',
        'sss-uat.dpaw.wa.gov.au',
        'sss-uat.dpaw.wa.gov.au.',
    ]
INTERNAL_IPS = ['127.0.0.1', '::1']
ROOT_URLCONF = 'resource_tracking.urls'
WSGI_APPLICATION = 'resource_tracking.wsgi.application'

CSW_URL = env('CSW_URL', 'https://oim.dpaw.wa.gov.au/catalogue/sss/')
PRINTING_URL = os.environ.get('PRINTING_URL', "https://printing.dpaw.wa.gov.au")
TRACPLUS_URL = os.environ.get('TRACPLUS_URL', False)
DEVICE_HTTP_CACHE_TIMEOUT = env('DEVICE_HTTP_CACHE_TIMEOUT', 60)
HISTORY_HTTP_CACHE_TIMEOUT = env('HISTORY_HTTP_CACHE_TIMEOUT', 60)

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.gis',
    'tastypie',
    'django_extensions',
    'django_uwsgi',
    'resource_autoversion',
    'resource_tracking',
    # Sub-app definitions
    'tracking',
    'djgeojson',
    'dpaw_utils'
)
MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'dpaw_utils.middleware.SSOLoginMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

# Email settings
ADMINS = ('asi@dpaw.wa.gov.au',)
EMAIL_HOST = env('EMAIL_HOST', 'email.host')
EMAIL_PORT = env('EMAIL_PORT', 25)
EMAIL_USER = env('EMAIL_USER', 'username')
EMAIL_PASSWORD = env('EMAIL_PASSWORD', 'password')


SERIALIZATION_MODULES = {
    "geojson": "djgeojson.serializers",
}


# Database
DATABASES = {
    # Defined in the DATABASE_URL env variable.
    'default': database.config(),
}

# Project authentication settings
AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
)

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Australia/Perth'
USE_I18N = True
USE_L10N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')


# Logging settings
# Ensure that the logs directory exists:
if not os.path.exists(os.path.join(BASE_DIR, 'logs')):
    os.mkdir(os.path.join(BASE_DIR, 'logs'))
LOGGING = {
    'version': 1,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(message)s'
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'resourcetracking.log'),
            'formatter': 'verbose',
            'maxBytes': 1024 * 1024 * 5
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['file'],
            'level': 'INFO'
        },
        'log': {
            'handlers': ['file'],
            'level': 'INFO'
        },
    }
}

JS_MINIFY = False
RESOURCE_FILES_WITH_AUTO_VERSION = [
    os.path.join(BASE_DIR, "tracking", "static", "sss", "sss.js"),
    os.path.join(BASE_DIR, "tracking", "static", "sss", "leaflet.dump.js"),
    os.path.join(BASE_DIR, "tracking", "static", "sss", "sss.css"),
]
