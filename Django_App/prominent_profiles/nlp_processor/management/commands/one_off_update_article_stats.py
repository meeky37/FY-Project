from itertools import combinations

import ppdeep
import trafilatura
from django.core.management.base import BaseCommand

from ...article_update import ArticleUpdate
from profiles_app.models import Article as ArticleModel
from ...models import ArticleStatistics, SimilarArticlePair

class Command(BaseCommand):
    help = 'Update article statistics for a specific article'

    def handle(self, *args, **options):

        # target_url = "https://www.bbc.co.uk/news/world-us-canada-68051757.amp"

        article_list = ArticleModel.objects.filter(
            articlestatistics__fuzzy_hash__isnull=True
        )

        for article in article_list:
            downloaded = trafilatura.fetch_url(article.url)
            extracted_text = trafilatura.extract(
                downloaded,
                favour_recall=True,
                include_comments=False,
                include_images=False,
                include_tables=False
            )

            article_update = ArticleUpdate(extracted_text, article)
            if extracted_text is not None:
                article_update.calculate_statistics()
                article_update.update_stats()
                self.stdout.write(
                    self.style.SUCCESS(f'Successfully updated stats for article {article.id}'))
            else:
                self.stdout.write(
                    self.style.WARNING(f'No text returned {article.id}'))

        all_stats = ArticleStatistics.objects.all()

        for stat1, stat2 in combinations(all_stats, 2):
            fuzzy_hash1 = stat1.fuzzy_hash
            fuzzy_hash2 = stat2.fuzzy_hash

            similarity_score = ppdeep.compare(fuzzy_hash1, fuzzy_hash2)

            print(
                f"Comparison between Article {stat1.article_id} and Article {stat2.article_id}: {similarity_score}")

        # Lowest genuine I have found thus far is 74 so no need to use 0 > as in first run through.
            if similarity_score >= 65:
                similar_pair = SimilarArticlePair(article1=stat1, article2=stat2,
                                                  similarity_score=similarity_score)
                similar_pair.save()
                print(f"Similarity pair stored: {similar_pair}")

        all_pairs = SimilarArticlePair.objects.all()

        for pair in all_pairs:
            stat1 = pair.article1
            stat2 = pair.article2

            print(
                    f"Comparison between Article {stat1.article_id} and Article "
                    f"{stat2.article_id}")

            def calculate_percentage_difference(value1, value2):
                return abs(value1 - value2) / max(value1, value2) * 100 if max(value1,
                                                                               value2) != 0 else \
                    None

            pair.words_diff = calculate_percentage_difference(stat1.word_count, stat2.word_count)
            pair.terms_diff = calculate_percentage_difference(stat1.terms_count, stat2.terms_count)
            pair.vocd_diff = calculate_percentage_difference(stat1.vocd, stat2.vocd)
            pair.yulek_diff = calculate_percentage_difference(stat1.yulek, stat2.yulek)
            pair.simpsond_diff = calculate_percentage_difference(stat1.simpsond, stat2.simpsond)
            pair.the_diff = calculate_percentage_difference(stat1.the_count, stat2.the_count)
            pair.and_diff = calculate_percentage_difference(stat1.and_count, stat2.and_count)
            pair.is_diff = calculate_percentage_difference(stat1.is_count, stat2.is_count)
            pair.of_diff = calculate_percentage_difference(stat1.of_count, stat2.of_count)
            pair.in_diff = calculate_percentage_difference(stat1.in_count, stat2.in_count)
            pair.to_diff = calculate_percentage_difference(stat1.to_count, stat2.to_count)
            pair.it_diff = calculate_percentage_difference(stat1.it_count, stat2.it_count)
            pair.that_diff = calculate_percentage_difference(stat1.that_count, stat2.that_count)
            pair.with_diff = calculate_percentage_difference(stat1.with_count, stat2.with_count)

            pair.avg_count_diff = pair.calculate_average_diff()
            pair.save()
