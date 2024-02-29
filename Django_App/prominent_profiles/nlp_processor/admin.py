"""
Customises the Django admin interface for the models: ProcessedFile, BoundError, ArticleStatistics,
and SimilarArticlePair. This includes setting display columns, custom actions to update model fields,
and filters to segment data based on specific criteria.
"""

from datetime import timedelta

from django.contrib import admin
from django.db import models
from django.db.models import Case, When, Value
from django.db.models import F
from django.utils.translation import gettext as _

from .models import ProcessedFile, BoundError, ArticleStatistics, SimilarArticlePair


class ProcessedFileAdmin(admin.ModelAdmin):
    """
    Custom admin interface for the ProcessedFile model.
    Provides custom actions to mark the NLP processing status of files, facilitating easy manipulation
    of job runs. This feature is particularly useful for testing the NLP job on a smaller set of articles
    or rerunning it on specific files in cases where bugs or unhandled exceptions were
    encountered in development.
    """
    list_display = ['search_term', 'file_name', 'media_path', 'nlp_applied']

    def set_nlp_applied_false(self, request, queryset):
        queryset.update(nlp_applied=False)

    set_nlp_applied_false.short_description = "Set NLP Applied to FALSE for selected items"

    actions = [set_nlp_applied_false]

    def set_nlp_applied_true(self, request, queryset):
        queryset.update(nlp_applied=True)

    set_nlp_applied_true.short_description = "Set NLP Applied to TRUE for selected items"

    actions = [set_nlp_applied_false, set_nlp_applied_true]


class DuplicatePrediction(admin.SimpleListFilter):
    """
    A custom filter for the admin interface to segment SimilarArticlePair instances based on
    the likelihood of being duplicates, determined by a combination of hash similarity score
    and other metrics.
    """
    title = _('Duplicate Prediction')
    parameter_name = 'hash_similarity_score'

    def lookups(self, request, model_admin):
        return (
            ('high', _('Likely Duplicates')),
            ('low', _('Unlikely Duplicates')),
        )

    def queryset(self, request, queryset):
        if self.value() == 'high':
            return queryset.filter(hash_similarity_score__gte=90) | (
                queryset.filter(
                    hash_similarity_score__gte=65, words_diff__lt=10, terms_diff__lt=10,
                    vocd_diff__lt=5, yulek_diff__lt=10, simpsond_diff__lt=10,
                    the_diff__lt=20, and_diff__lt=20, is_diff__lt=20,
                    of_diff__lt=20, in_diff__lt=20, to_diff__lt=20,
                    it_diff__lt=20, that_diff__lt=20, with_diff__lt=20
                ).annotate(
                    published_close_together=Case(
                        When(
                            article2__article__publication_date__lte=F(
                                'article1__article__publication_date') + timedelta(days=3),
                            then=Value(True)
                        ),
                        default=Value(False),
                        output_field=models.BooleanField()
                    )
                ).filter(published_close_together=True)
            )
        elif self.value() == 'low':
            return queryset


class SimilarArticlePairAdmin(admin.ModelAdmin):
    """
    Admin interface customisation for SimilarArticlePair model.
    Provides detailed views and filters to compare articles for similarity with the aim of
    avoiding expensive duplicate analysis of articles and the poor user expierence of
    encountering duplicate ArticleEntry cards on the web app.
    """
    list_display = ['id', 'get_article_1_headline', 'get_article_2_headline',
                    'get_article_1_site_name', 'get_article_2_site_name',
                    'hash_similarity_score',
                    'words_diff',
                    'terms_diff',
                    'yulek_diff', 'vocd_diff', 'avg_count_diff', 'simpsond_diff', 'the_diff',
                    'and_diff',
                    'is_diff', 'of_diff', 'in_diff', 'to_diff', 'it_diff', 'that_diff',
                    'with_diff']
    list_filter = [DuplicatePrediction]
    search_fields = ['article1__article__id', 'article2__article__id']
    readonly_fields = ['get_article_1_headline', 'get_article_2_headline'
        , 'get_article_1_site_name', 'get_article_2_site_name']

    def get_article_1_headline(self, obj):
        """
        Returns the headline of the first article in a SimilarArticlePair instance.
        """
        return obj.article1.article.headline

    get_article_1_headline.short_description = 'Article 1 Headline'
    get_article_1_headline.admin_order_field = 'article1__headline'

    def get_article_2_headline(self, obj):
        """
        Returns the headline of the second article in a SimilarArticlePair instance.
        """
        return obj.article2.article.headline

    get_article_2_headline.short_description = 'Article 2 Headline'
    get_article_2_headline.admin_order_field = 'article2__headline'

    def get_article_1_site_name(self, obj):
        """
        Returns the site name (usually but not always the publisher) of the first article in a
        SimilarArticlePair instance.
        """
        return obj.article1.article.site_name

    get_article_1_site_name.short_description = 'Article 1 Site Name'
    get_article_1_site_name.admin_order_field = 'article1__site_name'

    def get_article_2_site_name(self, obj):
        """
        Returns the site name (usually but not always the publisher) of the second article in a
        SimilarArticlePair instance.
        """
        return obj.article2.article.site_name

    get_article_2_site_name.short_description = 'Article 2 Site Name'
    get_article_2_site_name.admin_order_field = 'article2__site_name'


class BoundErrorAdmin(admin.ModelAdmin):
    """
    Admin customisation to present bound error contents upfront, to identify tokenization
    improvement or spot anomalies without needing to delve into individual BoundError details.
    """
    list_display = ('article', 'bound_start', 'bound_end', 'left_segment', 'mention_segment',
                    'right_segment', 'error_message', 'timestamp')


class ArticleStatisticsAdmin(admin.ModelAdmin):
    """
    Admin customisation to present statistics upfront, administrators can quickly assess the linguistic properties
    of articles, identify trends, or spot anomalies without needing to delve into individual article details.
    """
    list_display = (
    'article', 'fuzzy_hash', 'word_count', 'terms_count', 'vocd', 'yulek', 'simpsond', 'the_count',
    'and_count', 'is_count', 'of_count', 'in_count', 'to_count', 'it_count', 'that_count',
    'with_count')


admin.site.register(ProcessedFile, ProcessedFileAdmin)
admin.site.register(BoundError, BoundErrorAdmin)
admin.site.register(ArticleStatistics, ArticleStatisticsAdmin)
admin.site.register(SimilarArticlePair, SimilarArticlePairAdmin)
