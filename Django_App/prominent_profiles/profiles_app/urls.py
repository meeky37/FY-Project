from django.urls import path
from .views import VisibleEntitiesView, BingEntityDetailView, OverallSentimentExp, OverallSentimentLinear

urlpatterns = [
    path('entities/', VisibleEntitiesView.as_view(), name='visible_entities'),
    path('bing_entities/<int:entity_id>/', BingEntityDetailView.as_view(), name='bing_entity_detail'),
    path('overall_sentiments/exp/<int:entity_id>/', OverallSentimentExp.as_view(), name='exp_overall'),
    path('overall_sentiments/lin/<int:entity_id>/', OverallSentimentLinear.as_view(), name='lin_overall'),
]
