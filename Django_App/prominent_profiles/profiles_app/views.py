from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views import View
from .models import Entity, BingEntity, OverallSentiment, Article

# TODO: Remove unneeded attributes from JSON views.

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


from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import OverallSentiment, Article

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import OverallSentiment, Article


class OverallSentimentExp(View):
    def get(self, request, *args, **kwargs):
        entity_id = kwargs.get('entity_id')

        # Retrieve a queryset of OverallSentiment objects for the given entity_id
        overall_sentiments = OverallSentiment.objects.filter(entity=entity_id)

        # Handle the case where no object is found
        if not overall_sentiments.exists():
            return JsonResponse({'error': 'No OverallSentiment found for the given entity_id'},
                                status=404)

        # If one or more objects are found, serialize each object
        serialized_entities = []
        for overall_sentiment in overall_sentiments:
            # Assuming 'article' is the ForeignKey field in OverallSentiment
            article = get_object_or_404(Article, id=overall_sentiment.article.id)

            serialized_entity = {
                'id': article.id,
                'headline': article.headline,
                'url': article.url,
                'image_url': article.image_url,
                'neutral': overall_sentiment.exp_neutral,
                'positive': overall_sentiment.exp_positive,
                'negative': overall_sentiment.exp_negative
            }

            serialized_entities.append(serialized_entity)

        return JsonResponse(serialized_entities, safe=False)


class OverallSentimentLinear(View):

    def get(self, request, *args, **kwargs):
        entity_id = kwargs.get('entity_id')

        # Retrieve a queryset of OverallSentiment objects for the given entity_id
        overall_sentiments = OverallSentiment.objects.filter(entity=entity_id)

        # Handle the case where no object is found
        if not overall_sentiments.exists():
            return JsonResponse({'error': 'No OverallSentiment found for the given entity_id'},
                                status=404)

        # If one or more objects are found, serialize each object
        serialized_entities = []
        for overall_sentiment in overall_sentiments:
            # Assuming 'article' is the ForeignKey field in OverallSentiment
            article = get_object_or_404(Article, id=overall_sentiment.article.id)


            serialized_entity = {
                'id': article.id,
                'headline': article.headline,
                'url': article.url,
                'image_url': article.image_url,
                'neutral': overall_sentiment.exp_neutral,
                'positive': overall_sentiment.exp_positive,
                'negative': overall_sentiment.exp_negative
            }

            serialized_entities.append(serialized_entity)

        return JsonResponse(serialized_entities, safe=False)
