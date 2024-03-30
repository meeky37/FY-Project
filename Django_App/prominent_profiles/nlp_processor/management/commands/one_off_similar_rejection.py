import csv
from django.core.management.base import BaseCommand
from django.db.models import Q, F, Count
from datetime import datetime, timedelta
from django.utils import timezone
from nlp_processor.models import Article, SimilarArticlePair
from profiles_app.models import OverallSentiment


class Command(BaseCommand):
    help = ('Marks articles based on hash or linguistics,  and exports '
            'details to csv. Job created to reduce overhead on OverallSentiment API Views as this'
            ' means we can set similar to True for articles added before pipeline was updated on '
            '30th Jan. Also can use this to help evaluate the quality of duplicate detection.')

    def handle(self, *args, **options):
        filename = "article_pairs_details.csv"
        # Cut off set at month = 2, day = 1 for modification of before pipeline updated to
        # include similar rejection.
        # Cut off updated to month = 6, day = 1 for all duplicates dump.
        cutoff_date = timezone.make_aware(datetime(year=2999, month=1, day=1))
        potential_duplicates = SimilarArticlePair.objects.filter(
            Q(article2__article__publication_date__lt=cutoff_date) &
            (Q(hash_similarity_score__gte=90) |
             (Q(hash_similarity_score__gte=65, words_diff__lt=10, terms_diff__lt=10,
                vocd_diff__lt=5, yulek_diff__lt=10, simpsond_diff__lt=10,
                the_diff__lt=20, and_diff__lt=20, is_diff__lt=20,
                of_diff__lt=20, in_diff__lt=20, to_diff__lt=20,
                it_diff__lt=20, that_diff__lt=20, with_diff__lt=20)) &
             Q(article2__article__publication_date__lte=F(
                 'article1__article__publication_date') + timedelta(days=14)))
        ).select_related('article1__article', 'article2__article').distinct()

        article2_ids_to_mark = set()
        with open(filename, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow([
                'Article 1 ID',
                'Article 2 ID',
                'Article 1 Reject',
                'Article 2 Reject',
                'Article 1 Headline',
                'Article 2 Headline',
                'Article 1 Site Name',
                'Article 2 Site Name',
                'Article 1 Sentiment Count',
                'Article 2 Sentiment Count',
                'Hash Similarity Score',
                'Marking',
                'Live Latest Feed',
                'Article 1 URL',
                'Article 2 URL'
            ])

            for pair in potential_duplicates:
                marking = 'PP_DEEP' if pair.hash_similarity_score >= 90 else 'LINGUISTIC'
                contains_keywords = 'TRUE' if 'live' in pair.article1.article.headline.lower() or 'latest' in pair.article1.article.headline.lower() or 'live' in pair.article2.article.headline.lower() or 'latest' in pair.article2.article.headline.lower() else 'FALSE'

                # Count OverallSentiment for each article
                article1_sentiment_count = OverallSentiment.objects.filter(
                    article_id=pair.article1_id).count()
                article2_sentiment_count = OverallSentiment.objects.filter(
                    article_id=pair.article2_id).count()

                writer.writerow([
                    pair.article1_id,
                    pair.article2_id,
                    pair.article1.article.similar_rejection,
                    pair.article2.article.similar_rejection,
                    pair.article1.article.headline,
                    pair.article2.article.headline,
                    pair.article1.article.site_name,
                    pair.article2.article.site_name,
                    article1_sentiment_count,
                    article2_sentiment_count,
                    pair.hash_similarity_score,
                    marking,
                    contains_keywords,
                    pair.article1.article.url,
                    pair.article2.article.url,
                ])

                article2_ids_to_mark.add(pair.article2_id)

        self.stdout.write(self.style.SUCCESS(f'Details exported to {filename}.'))
        confirm = input(
            'Do you want to proceed and mark the identified Article 2s as similar rejects? (Y/N): ')

        if confirm.lower() == 'y':
            Article.objects.filter(id__in=article2_ids_to_mark).update(similar_rejection=True)
            self.stdout.write(self.style.SUCCESS(
                f'Marked {len(article2_ids_to_mark)} Article 2s as having a similar rejection.'))
        elif confirm.lower() == 'n':
            self.stdout.write(self.style.SUCCESS('Operation cancelled. No changes were made.'))
        else:
            self.stdout.write(
                self.style.ERROR('Invalid input. Operation cancelled. No changes were made.'))
