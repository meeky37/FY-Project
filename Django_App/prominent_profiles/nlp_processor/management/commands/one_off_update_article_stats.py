from itertools import combinations

import ppdeep
import trafilatura
from django.core.management.base import BaseCommand

from ...article_update import ArticleUpdate, calculate_all_percentage_differences
from profiles_app.models import Article as ArticleModel
from ...models import ArticleStatistics, SimilarArticlePair

class Command(BaseCommand):
    help = 'Update article statistics for a specific article'

    def handle(self, *args, **options):

        # target_url = "https://www.bbc.co.uk/news/world-us-canada-68051757.amp"
        #
        # article_list = ArticleModel.objects.filter(
        #     articlestatistics__fuzzy_hash__isnull=True
        # )
        #
        # for article in article_list:
        #     downloaded = trafilatura.fetch_url(article.url)
        #     extracted_text = trafilatura.extract(
        #         downloaded,
        #         favour_recall=True,
        #         include_comments=False,
        #         include_images=False,
        #         include_tables=False
        #     )
        #
        #     article_update = ArticleUpdate(extracted_text, article)
        #     if extracted_text is not None:
        #         article_update.get_statistics()
        #         article_update.update_stats()
        #         self.stdout.write(
        #             self.style.SUCCESS(f'Successfully updated stats for article {article.id}'))
        #     else:
        #         self.stdout.write(
        #             self.style.WARNING(f'No text returned {article.id}'))

        all_stats = ArticleStatistics.objects.all()
        # all_stats = ArticleStatistics.objects.filter(article_id__gt=3746)

        for stat1, stat2 in combinations(all_stats, 2):
            fuzzy_hash1 = stat1.fuzzy_hash
            fuzzy_hash2 = stat2.fuzzy_hash

            similarity_score = ppdeep.compare(fuzzy_hash1, fuzzy_hash2)

            print(
                f"Comparison between Article {stat1.article_id} and Article {stat2.article_id}: {similarity_score}")

        # The lowest genuine I have found thus far is 74, so no need to use 0 > as in the first run
        # through.
            if similarity_score >= 65:
                similar_pair = SimilarArticlePair(article1=stat1, article2=stat2,
                                                  hash_similarity_score=similarity_score)
                similar_pair.save()
                print(f"Similarity pair stored: {similar_pair}")

        all_pairs = SimilarArticlePair.objects.all()

        for pair in all_pairs:
            calculate_all_percentage_differences(pair)
