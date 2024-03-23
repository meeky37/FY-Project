"""
This module defines Celery tasks for asynchronously handling data processing operations.

Each task invokes a corresponding Django management command to carry out its operation,
leveraging Celery's asynchronous task execution capabilities.

Now I don't have to run these manually, resulting in no forgotten days and resource heavy sentiment
analysis taking place while I am sleeping or out-out.
"""

from celery import shared_task
from django.core.management import call_command


@shared_task
def collect_article_data():
    """
    Get fresh article data from Bing API
    """
    call_command('collect_article_data')


@shared_task
def scrape_articles_concurrent():
    """
    Get unprocessed Bing api files, trafilatura, and run NLP analysis.
    """
    call_command('scrape_articles_concurrent')


@shared_task
def visible_entity_bing():
    """
    Checks if any entities are set to visible but lacking wiki description and photo
    (From bing api)
    """
    call_command('visible_entity_bing')


@shared_task
def hello_celery():
    print('Celery says HELLO!')

    return
