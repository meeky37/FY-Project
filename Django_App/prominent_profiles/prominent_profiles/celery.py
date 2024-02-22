import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'prominent_profiles.settings')

app = Celery('prominent_profiles')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()