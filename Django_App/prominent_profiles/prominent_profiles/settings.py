"""
Django settings for prominent_profiles project.

Generated by 'django-admin startproject' using Django 4.1.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.1/ref/settings/
"""
import os
from pathlib import Path

# from .constants import DB_PASSWORD

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
if os.getenv('RUNNING_IN_DOCKER', 'False') == 'True':
    SECRET_KEY = os.getenv('SECRET_KEY', '')
    JWT_SECRET_KEY = os.getenv('SECRET_KEY', '')
else:
    SECRET_KEY = 'django-insecure-15i*(zucahz)+@8ikq9!%4dibe3#bjubrl4xmh17yjcbmabt9i'
    JWT_SECRET_KEY = 'django-insecure-15i*(zucahz)+@8ikq9!%4dibe3#bjubrl4xmh17yjcbmabt9i'


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ["localhost", "157.245.46.42", "www.prominentprofiles.com",
                 "prominentprofiles.com",
                 "api.ipify.org", "www.shadowserver.org", "0.0.0.0"]

# Application definition

INSTALLED_APPS = [
    'admin_shortcuts',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'drf_yasg',
    'django_celery_beat',
    'adminsortable2',
    'profiles_app',
    'nlp_processor',
    'accounts',
    'corsheaders',
    'rest_framework',
    'rest_framework_simplejwt',
    'django_rest_passwordreset',
    'django_extensions'
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
}

AUTHENTICATION_BACKENDS = [
    'accounts.backends.EmailPhoneBackend',
    'django.contrib.auth.backends.ModelBackend'
]

AUTH_USER_MODEL = 'accounts.CustomUser'

SIMPLE_JWT = {
    'AUTH_HEADER_TYPES': ('Bearer',),
    'TOKEN_COOKIE_SECURE': True,  # True for production will need HTTPS setup.
    'TOKEN_COOKIE_HTTPONLY': True,
}

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'accounts.middleware.UserActivityMiddleware',
]

# CORS_TRUSTED_ORIGINS = ["http://localhost:8080",
#                         "http://localhost:8084",  # Obviously, do not use in production.
#                         "http://localhost:8081",
#                         "http://localhost:8082",
#                         "http://localhost:8083",
#                         "http://localhost:8085",
#                         "http://localhost:8086",
#                         "http://localhost:8087",
#                         "http://localhost:8088",
#                         "http://localhost:8089",
#                         ]

CORS_ALLOWED_ORIGINS = [
    "http://localhost:8080",
    "https://localhost:8080",
    "http://157.245.46.42",
    "https://157.245.46.42",
    "http://www.prominentprofiles.com",
    "https://www.prominentprofiles.com",
    "http://prominentprofiles.com",
    "https://prominentprofiles.com",
]

CORS_TRUSTED_ORIGINS = [
    "http://localhost:8080",
    "https://localhost:8080",
    "http://157.245.46.42",
    "https://157.245.46.42",
    "http://www.prominentprofiles.com",
    "https://www.prominentprofiles.com",
    "http://prominentprofiles.com",
    "https://prominentprofiles.com",
]

CORS_ORIGIN_REGEX_WHITELIST = [
    r"^https://\w+\.prominentprofiles\.com$",
]

CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]

CORS_ALLOW_CREDENTIALS = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_NAME = "csrftoken"
CSRF_HEADER_NAME = "HTTP_X_CSRFTOKEN"
CSRF_TRUSTED_ORIGINS = ['http://localhost:8080',
                        "https://www.prominentprofiles.com",
                        'https://prominentprofiles.com']
CSRF_COOKIE_DOMAIN = '.prominentprofiles.com'
CSRF_COOKIE_PATH = '/'
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')


ROOT_URLCONF = 'prominent_profiles.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'prominent_profiles.wsgi.application'

# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases


if os.getenv('RUNNING_IN_DOCKER', 'False') == 'True':
    # Configuration for running inside Docker
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.getenv('DB_NAME', 'prominent_profiles'),
            'USER': os.getenv('DB_USER', 'django_access'),
            'PASSWORD': os.getenv('DB_PASSWORD', ''),
            'HOST': os.getenv('DB_HOST', 'db'),
            'PORT': os.getenv('DB_PORT', '25060'),
            'OPTIONS': {
                'options': '-c statement_timeout=300000'  # Timeout = 300 seconds / 5 minutes
            },
        }
    }
else:
    # Configuration for running locally/not in Docker
    # print('using fall back')
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

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

# Internationalization
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

ARTICLE_SCRAPER_MEDIA_ROOT = os.path.join(BASE_DIR, 'nlp_processor', 'media')
MEDIA_URL = '/media/'
MEDIA_ROOT = ARTICLE_SCRAPER_MEDIA_ROOT

# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'


ADMIN_SHORTCUTS = [
    {
        'shortcuts': [
            {
                'url': '/admin/profiles_app/entity/merge_review/',
                'title': 'Merge Review',
                'open_new_window': True,
            },
            {
                'url': '/admin/profiles_app/entity/merge_review/app_visible/',
                'title': 'Merge Review (App Visible)',
                'open_new_window': True,
            },
        ],
        'title': 'Fuzzy Matching',
    },
]

DEFAULT_FROM_EMAIL = 'info@prominentprofiles.com'
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtppro.zoho.eu'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'info@prominentprofiles.com'
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_PASSWORD', '')

CELERY_BROKER_URL = 'redis://redis:6379/0'
CELERY_RESULT_BACKEND = 'redis://redis:6379/0'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'GMT'

CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'
