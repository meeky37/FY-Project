from django.core.management.base import BaseCommand
from profiles_app.models import Article

class Command(BaseCommand):
    help = 'Remove duplicate articles based on headline'

    def handle(self, *args, **options):
        articles = Article.objects.all()

        # Dict for storing seen headlines
        seen_headlines = {}

        for article in articles:
            headline = article.headline

            if headline in seen_headlines:
                self.stdout.write(self.style.SUCCESS(
                    f'Deleted duplicate article with ID {article.headline}'))
                article.delete()
            else:
                seen_headlines[headline] = True
