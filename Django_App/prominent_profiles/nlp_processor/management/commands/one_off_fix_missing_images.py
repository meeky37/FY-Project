from concurrent.futures import ThreadPoolExecutor, as_completed
from django.core.management.base import BaseCommand
from profiles_app.models import Article as ArticleModel
from ...article_processor import get_preview_image_url

class Command(BaseCommand):
    help = 'Backfill image_url for articles with no image_url due to my bug in code late Jan 2024'

    def fetch_image_url(self, article):
        image_url = get_preview_image_url(article.url)
        return article, image_url

    def handle(self, *args, **options):
        articles_without_image = list(ArticleModel.objects.filter(image_url__isnull=True))
        total_articles = len(articles_without_image)

        self.stdout.write(f'Starting to process {total_articles} articles...')

        # Lets fetch image URLs in parallel
        with ThreadPoolExecutor(max_workers=20) as executor:
            future_to_article = {executor.submit(self.fetch_image_url, article): article for article in articles_without_image}

            for future in as_completed(future_to_article):
                article, image_url = future.result()
                if image_url:
                    article.image_url = image_url
                    article.save()
                    self.stdout.write(self.style.SUCCESS(f'Successfully backfilled image_url for {article.url}'))
                else:
                    self.stdout.write(self.style.WARNING(f'No image URL found for {article.url}'))

        self.stdout.write(self.style.SUCCESS(f'Finished processing all articles.'))
