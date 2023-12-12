

from django.urls import path
from .views import VisibleEntitiesView, BingEntityDetailView

urlpatterns = [
    path('entities/', VisibleEntitiesView.as_view(), name='visible_entities'),
    path('bing_entities/<int:entity_id>/', BingEntityDetailView.as_view(), name='bing_entity_detail'),
]