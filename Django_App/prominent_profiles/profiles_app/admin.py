# profiles_app/admin.py
from django.contrib import admin
from .models import Entity, Article, BoundMention, OverallSentiment, BingEntity




@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('headline', 'url', 'image_url', 'date_added')


class EntityAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'app_visible', 'article_count')
    list_filter = ('app_visible',)
    ordering = ('name',)


admin.site.register(Entity, EntityAdmin)
admin.site.register(BoundMention)
admin.site.register(OverallSentiment)
admin.site.register(BingEntity)