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

class BoundError(models.Model):
    bound_start = models.IntegerField()
    bound_end = models.IntegerField()
    left_segment = models.TextField()
    mention_segment = models.TextField()
    right_segment = models.TextField()
    error_message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)