"""
Models declared here are closely related for the nlp processor app use - i.e. they won't be
displayed in the front end app unlike Article, Entity etc. which are used across the django app
but are placed in profiles app as they are more tightly associated with the frontend user.

This module handles the tracking of bing api article JSON files, bound errors, plus article
statistics and their respective comparisons.
"""

import os
from django.db import models
from django.conf import settings
from profiles_app.models import Article


class ArticleStatistics(models.Model):
    """
    Stores detailed linguistic and statistical analysis results for articles. This includes metrics
    like word count, term count, various diversity indices (e.g., VOCD, Yule's K), and specific word
    frequencies.
    Each instance is linked to a unique Article model instance.
    Contents used by SimilarArticlePair to calculate % differences.
    """
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
    """
    Represents a pair of articles and quantifies their similarity based on various metrics,
    including hash similarity scores and differences in linguistic statistics (e.g., word count,
    term diversity).
    Useful for identifying potentially duplicate or closely related articles to reject their
    processing.
    """
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
    """
    Tracks bing news api files processed for NLP analysis.
    Contains metadata such as the search term used to acquire the file, the file name, the path
    to the file, and whether NLP analysis has successfully been applied - allowing recovery from
    failure without skipping articles.
    """
    search_term = models.CharField(max_length=255)
    file_name = models.CharField(max_length=255)
    media_path = models.CharField(max_length=255)
    nlp_applied = models.BooleanField(default=False)

    def full_path(self):
        return os.path.join(settings.ARTICLE_SCRAPER_MEDIA_ROOT, self.media_path, self.file_name)


class BoundError(models.Model):
    """
    Bound error used for NewsSentiment exceptions to identify tokenization improvements,
    poor extraction, etc.
    These records can be used to improve pre-processing steps in article_processor.py
    """
    article = models.ForeignKey(Article, on_delete=models.CASCADE, null=True, blank=True,
                                default=None)
    bound_start = models.IntegerField()
    bound_end = models.IntegerField()
    left_segment = models.TextField()
    mention_segment = models.TextField()
    right_segment = models.TextField()
    error_message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
