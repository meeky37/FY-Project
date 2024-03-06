from .settings import *


# SQLite for tests
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}



# CSRF checks disabled for testing
MIDDLEWARE = [mw for mw in MIDDLEWARE if mw != 'django.middleware.csrf.CsrfViewMiddleware']

DEBUG = True

# Redis/celery containers not in testing environment
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True
