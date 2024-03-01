"""
Key Module Functionality:
Defines key URL patterns for Vue app to get entity, trending entities, bing entities, and overall
sentiments views from the database.

Further comments for each view are in profiles_app/views.py.
"""

from django.urls import path
from .views import (VisibleEntitiesView, BingEntityDetailView,
                    BingEntityMiniView, OverallSentimentExp,
                    OverallSentimentLinear, ArticleOverallSentimentExp, entity_name,
                    increment_view_count, create_entity_view, get_trending_entities)

urlpatterns = [
    path('entities/', VisibleEntitiesView.as_view(), name='visible_entities'),
    path('bing_entities/<int:entity_id>/', BingEntityDetailView.as_view(), name='bing_entity_detail'),
    path('bing_entities/mini/<int:entity_id>/', BingEntityMiniView.as_view(),
         name='bing_entity_mini'),
    path('overall_sentiments/exp/<int:entity_id>/', OverallSentimentExp.as_view(), name='exp_overall'),
    path('overall_sentiments/lin/<int:entity_id>/', OverallSentimentLinear.as_view(), name='lin_overall'),
    path('overall_sentiments/exp/article/<int:entity_id>/<int:article_id>/',
         ArticleOverallSentimentExp.as_view(),
         name='exp_article_overall'),
    path('entity_name/<int:entity_id>/', entity_name, name='entity_name'),
    path('increment_view_count/<int:entity_id>/', increment_view_count,
         name='increment_view_count'),
    path('create_entity_view/<int:entity_id>/', create_entity_view,
         name='create_entity_view'),
    path('get_trending_entities/', get_trending_entities, name='get_trending_entities'),
]
