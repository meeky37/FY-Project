from celery import shared_task
from django.core.management import call_command


@shared_task
def similar_entity_pairs_update():
    """
    Drop and recreate the SimilarEntityPair table
    e.g. because entities have been manually changed or articles have been loaded (so recommended
    at least once a day scheduling).
    """
    call_command('similar_entity_pairs_update')
