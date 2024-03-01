from django.core.management.base import BaseCommand
from django.db import transaction
from profiles_app.models import Entity, SimilarEntityPair, IgnoreEntitySimilarity
from rapidfuzz import fuzz


def get_similar_entities(entities, ignored_entity_pairs, app_visible_entities, threshold):
    """
    Utilise rapid fuzzy matching on pairs that haven't been added to the ignore table.

    :param entities: A queryset or list of `Entity` objects to be compared.
    :param ignored_entity_pairs: A queryset `IgnoreEntitySimilarity` Pairs of entities to be ignored
                                in the similarity check.
    :param app_visible_entities: Entity` objects that when not None limits the scope of entities to
                                 be considered for matching.
    :param threshold: An integer score threshold for considering two entities as similar - an entity
                      pair needs to hit to be stored.
    :return: A list of tuples, where each tuple contains an `Entity` object and a list of tuples,
              each consisting of a similar `Entity` object and their similarity score.
    """

    similar_entities = []

    ignored_pairs = set()

    if ignored_entity_pairs:
        for ignore_relationship in ignored_entity_pairs:
            ignored_pairs.add((ignore_relationship.entity_a, ignore_relationship.entity_b))
            ignored_pairs.add((ignore_relationship.entity_b, ignore_relationship.entity_a))

    if app_visible_entities is not None:
        considered_entities = app_visible_entities
    else:
        considered_entities = entities

    for entity in considered_entities:
        similar_entities_for_current = []
        for other_entity in entities:
            if other_entity != entity and (entity, other_entity) not in ignored_pairs:
                score = fuzz.ratio(entity.name, other_entity.name)
                if score >= threshold:
                    similar_entities_for_current.append((other_entity, score))

        if similar_entities_for_current:
            similar_entities.append((entity, similar_entities_for_current))

    return similar_entities


class Command(BaseCommand):

    def handle(self, *args, **options):
        ignore_entity_pairs = IgnoreEntitySimilarity.objects.all()
        entities = Entity.objects.all()
        app_visible_entities = None  # (consider everything as user isn't waiting now)
        threshold = 65

        similar_entities_tuples = get_similar_entities(entities, ignore_entity_pairs,
                                                       app_visible_entities, threshold)
        # Delete all similar article entity pairs
        SimilarEntityPair.objects.all().delete()
        # Creating SimilarEntityPair records
        with transaction.atomic():
            for entity, similar_entities_for_current in similar_entities_tuples:
                for similar_entity, score in similar_entities_for_current:
                    SimilarEntityPair.objects.create(
                        entity_a=entity,
                        entity_b=similar_entity,
                        similarity_score=score
                    )