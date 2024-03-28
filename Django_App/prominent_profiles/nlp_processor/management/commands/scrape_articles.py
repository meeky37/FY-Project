import json
import os
import socket
import time
import urllib.request
import urllib.robotparser
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser

import spacy
import trafilatura
from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone
from fastcoref import FCoref
from nlp_processor.bing_api import *
from nlp_processor.models import ProcessedFile
from nlp_processor.utils import DatabaseUtils
from profiles_app.models import Article as ArticleModel

from Django_App.prominent_profiles.nlp_processor.article_processor import Article

"""This is a legacy django command designed to scrape articles, perform NLP analysis, 
and populate the database with processed data. It is a relatively early version of article 
processing that is more closely tied to the Jupyter Notebooks used to experiment and devise the
logic for PP.

It lacks the multithreading capability, has less error handling at various failure points, 
uses hardcoded values, and its process for identifying / handling duplicate articles is overly 
simplistic compared to the newer scrape_articles_concurrent.py - this file is retained for the 
evolution of my project.
"""


def can_fetch_url(url_to_check):
    """
    Determine if an article URL can be fetched by all crawlers - adding politeness / adherence to
    robot policy.

    :param url_to_check:
    :return: true or false depending on publisher urls policy
    """

    # print("robo check started")
    parsed_url = urlparse(url_to_check)
    base_url = parsed_url.scheme + "://" + parsed_url.netloc

    rules = RobotFileParser()
    try:
        with urllib.request.urlopen(base_url + "/robots.txt", timeout=5) as response:
            rules.parse(response.read().decode('utf-8').splitlines())
        # print("robo check done")
        return rules.can_fetch("*", url_to_check)
    except urllib.error.URLError as e:
        print(f"Error accessing robots.txt: {e}")
    except socket.timeout as e:
        print(f"Timeout occurred: {e}")

    # Default to False as if Robot can't be checked then not compliant + the site may timeout.
    return False


def perform_coreference_resolution(article_texts, batch_size=100):
    """
    Performs coreference resolution on a batch of article texts using the FCoref model. This function
    processes the provided texts to identify coreferences which is key to finding all
    sentences/bounds of an entity and their alternative mentions.

    e.g. ['Keir Starmer', 'Starmer', 'Keir Starmer', 'him', 'Sir Keir', 'the Labour leader',
    'Keir Starmer (left)', 'him', 'the Labour leader', "Sir Keir Starmer's", 'Starmer', 'Sir Keir',
     'the Labour leader', 'Keir', 'Sir Keir', 'Sir Keir']

    :param article_texts: A list of strings, where each string is the text of an article on which
                          coreference resolution is to be performed.

    :param batch_size: An integer specifying the maximum number of tokens to process in a single batch.
                       This helps manage memory usage and computational load, especially for large texts.

    :return: A list of lists, where each sublist contains tuples of (text, positions, length) for each
             cluster identified in the corresponding article text. The clusters are sorted by the length
             of their text in descending order, later insignificant, small clusters will be
             removed.
    """
    # Non-dynamic batch size fixed in scrape_articles_concurrent job.
    model = FCoref(device='mps')

    predictions = model.predict(texts=article_texts, max_tokens_in_batch=batch_size)

    # Empty list to store clusters for each article
    article_text_clusters = []

    for prediction in predictions:
        clusters_text = prediction.get_clusters()
        clusters_positions = prediction.get_clusters(as_strings=False)
        combined_clusters = [(text, positions, len(text)) for text, positions in zip
        (clusters_text, clusters_positions)]
        sorted_combined_clusters = sorted(combined_clusters, key=lambda x: x[2], reverse=True)

        article_text_clusters.append(sorted_combined_clusters)

    return article_text_clusters


class Command(BaseCommand):
    help = 'Scrape articles and trigger NLP flow'

    def process_articles(articles, article_objects, processed_urls, start=0, end=None):

        ner = spacy.load("en_core_web_sm")

        fetches = 0
        skips = 0
        too_short = 0
        if end is None:
            end = len(articles)

        for article in articles[start:end]:
            url = article["url"]
            headline = article["title"]

            # Check if the URL has been seen before
            if url in processed_urls:
                print('url seen before')
                skips += 1
                continue  # Skip this article

            # Check if the URL already exists in the database
            if ArticleModel.objects.filter(url=url).exists():
                print('Article URL already exists in db')
                skips += 1
                continue

            try:
                if can_fetch_url(url):
                    fetches += 1
                    downloaded = trafilatura.fetch_url(url)
                    # Extract metadata
                    metadata = trafilatura.extract_metadata(downloaded)
                    # print(metadata.date)

                    # Extract publication date
                    date_str = metadata.date
                    naive_datetime = datetime.strptime(date_str, '%Y-%m-%d')

                    publication_date = timezone.make_aware(naive_datetime)  # datetime aware to a
                    # satisfy model

                    # Extract some useful trafilatura metadata.
                    author = metadata.author

                    if ArticleModel.objects.filter(headline=headline, author=author).exists():
                        print('Exact headline and author already exists in db')
                        skips += 1
                        continue

                    site_name = metadata.sitename
                    article_text = trafilatura.extract(downloaded, favour_recall=True,
                                                       include_comments=False, include_images=False,
                                                       include_tables=False)
                    # article_text = trafilatura.extract(downloaded, favour_recall=True)
                    if article_text and len(article_text) > 249:
                        article_obj = Article(url, headline, article_text, ner,
                                              publication_date, author, site_name)
                        article_objects.append(article_obj)
                        # Mark the URL as processed
                        processed_urls.add(url)
                    elif article_text is None:
                        print('article text is None')
                    elif len(article_text) < 250:
                        print(article_text)
                        too_short += 1

            except Exception as e:
                print(f"Error processing article: {url}")
                print(f"Error message: {str(e)}")

        print("Fetches:")
        print(fetches)

        print("Skips:")
        print(skips)

        print("Too short count <250:")
        print(too_short)

        print("Article Objects length...")
        print(len(article_objects))
        return article_objects

    def process_file(self, file_name, article_objects, processed_urls):
        directory_path = "Daily_Results"
        file_path = os.path.join(file_name)

        with open(file_path, "r") as articles_file:
            articles = json.load(articles_file)

        return Command.process_articles(articles, article_objects, processed_urls)

    def handle(self, *args, **options):

        processed_urls = set()
        article_objects = []

        media_path = os.path.join(settings.ARTICLE_SCRAPER_MEDIA_ROOT, 'api_articles')

        # Originally had to specify manual file paths.

        # file_name_1 = "keir+starmer_no_dup_articles_loop_17-11-2023-18:44.json"
        # media_path_1 = os.path.join(media_path, 'keir+starmer', file_name_1)
        # full_path_1 = os.path.join(settings.BASE_DIR, 'nlp_processor', media_path_1)
        # article_objects = self.process_file(full_path_1, article_objects, processed_urls)
        #
        # file_name_2 = "rishi+sunak_no_dup_articles_loop_17-11-2023-18:46.json"
        # media_path_2 = os.path.join(media_path, 'rishi+sunak', file_name_2)
        # full_path_2 = os.path.join(settings.BASE_DIR, 'nlp_processor', media_path_2)
        # # article_objects.extend(self.process_file(full_path_2, article_objects, processed_urls))
        #
        # file_name_3 = "uk+politics_no_dup_articles_loop_17-11-2023-19:26.json"
        # media_path_3 = os.path.join(media_path, 'uk+politics', file_name_3)
        # full_path_3 = os.path.join(settings.BASE_DIR, 'nlp_processor', media_path_3)
        # # article_objects.extend(self.process_file(full_path_3, article_objects, processed_urls))

        # Get a list of ProcessedFile objects with nlp_applied=False
        unapplied_files = ProcessedFile.objects.filter(nlp_applied=False)

        processed_urls = set()

        for file in unapplied_files:

            article_objects = []

            full_path = file.full_path()

            print(full_path)

            # Check if the file has already been processed
            if full_path not in processed_urls:
                # Retrieve articles from the current file
                articles_from_file = self.process_file(full_path, [], processed_urls)
                # Extend article_objects with articles from the current file
                article_objects = articles_from_file

                article_texts = [article.text_body for article in article_objects]
                article_text_clusters = perform_coreference_resolution(article_texts)

                for article, clusters in zip(article_objects, article_text_clusters):
                    article.set_coref_clusters(clusters)

                print("Length Article Objects: ")

                total_objects = len(article_objects)
                print(f"Total objects: {total_objects}")

                i = 1

                for article in article_objects:
                    print(f"Current Progress: {i} of {total_objects}")
                    i += 1

                    start_time = time.time()
                    article.source_ner_people()
                    print(f"NER People Time: {time.time() - start_time} seconds")

                    start_time = time.time()
                    article.determine_sentences()
                    print(f"Sentence determined Time: {time.time() - start_time} seconds")

                    start_time = time.time()
                    article.determine_entity_to_cluster_mapping()
                    print(f"Entity to cluster map time: {time.time() - start_time} seconds")

                    start_time = time.time()
                    article.entity_cluster_map_consolidation()
                    print(
                        f"Entity cluster map consolidation Time: {time.time() - start_time} seconds")
                    start_time = time.time()

                    if article.database_candidate:
                        article.save_to_database()

                        if article.database_id != -1:
                            for entity_data in article.clustered_entities:
                                entity_name = entity_data['Entity Name']
                                entity_db_id = DatabaseUtils.insert_entity(entity_name,
                                                                           article.database_id)
                                # print(entity_db_id)

                                """This turned out to be a very quick way to hit my free 1000 bing 
                                api quota! Visible Entity Bing in bing_api.py replaced this 
                                approach."""

                                # if not entity_db_id_exists_in_bing(entity_db_id):
                                #     bing_entity_info = get_bing_entity_info(entity_name)
                                #     if bing_entity_info:
                                #         # Insert into the bing_entity_info table
                                #         insert_into_bing_entity_table(entity_db_id, bing_entity_info)
                                # else:
                                #     bing_entity_pending = BingEntityPending.objects.filter(entity_id=entity_db_id).first()
                                #
                                #     if not bing_entity_pending:
                                #         # If not, add to the BingEntityPending table
                                #         BingEntityPending.objects.create(entity_id=entity_db_id, entity_name=entity_name)

                                entity_data['entity_db_id'] = entity_db_id

                            start_time = time.time()
                            print(f"Entity insert time: {time.time() - start_time} seconds")

                            start_time = time.time()
                            article.set_sentiment_analyser()
                            print(
                                f"Sentiment analyser setup time: {time.time() - start_time} seconds")

                            start_time = time.time()
                            article.get_bounds_sentiment()
                            print(f"Bounds sentiment time: {time.time() - start_time} seconds")

                            start_time = time.time()
                            article.get_average_sentiment_results()
                            print(f"Average results time: {time.time() - start_time} seconds")

                    elif not article.database_candidate:
                        print("Not enough mentions to add")
                    else:
                        print("Article already exists in the database")
                    article.reset_attributes()

                # Update the ProcessedFile object to mark it as processed
                file.nlp_applied = True
                file.save()
