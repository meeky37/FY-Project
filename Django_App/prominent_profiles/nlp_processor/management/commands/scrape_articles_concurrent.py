import concurrent.futures
import json
import logging
import os
import queue
import socket
import time
import urllib.request
import urllib.robotparser
from datetime import datetime
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser

import spacy
import trafilatura
from django.core.mail import send_mail
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.conf import settings
from fastcoref import FCoref
from nlp_processor.bing_api import *
from nlp_processor.models import ProcessedFile
from nlp_processor.utils import DatabaseUtils
from profiles_app.models import Article as ArticleModel

from ...article_processor import Article
from ...constants import (ARTICLE_CHUNK_SIZE, ARTICLE_BATCH_SIZE, ARTICLE_THREADS,
                          F_COREF_DEVICE, SIMILARITY_TIMEOUT)
from ...sentiment_resolver import SentimentAnalyser




# Memory Profiling to establish resource requirements, make improvements like deleting article
# instances where possible.
# from memory_profiler import profile
# from Django_App.prominent_profiles.nlp_processor.constants import F_COREF_DEVICE


def can_fetch_url(url_to_check):
    """
    Determine if an article URL can be fetched by all crawlers - adding politeness / adherence to
    robot policy.

    :param url_to_check:
    :return: true or false depending on publisher urls policy
    """

    parsed_url = urlparse(url_to_check)
    base_url = parsed_url.scheme + "://" + parsed_url.netloc

    rules = RobotFileParser()
    try:
        with urllib.request.urlopen(base_url + "/robots.txt", timeout=5) as response:
            rules.parse(response.read().decode('utf-8').splitlines())
        return rules.can_fetch("*", url_to_check)
    except urllib.error.URLError as e:
        print(f"Error accessing robots.txt: {e}")
    except socket.timeout as e:
        print(f"Timeout occurred: {e}")

    # Default to False as if Robot can't be checked then not compliant + the site may timeout.
    return False


def perform_coreference_resolution(article_texts, batch_size=ARTICLE_BATCH_SIZE):
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

     Batch size is controlled centrally by a constant.py entry now.
    """

    model = FCoref(device=F_COREF_DEVICE)
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
    """
    Executes the similarity check for an article object within a specified timeout period. If the
    operation does not complete within the timeout, it is aborted, and the function returns False.

    My thinking is if it is taking more than e.g. 60 seconds then take the risk of it being a
    duplicate in return for less disruption to the pipeline.

    :param article_obj: An instance of the Article class, holding the article to check for similarity.
    :return: bool: True if the article is considered similar to others based on predefined criteria,
             False if not similar or check not completed within the timeout period.
    """
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.submit(article_obj.check_similarity)
        try:
            # Returns True/False based on similarity check
            return future.result(timeout=SIMILARITY_TIMEOUT)
        except concurrent.futures.TimeoutError:
            print("Check Similarity timed out!")
            return False  # If we timeout, assume not too similar


class Command(BaseCommand):
    """
    A Django management command intended to scrape articles, process them for NLP tasks including
    coreference resolution, sentiment analysis, and similarity checking, and then update the
    database to confirm successful completion*.

    This command handles the full workflow from fetching unprocessed article data, applying NLP
    processing, and then marking articles as processed since we don't want to store article texts for
    legal/terms of service/storage reasons etc. it makes sense to have this as one end-to-end job
    that can be run regularly 12 or 24 increments following Bing News Api calls.

    If processed file fails and is not set to true e.g. the job is interrupted it will
    conveniently be picked up on the next job get_or_create has been used across the NLP Processor
    code to avoid breaking unique keys.
    """
    help = 'Scrape articles and trigger NLP flow'

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)

        self.sa_queue = queue.Queue()

        self.max_concurrent_threads = ARTICLE_THREADS
        # Create 5 SentimentAnalyser objects (these take quite a bit of time to define!)
        # Previously declared for each article object so quite a wasteful operation
        # Queue for the 5 threads
        for _ in range(self.max_concurrent_threads):
            sa = SentimentAnalyser()
            self.sa_queue.put(sa)

    def process_articles(self, source_file_id, articles, article_objects, processed_urls, ner,
                         start=0,
                         end=None):
        """
        Processes a list of articles by downloading their content (if permitted by robots.txt),
        uses statistic analysis methods (article_update.py), and updating the database with the
        results. It can then filter out articles based on duplication and length criteria.

        :param source_file_id: The ID of the source file from which the articles are derived.
        :param articles: A list of article metadata (such as URLs and titles) to process.
        :param article_objects: A list to which newly created and processed Article objects will be added.
        :param processed_urls: A set containing URLs of articles that have already been processed
                                in this job to avoid duplication (first line defence).
        :param ner: The named entity recognition model to use for processing articles.
        :param start: The starting index in the articles list from which to begin processing.
        :param end: The ending index in the articles list up to which to process. If None, processes all articles from start.
        :return: A list of Article objects that have been processed.
        """

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
            existing_article = ArticleModel.objects.filter(url=url).first()
            if existing_article:
                if existing_article.processed:
                    print('Article URL already exists in db and has been processed already')
                    skips += 1
                    continue  # Skip this article as it's already processed
                else:
                    print('Article URL already exists in db BUT has not been processed')
                    # Added to handle crash during a sentiment job on the first occasion.

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
                    if ArticleModel.objects.filter(headline=headline, author=author,
                                                   processed=True).exists():
                        print('Exact headline and author already exists in db and has been '
                              'processed')
                        skips += 1
                        continue

                    site_name = metadata.sitename
                    article_text = trafilatura.extract(downloaded, favour_recall=True,
                                                       include_comments=False, include_images=False,
                                                       include_tables=False)

                    if article_text and len(article_text) > 249:
                        source_file = ProcessedFile.objects.get(id=source_file_id)

                        article_obj = Article(url, headline, article_text, ner, publication_date,
                                              author, site_name, source_file)

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
                            article_obj.text_body = None  # Free memory explicitly
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

    def process_file(self, source_file_id, file_name, start, end, processed_urls, ner):
        """
        Processes a specified range of articles within a source file.
        Articles are read from a JSON file and then sent for download.

        Start and end filtering was useful for debugging e.g. running with just 2 or 3 articles
        quickly

        :param source_file_id: The ID of the source file containing the articles.
        :param file_name: The path to the file containing article data in JSON format.
        :param start: The index of the first article to process.
        :param end: The index of the last article to process.
        :param processed_urls: A set containing URLs of articles that have already been processed
                                in this job to avoid duplication (first line defence).
        :param ner: The spacy named entity recognition (NER) model used for processing articles.
        :return: A list of processed Article objects.
        """
        article_objects = []
        file_path = os.path.join(file_name)

        with open(file_path, "r") as articles_file:
            articles = json.load(articles_file)

        articles_subset = articles[start:end]

        return self.process_articles(source_file_id, articles_subset, article_objects,
                                     processed_urls,
                                     ner=ner)

    def process_article(self, article, sa):
        """
        Applies NLP processing on a single article, including named entity recognition, sentiment
        analysis, and updating the database with the analysis results.

        :param article: An instance of the Article class to be processed.
        :param sa: An instance of the SentimentAnalyser class from the queue used to perform
        sentiment analysis on the article.
        """

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
        if article.sentiment_candidate:
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

        elif not article.sentiment_candidate:
            # print("Not enough mentions to add")
            article.set_db_processed(True, similar_rejection=False)
        else:
            print("Article already exists in the database")

        # Saved memory instead by deleting whole object properly!
        # article.reset_attributes()
        del article

    def process_article_wrapper(self, args):
        """
        A wrapper function designed to process an individual article within a concurrent env.
        It ensures that each article is processed and that SentimentAnalyser instances are managed.

        :param args: A tuple containing the article to process, its index, and the total number of articles to process.
        """
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
        """
        This is the entrypoint for the Django command that handles the workflow of fetching unprocessed
        article files, applying NLP processing to each article, and updates the database accordingly.

        29th Feb adding emails to internal email address for easy job monitoring.
        """

        logger = logging.getLogger('scrape_articles_logger')
        logger.info(f"Scrape and analyse articles job started at {datetime.now()}")

        send_mail(
            'NLP Job Started',
            'The scrape and analyse articles job has started.',
            settings.EMAIL_HOST_USER,
            [settings.EMAIL_HOST_USER],
            fail_silently=True,
        )

        ner = spacy.load("en_core_web_sm")

        # Get a list of ProcessedFile objects with nlp_applied=False
        unapplied_files = ProcessedFile.objects.filter(nlp_applied=False)

        processed_urls = set()

        for file in unapplied_files:
            full_path = file.full_path()
            print(full_path)

            with open(full_path, "r") as articles_file:
                articles = json.load(articles_file)
            total_articles = len(articles)

            # user_input = input("Continue? (y/n): ").lower()
            # if user_input.lower() != 'y':
            #     print("Terminating...")
            #     sys.exit()

            for start_index in range(0, total_articles, ARTICLE_CHUNK_SIZE):
                end_index = min(start_index + ARTICLE_CHUNK_SIZE, total_articles)

                # Retrieve and process a chunk of articles from the current file
                articles_from_file = self.process_file(file.id, full_path, start_index, end_index,
                                                       processed_urls, ner)

                # Extend article_objects with articles from the current file
                article_objects = articles_from_file

                article_texts = [article.text_body for article in article_objects]
                article_text_clusters = perform_coreference_resolution(article_texts)

                for article, clusters in zip(article_objects, article_text_clusters):
                    article.set_coref_clusters(clusters)

                print("\nLength Article Objects: ")

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

        send_mail(
            'NLP Job Finished',
            'The scrape and analyse articles job has finished.',
            settings.EMAIL_HOST_USER,
            [settings.EMAIL_HOST_USER],
            fail_silently=True,
        )
