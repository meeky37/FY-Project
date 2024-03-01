from concurrent.futures import ThreadPoolExecutor, as_completed
from django.core.management.base import BaseCommand
from profiles_app.models import Article as ArticleModel
from ...article_processor import get_preview_image_url


def fetch_image_url(article):
    """
    Gets an image url for the given Article instance.

    :param article: An Article instance for which to fetch the image URL.
    :return: A tuple containing the Article instance and the fetched image URL. If no image URL
         is found, the second element of the tuple will be None.
    """
    image_url = get_preview_image_url(article.url)
    return article, image_url


class Command(BaseCommand):
    help = 'Find image_url for articles with no image_url due to my bug in code late Jan 2024'

    def handle(self, *args, **options):
        """
        Executes the command to fill missing `image_url` fields for Article instances.
        It finds articles without an image URL, fetches URLs in parallel, and updates each record.
        Progress and results are logged to the console, highlighting both successful updates and
        articles for which no image URL could be found.

        This was a one-off method as the bug was resolved by the end of Jan 2024.
        """

        articles_without_image = list(ArticleModel.objects.filter(image_url__isnull=True))
        total_articles = len(articles_without_image)

        self.stdout.write(f'Starting to process {total_articles} articles...')

        # Lets fetch image URLs in parallel
        with ThreadPoolExecutor(max_workers=20) as executor:
            future_to_article = {executor.submit(fetch_image_url, article): article for article
                                 in articles_without_image}

            for future in as_completed(future_to_article):
                article, image_url = future.result()
                if image_url:
                    article.image_url = image_url
                    article.save()
                    self.stdout.write(
                        self.style.SUCCESS(f'Successfully backfilled image_url for {article.url}'))
                else:
                    self.stdout.write(self.style.WARNING(f'No image URL found for {article.url}'))

        self.stdout.write(self.style.SUCCESS(f'Finished processing all articles.'))
