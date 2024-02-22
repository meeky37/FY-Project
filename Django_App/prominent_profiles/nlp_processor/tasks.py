from celery import shared_task
from django.core.management import call_command

@shared_task
def collect_article_data():
    """
    Get fresh article data from bing API
    """
    call_command('collect_article_data')


@shared_task
def scrape_articles_concurrent():
    """
    Get unprocessed bing api files, trafilatura and run NLP analysis.
    """
    call_command('scrape_articles_concurrent')


@shared_task
def visible_entity_bing():
    """
    Checks if any entities are set to visible but lacking wiki description and photo
    (From bing api)
    """
    call_command('scrape_articles_concurrent')

@shared_task
def hello_celery():
    print('Celery says HELLO!')

    return