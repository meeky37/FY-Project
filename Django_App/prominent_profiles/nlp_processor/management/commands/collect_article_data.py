import json
import os
from datetime import datetime

from django.core.mail import send_mail
from django.core.management.base import BaseCommand
from django.conf import settings
from nlp_processor.bing_api import fetch_articles
from nlp_processor.models import ProcessedFile


def save_articles_to_files(self, search_results_list, search_term):
    """

    :param self:
    :param search_results_list: A list of dictionaries, where each dictionary represents the raw
                                search results from the scraping operation.
    :param search_term: The search term used to fetch the articles, which also influences the
                        naming convention of the saved files and their directory.
    :return:
    """
    formatted_search_term = search_term.replace(" ", "+")
    timestamp = datetime.now().strftime("%d-%m-%Y-%H:%M")
    articles_filename = f"{formatted_search_term}_no_dup_articles_loop_{timestamp}.json"
    results_filename = f"{formatted_search_term}_no_dup_results_loop_{timestamp}.json"

    folder_name = formatted_search_term
    folder_path = os.path.join(settings.ARTICLE_SCRAPER_MEDIA_ROOT, 'api_articles', folder_name)

    # Create the folder if it doesn't exist - e.g. added 'general election' 19th Jan will need folder
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

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
        defaults={'nlp_applied': False}  # Set nlp_applied to false - article scrape/NLP job will
        # handle setting this to true later
    )

    processed_file.save()

    print(f"Articles and search results saved to files in the media/api_articles/{folder_name}")


class Command(BaseCommand):
    """
    A Django management command to fetch news articles data using the Bing News API and store them
    in JSON format.

    This command automates the process of fetching articles for multiple predefined search terms
    and organising the data within the project's media directory.

    It populates the media with fresh article data for subsequent processing.
    The command handles the execution of fetching and saving operations for each search term sequentially.
    """

    help = 'Populate media with news article data for use be scrape articles later'

    send_mail(
        'Bing News API Job Started',
        'Collect article data from Bing News API has started.',
        settings.EMAIL_HOST_USER,
        [settings.EMAIL_HOST_USER],
        fail_silently=True,
    )

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

        search_term = "prince harry"
        articles, search_results_list = fetch_articles(search_term)
        save_articles_to_files(articles, search_results_list, search_term)

        search_term = "meghan markle"
        articles, search_results_list = fetch_articles(search_term)
        save_articles_to_files(articles, search_results_list, search_term)

        #  19th Jan add general election
        search_term = "general election"
        articles, search_results_list = fetch_articles(search_term)
        save_articles_to_files(articles, search_results_list, search_term)

        #  23th Jan add individual political parties...
        search_term = "SNP"
        articles, search_results_list = fetch_articles(search_term)
        save_articles_to_files(articles, search_results_list, search_term)

        search_term = "Labour"
        articles, search_results_list = fetch_articles(search_term)
        save_articles_to_files(articles, search_results_list, search_term)

        search_term = "Conservatives"
        articles, search_results_list = fetch_articles(search_term)
        save_articles_to_files(articles, search_results_list, search_term)

        search_term = "Liberal Democrats"
        articles, search_results_list = fetch_articles(search_term)
        save_articles_to_files(articles, search_results_list, search_term)

        search_term = "Green Party"
        articles, search_results_list = fetch_articles(search_term)
        save_articles_to_files(articles, search_results_list, search_term)

        search_term = "Reform"
        articles, search_results_list = fetch_articles(search_term)
        save_articles_to_files(articles, search_results_list, search_term)

    send_mail(
        'Bing News API Job Finished',
        'Collect article data from Bing News API has finished.',
        settings.EMAIL_HOST_USER,
        [settings.EMAIL_HOST_USER],
        fail_silently=True,
    )
