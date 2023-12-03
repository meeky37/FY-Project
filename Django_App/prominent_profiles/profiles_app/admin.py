# profiles_app/admin.py
from django.contrib import admin
from .models import Entity, Article, BoundMention, OverallSentiment, BingEntity

admin.site.register(Entity)
admin.site.register(Article)
admin.site.register(BoundMention)
admin.site.register(OverallSentiment)
admin.site.register(BingEntity)