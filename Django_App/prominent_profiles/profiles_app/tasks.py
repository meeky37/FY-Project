from celery import shared_task
from django.core.management import call_command


@shared_task
def collect_article_data():
    """
    Drop and recreate the SimilarEntityPairs table
    e.g. because entities have been manually changed or articles have been loaded (so recommended
    at least once a day).
    """
    call_command('similar_entity_pairs_update')