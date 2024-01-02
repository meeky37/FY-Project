# profiles_app/admin.py
from django.contrib import admin
from django.db.models import Count

from .models import Entity, Article, BoundMention, OverallSentiment, BingEntity


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('headline', 'url', 'image_url', 'date_added', 'publication_date',
                    'site_name', 'author')


class EntityAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'app_visible', 'view_count', 'display_article_count_numeric')
    list_filter = ('app_visible', )
    ordering = ('-overallsentiment__count',)  # '-' for high to low on mention count
    list_per_page = 1000


    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(overallsentiment__count=Count('overallsentiment__id'))
        return queryset

    def display_article_count_numeric(self, obj):
        return obj.overallsentiment__count

    display_article_count_numeric.short_description = 'Article Count (Numeric)'

    def merge_entities(self, request, queryset):
        queryset = queryset.annotate(article_count_numeric=Count('overallsentiment'))
        if queryset.count() == 2:
            master_entity = queryset.first()
            secondary_entity = queryset.last()

            # Update references
            BoundMention.objects.filter(entity=secondary_entity).update(entity=master_entity)
            OverallSentiment.objects.filter(entity=secondary_entity).update(entity=master_entity)
            BingEntity.objects.filter(entity=secondary_entity).update(entity=master_entity)

            # Additional merge logic for Entity model
            master_entity.name = f"{master_entity.name}"
            master_entity.type = master_entity.type or secondary_entity.type
            master_entity.app_visible = master_entity.app_visible or secondary_entity.app_visible

            # Save the changes to the Master entity
            master_entity.save()

            # Delete the secondary entity
            secondary_entity.delete()

            self.message_user(request, "Entities merged successfully.", level='INFO')

        else:
            self.message_user(request, "Please select exactly two entities for merging.",
                                    level='ERROR')


    def reset_view_count(self, request, queryset):
        queryset = queryset.order_by('id')
        queryset.update(view_count=0)

    def make_app_visible(self, request, queryset):
        queryset = queryset.order_by('id')
        queryset.update(app_visible=True)

    make_app_visible.short_description = "Mark selected entities as app visible"


    merge_entities.short_description = "Merge SELECT Primary (keeping) FIRST then Secondary (deleting)"
    make_app_visible.short_description = 'Make App Visible'
    reset_view_count.short_description = 'Reset View Count'

    actions = [merge_entities, make_app_visible,  reset_view_count]

admin.site.register(Entity, EntityAdmin)

class BingEntityAdmin(admin.ModelAdmin):
    list_display = ('id', 'entity', 'name', 'description', 'image_url', 'web_search_url', 'bing_id',
                    'contractual_rules', 'entity_type_display_hint', 'entity_type_hints', 'date_added')


admin.site.register(BingEntity, BingEntityAdmin)
admin.site.register(BoundMention)
admin.site.register(OverallSentiment)

