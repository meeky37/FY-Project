from django.core.management.base import BaseCommand
from profiles_app.models import Article

"""
This very simplistic approach was inappropriate for a number of reasons, but an initial start.
1. When the same articles are republished headlines often are rewritten / different editorial
2. Examples across the site show headlines across completely different texts can be the exact same 
   especially if the news event is neutral/general reporting.
"""


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
