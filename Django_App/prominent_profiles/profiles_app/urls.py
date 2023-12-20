from django.urls import path
from .views import (VisibleEntitiesView, BingEntityDetailView,
                    BingEntityMiniView, OverallSentimentExp,
                    OverallSentimentLinear, ArticleOverallSentimentExp)

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
]
