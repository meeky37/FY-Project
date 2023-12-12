from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views import View
from .models import Entity, BingEntity

class VisibleEntitiesView(View):
    def get(self, request, *args, **kwargs):
        visible_entities = Entity.objects.filter(app_visible=True)
        serialized_entities = [
            {'id': entity.id, 'name': entity.name}
            for entity in visible_entities
        ]
        return JsonResponse(serialized_entities, safe=False)

class BingEntityDetailView(View):
    def get(self, request, *args, **kwargs):
        entity_id = kwargs.get('entity_id')
        bing_entity = get_object_or_404(BingEntity, entity=entity_id)

        serialized_entity = {
            'id': bing_entity.id,
            'name': bing_entity.name,
            'description': bing_entity.description,
            'image_url': bing_entity.image_url,
            'web_search_url': bing_entity.web_search_url,
            'bing_id': bing_entity.bing_id,
            'contractual_rules': bing_entity.contractual_rules,
            'entity_type_display_hint': bing_entity.entity_type_display_hint,
            'entity_type_hints': bing_entity.entity_type_hints,
            'date_added': bing_entity.date_added
        }

        # serialized_entity = {
        #     'id': bing_entity.id,
        #     'description': bing_entity.description,
        #     'image_url': bing_entity.image_url,
        # }

        return JsonResponse(serialized_entity, safe=False)
