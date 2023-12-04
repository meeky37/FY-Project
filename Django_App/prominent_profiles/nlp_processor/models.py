import os

from django.db import models
from django.conf import settings


class ProcessedFile(models.Model):
    search_term = models.CharField(max_length=255)
    file_name = models.CharField(max_length=255)
    media_path = models.CharField(max_length=255)
    nlp_applied = models.BooleanField(default=False)

    def full_path(self):
        return os.path.join(settings.ARTICLE_SCRAPER_MEDIA_ROOT, self.media_path, self.file_name)