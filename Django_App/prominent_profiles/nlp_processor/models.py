import os
from django.db import models
from django.conf import settings
from profiles_app.models import Article

class ArticleStatistics(models.Model):
    article = models.OneToOneField(Article, on_delete=models.CASCADE, primary_key=True)

    fuzzy_hash = models.CharField(max_length=128, null=True)
    word_count = models.IntegerField(null=True, blank=True)
    terms_count = models.IntegerField(null=True, blank=True)
    vocd = models.FloatField(null=True, blank=True)
    yulek = models.FloatField(null=True, blank=True)
    simpsond = models.FloatField(null=True, blank=True)
    the_count = models.IntegerField(null=True, blank=True)
    and_count = models.IntegerField(null=True, blank=True)
    is_count = models.IntegerField(null=True, blank=True)
    of_count = models.IntegerField(null=True, blank=True)
    in_count = models.IntegerField(null=True, blank=True)
    to_count = models.IntegerField(null=True, blank=True)
    it_count = models.IntegerField(null=True, blank=True)
    that_count = models.IntegerField(null=True, blank=True)
    with_count = models.IntegerField(null=True, blank=True)


class SimilarArticlePair(models.Model):
    article1 = models.ForeignKey(ArticleStatistics, related_name='article1',
                                 on_delete=models.CASCADE)
    article2 = models.ForeignKey(ArticleStatistics, related_name='article2',
                                 on_delete=models.CASCADE)
    hash_similarity_score = models.IntegerField()
    words_diff = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    terms_diff = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    vocd_diff = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    yulek_diff = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    simpsond_diff = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    avg_count_diff = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    the_diff = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    and_diff = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    is_diff = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    of_diff = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    in_diff = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    to_diff = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    it_diff = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    that_diff = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    with_diff = models.DecimalField(max_digits=5, decimal_places=2, null=True)

    def calculate_average_diff(self):
        diff_fields = ['the_diff', 'and_diff', 'is_diff', 'of_diff', 'in_diff', 'to_diff',
                       'it_diff', 'that_diff', 'with_diff']

        diffs = [getattr(self, field) for field in diff_fields if getattr(self, field) is not None]

        # Likely to be very few mentions or an
        # extra message on page creating a huge % difference so filter.
        diffs = [diff for diff in diffs if diff < 50]

        if diffs:
            return sum(diffs) / len(diffs)
        else:
            return None


class ProcessedFile(models.Model):
    search_term = models.CharField(max_length=255)
    file_name = models.CharField(max_length=255)
    media_path = models.CharField(max_length=255)
    nlp_applied = models.BooleanField(default=False)

    def full_path(self):
        return os.path.join(settings.ARTICLE_SCRAPER_MEDIA_ROOT, self.media_path, self.file_name)


class BoundError(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, null=True, blank=True,
                                default=None)
    bound_start = models.IntegerField()
    bound_end = models.IntegerField()
    left_segment = models.TextField()
    mention_segment = models.TextField()
    right_segment = models.TextField()
    error_message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
