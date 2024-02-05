from datetime import timedelta
from django.shortcuts import get_object_or_404
from django.views import View
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from .models import Entity, BingEntity, OverallSentiment
from nlp_processor.models import SimilarArticlePair
from django.http import Http404


# TODO: Remove unneeded attributes from JSON views.

class VisibleEntitiesView(View):
    def get(self, request, *args, **kwargs):
        visible_entities = Entity.objects.filter(app_visible=True).order_by('name')
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
        return JsonResponse(serialized_entity, safe=False)





class BingEntityMiniView(View):
    def get(self, request, *args, **kwargs):
        entity_id = kwargs.get('entity_id')

        # Check if Entity exists before attempting to fetch BingEntity
        try:
            entity = get_object_or_404(Entity, id=entity_id)

            try:
                bing_entity = BingEntity.objects.get(entity=entity_id)

                serialized_entity = {
                    'id': bing_entity.id,
                    'name': bing_entity.name,
                    'image_url': bing_entity.image_url,
                    'contractual_rules': bing_entity.contractual_rules,
                    'display_hint': bing_entity.entity_type_display_hint
                }
                return JsonResponse(serialized_entity, safe=False)
            except BingEntity.DoesNotExist:
                # BingEntity is not found but Entity exists
                return JsonResponse(
                    {'message': 'Bing entity does not exist - use Google/alternative'}, status=204)

        except Http404:
            # Entity itself does not exist
            return JsonResponse({'error': 'Entity not found'}, status=404)


# TODO EXP and LINEAR could become one function with parameter true/false
class OverallSentimentExp(APIView):
    authentication_classes = [JWTAuthentication]

    def get(self, request, *args, **kwargs):
        entity_id = kwargs.get('entity_id')

        dashboard = request.GET.get('dashboard', 'false').lower() == 'true'
        user = request.user

        print(dashboard)
        print(request.user)
        overall_sentiments = OverallSentiment.objects.filter(entity=entity_id)

        # Apply user-specific filtering if the dashboard flag is true and the user is authenticated
        if dashboard and user.is_authenticated:
            last_visit = user.last_visit_excluding_today or timezone.now()
            overall_sentiments = overall_sentiments.filter(article__publication_date__gt=last_visit)
        else:
            last_visit = None

        if not overall_sentiments.exists() and last_visit is not None:
            response_data = {
                'message': 'No new articles since last visit',
                'lastVisit': last_visit.isoformat(),
                'data': []
            }
            return JsonResponse(response_data, status=200)
        elif not overall_sentiments.exists():
            return JsonResponse({'error': 'No OverallSentiment found for the given entity_id'},
                                status=404)

        has_similar_pair = SimilarArticlePair.objects.filter(
            Q(article2_id__in=[sentiment.article.id for sentiment in overall_sentiments]),
            Q(hash_similarity_score__gte=90) |
            (
                    Q(hash_similarity_score__gte=65, words_diff__lt=10, terms_diff__lt=10,
                      vocd_diff__lt=5, yulek_diff__lt=10, simpsond_diff__lt=10,
                      the_diff__lt=20, and_diff__lt=20, is_diff__lt=20,
                      of_diff__lt=20, in_diff__lt=20, to_diff__lt=20,
                      it_diff__lt=20, that_diff__lt=20, with_diff__lt=20
                      ) & Q(
                article2__article__publication_date__lte=F(
                    'article1__article__publication_date') + timedelta(days=14)
            )
            )
        ).values_list('article2_id', flat=True)

        print(has_similar_pair)

        serialized_entities = []
        for overall_sentiment in overall_sentiments:
            if overall_sentiment.article.id not in has_similar_pair:
                serialized_entity = {
                    'id': overall_sentiment.article.id,
                    'entity_id': overall_sentiment.entity.id,
                    'headline': overall_sentiment.article.headline,
                    'url': overall_sentiment.article.url,
                    'image_url': overall_sentiment.article.image_url,
                    'publication_date': overall_sentiment.article.publication_date.isoformat(),
                    'author': overall_sentiment.article.author,
                    'neutral': overall_sentiment.exp_neutral,
                    'positive': overall_sentiment.exp_positive,
                    'negative': overall_sentiment.exp_negative,
                }
                serialized_entities.append(serialized_entity)
        if last_visit is not None:
            last_visit_str = last_visit.isoformat()
        else:
            last_visit_str = None

        '''Construct response_data with the list of serialized_entities and last_visit so we can
           pass to entity page if a SubProfileCard in Vue is clicked.'''
        response_data = {
            'lastVisit': last_visit_str,
            'data': serialized_entities,
        }

        return JsonResponse(response_data, safe=False)


class OverallSentimentLinear(View):
    authentication_classes = [JWTAuthentication]

    def get(self, request, *args, **kwargs):
        entity_id = kwargs.get('entity_id')

        dashboard = request.GET.get('dashboard', 'false').lower() == 'true'
        user = request.user

        print(dashboard)
        print(request.user)
        overall_sentiments = OverallSentiment.objects.filter(entity=entity_id)

        # Apply user-specific filtering if the dashboard flag is true and the user is authenticated
        if dashboard and user.is_authenticated:
            last_visit = user.last_visit_excluding_today or timezone.now()
            overall_sentiments = overall_sentiments.filter(article__publication_date__gt=last_visit)
        else:
            last_visit = None

        if not overall_sentiments.exists():
            return JsonResponse({'error': 'No OverallSentiment found for the given entity_id'},
                                status=404)

        has_similar_pair = SimilarArticlePair.objects.filter(
            Q(article2_id__in=[sentiment.article.id for sentiment in overall_sentiments]),
            Q(hash_similarity_score__gte=90) |
            (
                    Q(hash_similarity_score__gte=65, words_diff__lt=10, terms_diff__lt=10,
                      vocd_diff__lt=5, yulek_diff__lt=10, simpsond_diff__lt=10,
                      the_diff__lt=20, and_diff__lt=20, is_diff__lt=20,
                      of_diff__lt=20, in_diff__lt=20, to_diff__lt=20,
                      it_diff__lt=20, that_diff__lt=20, with_diff__lt=20
                      ) & Q(
                article2__article__publication_date__lte=F(
                    'article1__article__publication_date') + timedelta(days=14)
            )
            )
        ).values_list('article2_id', flat=True)

        print(has_similar_pair)

        serialized_entities = []
        for overall_sentiment in overall_sentiments:
            if overall_sentiment.article.id not in has_similar_pair:
                serialized_entity = {
                    'id': overall_sentiment.article.id,
                    'entity_id': overall_sentiment.entity.id,
                    'headline': overall_sentiment.article.headline,
                    'url': overall_sentiment.article.url,
                    'image_url': overall_sentiment.article.image_url,
                    'publication_date': overall_sentiment.article.publication_date.isoformat(),
                    'author': overall_sentiment.article.author,
                    'neutral': overall_sentiment.linear_neutral,
                    'positive': overall_sentiment.linear_positive,
                    'negative': overall_sentiment.linear_negative,
                }
                serialized_entities.append(serialized_entity)
        if last_visit is not None:
            last_visit_str = last_visit.isoformat()
        else:
            last_visit_str = None

        '''Construct response_data with the list of serialized_entities and last_visit so we can
           pass to entity page if a SubProfileCard in Vue is clicked.'''
        response_data = {
            'lastVisit': last_visit_str,
            'data': serialized_entities,
        }

        return JsonResponse(response_data, safe=False)


class ArticleOverallSentimentExp(View):
    def get(self, request, *args, **kwargs):
        article_id = kwargs.get('article_id')
        entity_id = kwargs.get('entity_id')

        # Retrieving OverallSentiment objects for given article_id
        overall_sentiments = OverallSentiment.objects.filter(article=article_id)

        # Handle no object found
        if not overall_sentiments.exists():
            return JsonResponse({'error': 'No OverallSentiment found for the given article_id'},
                                status=404)

        # Sort the queryset to prioritize the entry id provided for article detail for that
        # click-thru.
        overall_sentiments = sorted(
            overall_sentiments,
            key=lambda x: x.entity.id != entity_id
        )

        # Serialize each found object
        serialized_entities = []
        for overall_sentiment in overall_sentiments:
            serialized_entity = {
                'id': overall_sentiment.article.id,
                'entity_id': overall_sentiment.entity.id,
                'headline': overall_sentiment.article.headline,
                'url': overall_sentiment.article.url,
                'image_url': overall_sentiment.article.image_url,
                'publication_date': overall_sentiment.article.publication_date,
                'author': overall_sentiment.article.author,
                'neutral': overall_sentiment.exp_neutral,
                'positive': overall_sentiment.exp_positive,
                'negative': overall_sentiment.exp_negative
            }

            serialized_entities.append(serialized_entity)

        return JsonResponse(serialized_entities, safe=False)


# Simple entity request (fall back for bing)
def entity_name(request, entity_id):
    try:
        entity = Entity.objects.get(pk=entity_id)
        name = entity.name
        return JsonResponse({'name': name})
    except Entity.DoesNotExist:
        return JsonResponse({'error': 'Entity not found'}, status=404)


# Using for trending profiles front page
def increment_view_count(request, entity_id):
    entity = get_object_or_404(Entity, id=entity_id)
    entity.view_count += 1
    entity.save()
    return JsonResponse({'message': 'View count incremented successfully'})


def create_entity_view(request, entity_id):
    entity = get_object_or_404(Entity, pk=entity_id)

    EntityView.objects.create(
        entity=entity,
        view_dt=timezone.now().date(),
        view_time=timezone.now().time()
    )

    return JsonResponse({'status': 'success', 'message': 'EntityView record created successfully'})


from django.utils import timezone
from django.http import JsonResponse
from django.db.models import Sum, Count, Q, F
from .models import EntityView


def get_trending_entities(request):
    # Time ranges 1, 3 and 5 days for trending entities homepage
    time_ranges = [24, 72, 120]

    for hours in time_ranges:
        end_time = timezone.now()
        start_time = end_time - timezone.timedelta(hours=hours)

        # Top 7 entities within the time range
        top_entities = EntityView.objects.filter(view_dt__range=(start_time, end_time)) \
                           .values('entity__id', 'entity__name') \
                           .annotate(total_views=Count('entity__id')) \
                           .order_by('-total_views')[:6]

        # Check if there are clear top 6 entities
        if len(top_entities) > 6:
            if top_entities[5]['total_views'] > top_entities[6]['total_views']:
                break  # Found clear top 3 entities

    # If no clear top 6, just return those 6 entities (we tried 3 time periods so this shouldn't
    # occur much)

    data = [{'entity_id': entity['entity__id'], 'entity_name': entity['entity__name'],
             'total_views': entity['total_views']} for entity in top_entities[:6]]

    return JsonResponse({'trending_entities': data})
