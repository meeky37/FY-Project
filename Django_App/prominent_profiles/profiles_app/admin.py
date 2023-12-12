# profiles_app/admin.py
from django.contrib import admin
from .models import Entity, Article, BoundMention, OverallSentiment, BingEntity

def merge_entities(modeladmin, request, queryset):
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

        modeladmin.message_user(request, "Entities merged successfully.", level='INFO')

    else:
        modeladmin.message_user(request, "Please select exactly two entities for merging.", level='ERROR')

merge_entities.short_description = "Merge SELECT Primary (keeping) FIRST then Secondary (deleting)"

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('headline', 'url', 'image_url', 'date_added')


class EntityAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'app_visible', 'article_count')
    list_filter = ('app_visible',)
    ordering = ('name',)
    actions = [merge_entities]


class BingEntityAdmin(admin.ModelAdmin):
    list_display = ('id', 'entity', 'name', 'description', 'image_url', 'web_search_url', 'bing_id', 'contractual_rules', 'entity_type_display_hint', 'entity_type_hints', 'date_added')


admin.site.register(BingEntity, BingEntityAdmin)




admin.site.register(Entity, EntityAdmin)
admin.site.register(BoundMention)
admin.site.register(OverallSentiment)

