from datetime import timedelta

from django.contrib import admin
from django.db.models import F
from django.db.models import Case, When, Value
from django.db import models

from .models import ProcessedFile, BoundError, ArticleStatistics, SimilarArticlePair
from django.utils.translation import gettext as _


class ProcessedFileAdmin(admin.ModelAdmin):
    list_display = ['search_term', 'file_name', 'media_path', 'nlp_applied']

    def set_nlp_applied_false(self, request, queryset):
        queryset.update(nlp_applied=False)

    set_nlp_applied_false.short_description = "Set NLP Applied to False for selected items"

    actions = [set_nlp_applied_false]


class DuplicatePrediction(admin.SimpleListFilter):
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
                                'article1__article__publication_date') + timedelta(days=14),
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
    list_display = ['id', 'article1', 'article2', 'hash_similarity_score', 'words_diff',
                    'terms_diff',
                    'yulek_diff', 'avg_count_diff', 'simpsond_diff', 'the_diff', 'and_diff',
                    'is_diff', 'of_diff', 'in_diff', 'to_diff', 'it_diff', 'that_diff',
                    'with_diff']
    list_filter = [DuplicatePrediction]
    search_fields = ['article1__article__id', 'article2__article__id']


class BoundErrorAdmin(admin.ModelAdmin):
    list_display = ('article', 'bound_start', 'bound_end', 'left_segment', 'mention_segment',
                    'right_segment', 'error_message', 'timestamp')


admin.site.register(ProcessedFile, ProcessedFileAdmin)
admin.site.register(BoundError, BoundErrorAdmin)
admin.site.register(ArticleStatistics)
admin.site.register(SimilarArticlePair, SimilarArticlePairAdmin)
