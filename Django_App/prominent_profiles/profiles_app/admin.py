# profiles_app/admin.py
from django.contrib import admin
from .models import Entity, Article, BoundMention, OverallSentiment

admin.site.register(Entity)
admin.site.register(Article)
admin.site.register(BoundMention)
admin.site.register(OverallSentiment)