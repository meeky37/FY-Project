import json
import os
from datetime import datetime

from django.core.management.base import BaseCommand
from django.conf import settings
from nlp_processor.bing_api import fetch_articles
from nlp_processor.models import ProcessedFile


def save_articles_to_files(self, search_results_list, search_term):
    formatted_search_term = search_term.replace(" ", "+")
    timestamp = datetime.now().strftime("%d-%m-%Y-%H:%M")
    articles_filename = f"{formatted_search_term}_no_dup_articles_loop_{timestamp}.json"
    results_filename = f"{formatted_search_term}_no_dup_results_loop_{timestamp}.json"

    folder_name = formatted_search_term
    folder_path = os.path.join(settings.ARTICLE_SCRAPER_MEDIA_ROOT, 'api_articles', folder_name)
    articles_filepath = os.path.join(folder_path, articles_filename)
    results_filepath = os.path.join(folder_path, results_filename)

    with open(articles_filepath, "w") as articles_file:
        json.dump(self, articles_file, indent=4)

    with open(results_filepath, "w") as results_file:
        json.dump(search_results_list, results_file, indent=4)

    processed_file, created = ProcessedFile.objects.get_or_create(
        search_term=search_term,
        file_name=articles_filename,
        media_path=os.path.join('api_articles', folder_name),
        defaults={'nlp_applied': False}  # Set nlp_applied to False if the entry is created
    )

    processed_file.save()

    print("Articles and search results saved to files in the media/api_articles folder.")


class Command(BaseCommand):
    help = 'Populate media with news article data for use be scrape articles later'

    def handle(self, *args, **options):
        search_term = "keir starmer"
        articles, search_results_list = fetch_articles(search_term)
        save_articles_to_files(articles, search_results_list, search_term)

        search_term = "rishi sunak"
        articles, search_results_list = fetch_articles(search_term)
        save_articles_to_files(articles, search_results_list, search_term)

        search_term = "uk politics"
        articles, search_results_list = fetch_articles(search_term)
        save_articles_to_files(articles, search_results_list, search_term)
