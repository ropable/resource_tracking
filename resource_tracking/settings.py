from dbca_utils.utils import env
from django.core.exceptions import DisallowedHost
from django.db.utils import OperationalError
import dj_database_url
import os
from pathlib import Path
import sys
import tomllib
from zoneinfo import ZoneInfo

# Project paths
# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = str(Path(__file__).resolve().parents[1])

# Application definition
project = tomllib.load(open(os.path.join(BASE_DIR, "pyproject.toml"), "rb"))
APPLICATION_VERSION_NO = project["tool"]["poetry"]["version"]
DEBUG = env("DEBUG", False)
SECRET_KEY = env("SECRET_KEY", "PlaceholderSecretKey")
CSRF_COOKIE_SECURE = env("CSRF_COOKIE_SECURE", False)
CSRF_TRUSTED_ORIGINS = env("CSRF_TRUSTED_ORIGINS", "http://127.0.0.1").split(",")
SESSION_COOKIE_SECURE = env("SESSION_COOKIE_SECURE", False)
if not DEBUG:
    ALLOWED_HOSTS = env("ALLOWED_HOSTS", "localhost").split(",")
else:
    ALLOWED_HOSTS = ["*"]
INTERNAL_IPS = ["127.0.0.1", "::1"]
ROOT_URLCONF = "resource_tracking.urls"
WSGI_APPLICATION = "resource_tracking.wsgi.application"
TRACPLUS_URL = env("TRACPLUS_URL", "")
DFES_URL = env("DFES_URL", "")
DFES_USER = env("DFES_USER", "")
DFES_PASS = env("DFES_PASS", "")
# Add scary warning on device edit page for prod
PROD_SCARY_WARNING = env("PROD_SCARY_WARNING", False)
DEVICE_HTTP_CACHE_TIMEOUT = env("DEVICE_HTTP_CACHE_TIMEOUT", 60)
GEOSERVER_URL = env("GEOSERVER_URL", "")
INSTALLED_APPS = [
    "whitenoise.runserver_nostatic",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.gis",
    "tastypie",
    "django_extensions",
    "djgeojson",
    "tracking",
]
MIDDLEWARE = [
    "resource_tracking.middleware.HealthCheckMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "dbca_utils.middleware.SSOLoginMiddleware",
]
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
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
DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

# Email settings
EMAIL_HOST = env("EMAIL_HOST", "email.host")
EMAIL_PORT = env("EMAIL_PORT", 25)
EMAIL_USER = env("EMAIL_USER", "username")
EMAIL_PASSWORD = env("EMAIL_PASSWORD", "password")
EMAIL_IRIDITRAK = env("EMAIL_IRIDITRAK", "sbdservice@sbd.iridium.com")
EMAIL_DPLUS = env("EMAIL_DPLUS", "dplus@asta.net.au")
EMAIL_SPOT = env("EMAIL_SPOT", "noreply@findmespot.com")
EMAIL_MP70 = env("EMAIL_MP70", "sierrawireless_v1@mail.lan.fyi")


SERIALIZATION_MODULES = {
    "geojson": "djgeojson.serializers",
}


# Database
DATABASES = {
    # Defined in the DATABASE_URL env variable.
    "default": dj_database_url.config(),
}

# Project authentication settings
AUTHENTICATION_BACKENDS = ("django.contrib.auth.backends.ModelBackend",)

# Internationalization
LANGUAGE_CODE = "en-us"
TIME_ZONE = "Australia/Perth"
TZ = ZoneInfo(TIME_ZONE)
USE_I18N = True
USE_L10N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, "resource_tracking", "static"),
    os.path.join(BASE_DIR, "tracking", "static"),
)
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
WHITENOISE_ROOT = STATIC_ROOT

# Logging settings - log to stdout
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {"format": "%(asctime)s %(levelname)-12s %(message)s"},
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
            "stream": sys.stdout,
            "level": "INFO",
        },
    },
    "loggers": {
        "": {
            "handlers": ["console"],
            "level": "INFO",
        },
    },
}

# Tastypie settings
TASTYPIE_DEFAULT_FORMATS = ["json"]
TASTYPIE_DATETIME_FORMATTING = "iso-8601-strict"


def sentry_excluded_exceptions(event, hint):
    """Exclude defined class(es) of Exception from being reported to Sentry.
    These exception classes are generally related to operational or configuration issues,
    and they are not errors that we want to capture.
    https://docs.sentry.io/platforms/python/configuration/filtering/#filtering-error-events
    """
    if "exc_info" in hint and hint["exc_info"]:
        # Exclude database-related errors (connection error, timeout, DNS failure, etc.)
        if hint["exc_info"][0] is OperationalError:
            return None
        # Exclude exceptions related to host requests not in ALLOWED_HOSTS.
        elif hint["exc_info"][0] is DisallowedHost:
            return None

    return event


# Sentry settings
SENTRY_DSN = env("SENTRY_DSN", None)
SENTRY_SAMPLE_RATE = env("SENTRY_SAMPLE_RATE", 1.0)  # Error sampling rate
SENTRY_TRANSACTION_SAMPLE_RATE = env(
    "SENTRY_TRANSACTION_SAMPLE_RATE", 0.0
)  # Transaction sampling
SENTRY_PROFILES_SAMPLE_RATE = env(
    "SENTRY_PROFILES_SAMPLE_RATE", 0.0
)  # Proportion of sampled transactions to profile.
SENTRY_ENVIRONMENT = env("SENTRY_ENVIRONMENT", None)
if SENTRY_DSN and SENTRY_ENVIRONMENT:
    import sentry_sdk

    sentry_sdk.init(
        dsn=SENTRY_DSN,
        sample_rate=SENTRY_SAMPLE_RATE,
        traces_sample_rate=SENTRY_TRANSACTION_SAMPLE_RATE,
        environment=SENTRY_ENVIRONMENT,
        profiles_sample_rate=SENTRY_PROFILES_SAMPLE_RATE,
        release=APPLICATION_VERSION_NO,
        before_send=sentry_excluded_exceptions,
    )
