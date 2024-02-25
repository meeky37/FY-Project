import concurrent.futures
import json
import os
import queue
import urllib.robotparser
import trafilatura
import spacy
import time
import logging
import urllib.request
import socket

from datetime import datetime
from django.utils import timezone
from django.core.management.base import BaseCommand
from profiles_app.models import Article as ArticleModel
from nlp_processor.models import ProcessedFile
from nlp_processor.utils import DatabaseUtils
from nlp_processor.bing_api import *
from fastcoref import FCoref
from ...article_processor import Article
from django.conf import settings
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser
from ...sentiment_resolver import SentimentAnalyser
# from memory_profiler import profile
# from Django_App.prominent_profiles.nlp_processor.constants import F_COREF_DEVICE


def can_fetch_url(url_to_check):
    """Determine if the URL can be fetched by all crawlers - adding politeness / adherence to
        robot policy."""
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
    # model = FCoref(device='mps')
    model = FCoref(device='cpu')
    predictions = model.predict(texts=article_texts, max_tokens_in_batch=batch_size)

    # Empty list to store clusters for each article
    article_text_clusters = []

    for prediction in predictions:
        clusters_text = prediction.get_clusters()
        clusters_positions = prediction.get_clusters(as_strings=False)
        combined_clusters = [(text, positions, len(text)) for text, positions in
                             zip(clusters_text, clusters_positions)]
        sorted_combined_clusters = sorted(combined_clusters, key=lambda x: x[2], reverse=True)

        article_text_clusters.append(sorted_combined_clusters)

    return article_text_clusters


def check_similarity_with_timeout(article_obj):
    """Wrapper function for check_similarity with a timeout."""
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.submit(article_obj.check_similarity)
        try:
            return future.result(timeout=60)  # Returns True/False based on similarity check
        except concurrent.futures.TimeoutError:
            print("Check Similarity timed out!")
            return False  # If we timeout, assume not too similar


class Command(BaseCommand):
    help = 'Scrape articles and trigger NLP flow'

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)

        self.sa_queue = queue.Queue()

        self.max_concurrent_threads = 2
        # Create 5 SentimentAnalyser objects (these take quite a bit of time to define!)
        # Previously declared for each article object so quite a wasteful operation
        # Queue for the 5 threads
        for _ in range(self.max_concurrent_threads):
            sa = SentimentAnalyser()
            self.sa_queue.put(sa)

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

            # Check if the URL has been seen before in this job
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

                    # datetime aware to a satisfy model
                    publication_date = timezone.make_aware(naive_datetime)

                    # Extract some useful trafilatura metadata.
                    author = metadata.author

                    # 29th Jan Note - this was added over Christmas as an initial "solution" before
                    # a direction to use similarity hashing and statistic linguistics.
                    if ArticleModel.objects.filter(headline=headline, author=author).exists():
                        print('Exact headline and author already exists in db')
                        skips += 1
                        continue

                    site_name = metadata.sitename
                    article_text = trafilatura.extract(downloaded, favour_recall=True,
                                                       include_comments=False, include_images=False,
                                                       include_tables=False)

                    if article_text and len(article_text) > 249:
                        article_obj = Article(url, headline, article_text, ner, publication_date,
                                              author, site_name)

                        start_time = time.time()
                        article_obj.get_statistics()
                        # print(f"Statistics Calculation: {time.time() - start_time} seconds")
                        # About 2 seconds

                        article_obj.save_to_database()

                        start_time = time.time()
                        too_similar = check_similarity_with_timeout(article_obj)
                        print(f"Check Similarity Time: {time.time() - start_time} seconds")

                        if too_similar:
                            article_obj.set_db_processed(is_processed=False, similar_rejection=True)
                            print(f"{article_obj.headline} removed on similarity grounds!")
                        else:
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
                # traceback.print_exc()

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

    def process_article(self, article, sa):

        start_time = time.time()
        article.source_ner_people()
        # print(f"NER People Time: {time.time() - start_time} seconds")

        start_time = time.time()
        article.determine_sentences()
        # print(f"Sentence determined Time: {time.time() - start_time} seconds")

        start_time = time.time()
        article.determine_entity_to_cluster_mapping()
        # print(f"Entity to cluster map time: {time.time() - start_time} seconds")

        start_time = time.time()
        article.entity_cluster_map_consolidation()
        # print(f"Entity cluster map consolidation Time: {time.time() - start_time} seconds")

        time.time()
        if article.database_candidate:
            # article.save_to_database() already done earlier in similar check now

            if article.database_id != -1:
                for entity_data in article.clustered_entities:
                    entity_name = entity_data['Entity Name']
                    entity_db_id = DatabaseUtils.insert_entity(entity_name, article.database_id)
                    entity_data['entity_db_id'] = entity_db_id

                article.set_sentiment_analyser(sa)

                start_time = time.time()
                article.get_bounds_sentiment()
                print(f"Bounds sentiment time: {time.time() - start_time} seconds")

                start_time = time.time()
                article.get_average_sentiment_results()
                # print(f"Average results time: {time.time() - start_time} seconds")
                # < 0.5 seconds

                article.set_db_processed(True, similar_rejection=False)

        elif not article.database_candidate:
            # print("Not enough mentions to add")
            article.set_db_processed(True, similar_rejection=False)
        else:
            print("Article already exists in the database")

        # Save memory by deleting properly!
        # article.reset_attributes()
        del article

    def process_article_wrapper(self, args):
        article, i, total_objects = args
        print(f"Current Progress: {i} of {total_objects}")

        sa = self.sa_queue.get()
        try:
            self.process_article(article, sa)

        finally:
            # Putting the SentimentAnalyser back in the queue, even if exception takes place
            self.sa_queue.put(sa)

    # @profile
    def handle(self, *args, **options):

        logger = logging.getLogger('scrape_articles_logger')
        logger.info(f"Scrape and analyse articles job started at {datetime.now()}")

        media_path = os.path.join(settings.ARTICLE_SCRAPER_MEDIA_ROOT, 'api_articles')

        # Get a list of ProcessedFile objects with nlp_applied=False
        unapplied_files = ProcessedFile.objects.filter(nlp_applied=False)

        processed_urls = set()

        for file in unapplied_files:

            full_path = file.full_path()
            print(full_path)

            # user_input = input("Continue? (y/n): ").lower()
            # if user_input.lower() != 'y':
            #     print("Terminating...")
            #     sys.exit()

            # Check if the file has already been processed
            if full_path not in processed_urls:
                # Retrieve articles from the current file
                articles_from_file = self.process_file(full_path, [], processed_urls)

                print()

                # Extend article_objects with articles from the current file
                article_objects = articles_from_file

                article_texts = [article.text_body for article in article_objects]
                article_text_clusters = perform_coreference_resolution(article_texts)

                for article, clusters in zip(article_objects, article_text_clusters):
                    article.set_coref_clusters(clusters)

                print("Length Article Objects: ")

                total_objects = len(article_objects)
                print(f"Total objects: {total_objects}")
                logging.info(f"Processing {total_objects} article objects")

                with concurrent.futures.ThreadPoolExecutor(
                        max_workers=self.max_concurrent_threads) as executor:
                    list(executor.map(self.process_article_wrapper,
                                      ((article, i + 1, len(article_objects)) for i, article in
                                       enumerate(article_objects))))

                # Update the ProcessedFile object to mark it as processed
                file.nlp_applied = True
                file.save()

        logger.info(f"Scrape and analyse articles job finished at {datetime.now()}")
