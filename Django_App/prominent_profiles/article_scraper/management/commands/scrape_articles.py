import json
import os

import spacy
from django.core.management.base import BaseCommand
# from profiles_app.models import Article as ArticleModel
# from nlp_processor.article_processor import Article as NLPProcessorArticle

import trafilatura

from django.conf import settings


class Command(BaseCommand):
    help = 'Scrape articles and trigger NLP flow'

    def process_articles(articles, article_objects, processed_urls, start=0, end=None):
        fetches = 0
        skips = 0
        too_short = 0
        if end is None:
            end = len(articles)

        for article in articles[start:end]:
            url = article["url"]

            # Check if the URL has been seen before
            if url in processed_urls:
                skips += 1
                continue  # Skip this article

            try:
                if can_fetch_url(url):
                    fetches += 1
                    downloaded = trafilatura.fetch_url(url)
                    article_text = trafilatura.extract(downloaded, favour_recall=True,
                                                       include_comments=False, include_images=False,
                                                       include_tables=False)
                    article_text = trafilatura.extract(downloaded, favour_recall=True)
                    if article_text and len(article_text) > 249:
                        article_obj = Article(url, article["title"], article_text, NER)
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
        file_path = os.path.join(directory_path, file_name)

        with open(file_path, "r") as articles_file:
            articles = json.load(articles_file)

        return Command.process_articles(articles, article_objects, processed_urls)

    def handle(self, *args, **options):
        processed_urls = set()
        article_objects = []
        ner = spacy.load("en_core_web_sm")

        media_path = os.path.join(settings.ARTICLE_SCRAPER_MEDIA_ROOT, 'api_articles')

        file_name_1 = "keir+starmer_no_dup_articles_loop_17-11-2023-18:44.json"
        media_path_1 = os.path.join(media_path, 'keir_starmer', file_name_1)
        full_path_1 = os.path.join(settings.BASE_DIR, 'article_scraper', media_path_1)
        article_objects = self.process_file(full_path_1, article_objects, processed_urls)

        file_name_2 = "rishi+sunak_no_dup_articles_loop_17-11-2023-18:46.json"
        media_path_2 = os.path.join(media_path, 'rishi_sunak', file_name_2)
        full_path_2 = os.path.join(settings.BASE_DIR, 'article_scraper', media_path_2)
        article_objects.extend(self.process_file(full_path_2, article_objects, processed_urls))

        file_name_3 = "uk+politics_no_dup_articles_loop_17-11-2023-19:26.json"
        media_path_3 = os.path.join(media_path, 'uk_politics', file_name_3)
        full_path_3 = os.path.join(settings.BASE_DIR, 'article_scraper', media_path_3)
        article_objects.extend(self.process_file(full_path_3, article_objects, processed_urls))

        print(len(article_objects))



