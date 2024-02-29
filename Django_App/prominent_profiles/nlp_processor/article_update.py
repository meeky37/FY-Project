"""For storage and legal/publisher terms of service considerations Prominent Profiles does not
store full article texts. The intention was always to provide traffic to the site directly;
PP is an innovative News Discovery tool rather than a news article reader. However, duplicates were
commonplace and create an unprofessional look as well as costing expensive resource time running
NewsSentiment on sentences it has seen EXACTLY before! This module provides a solution in the
form of article statistics determination and analysis and stores these stats OneToOne for an
article in the database

Key Features:
- Statistics calculation using fuzzy hash, and linguistic statistics to help fingerprint articles.
- Create (or update) ArticleStatistics (One to one w/ Article) in the database.
- Compute percentage differences so thresholding can be used across PP processes.
"""

import nltk
import ppdeep
from lexicalrichness import LexicalRichness

from .models import ArticleStatistics


def calculate_statistics(text_body):
    """
    Calculates various linguistic statistics and a fuzzy hash for a given text body.

    This function computes word count, terms count, TTR (Type-Token Ratio) metrics like VOCD,
    Yule's K, and Simpson's D, along with counts of common stop words within the text. These
    statistics were chosen based on MINIMAL % difference between duplicate (or near-duplicate
    articles) articles, and MAXIMAL % difference between different articles.

    It uses NLTK for tokenization and lexical richness calculations, and ppdeep for fuzzy hashing
    (the primary indicator of duplication in PP business logic).

    :param text_body: The text content for which to calculate statistics.
    :return: dict: A dictionary containing the calculated linguistic statistics and fuzzy hash of the text.
    """

    try:
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        nltk.download('punkt')

    lex = LexicalRichness(text_body)
    common_stop_words = ["the", "and", "is", "of", "in", "it", "that", "to", "with"]
    tokens = nltk.word_tokenize(text_body)
    stop_word_counts = {word: tokens.count(word) for word in common_stop_words}

    try:
        vocd_int = lex.vocd()
    except ValueError:
        vocd_int = None

    linguistic_stats = {
        "fuzzy_hash": ppdeep.hash(text_body),
        "word_count": len(tokens),
        "terms_count": lex.terms,
        "vocd": vocd_int,
        "yulek": lex.yulek,
        "simpsond": lex.simpsond,
        "the_count": stop_word_counts["the"],
        "and_count": stop_word_counts["and"],
        "is_count": stop_word_counts["is"],
        "of_count": stop_word_counts["of"],
        "in_count": stop_word_counts["in"],
        "it_count": stop_word_counts["it"],
        "that_count": stop_word_counts["that"],
        "to_count": stop_word_counts["to"],
        "with_count": stop_word_counts["with"],
    }

    return linguistic_stats


def create_update_stats(article_model, linguistic_stats):
    """
    Updates or creates an ArticleStatistics model instance with the provided linguistic statistics.
    Updates would typically be in the case of an interrupted article processing celery job.
    Exceptions handled, printing error messages in case of failure.

    :param article_model: The Django model instance of the article for which statistics are being updated or created.
    :param linguistic_stats: A dictionary of linguistic statistics to be saved or updated in the ArticleStatistics model.
    :return:
    """

    try:
        stats_model, created = ArticleStatistics.objects.update_or_create(
            article=article_model,
            defaults={
                "fuzzy_hash": linguistic_stats["fuzzy_hash"],
                "word_count": linguistic_stats["word_count"],
                "terms_count": linguistic_stats["terms_count"],
                "vocd": linguistic_stats["vocd"],
                "yulek": linguistic_stats["yulek"],
                "simpsond": linguistic_stats["simpsond"],
                "the_count": linguistic_stats["the_count"],
                "and_count": linguistic_stats["and_count"],
                "is_count": linguistic_stats["is_count"],
                "of_count": linguistic_stats["of_count"],
                "in_count": linguistic_stats["in_count"],
                "to_count": linguistic_stats["to_count"],
                "it_count": linguistic_stats["it_count"],
                "that_count": linguistic_stats["that_count"],
                "with_count": linguistic_stats["with_count"],
            }
        )

        if not created:
            print(f"ArticleStatistics updated for article {article_model.id}")
        else:
            print(f"ArticleStatistics created for article {article_model.id}")

    except Exception as e:
        print(f"Error updating ArticleStatistics: {e}")


def calculate_percentage_difference(value1, value2):
    """
    :param value1:
    :param value2:
    :return: float or none
    """
    if value1 is not None and value2 is not None and max(value1, value2) != 0:
        return abs((value1 - value2) / max(value1, value2)) * 100
    elif value1 is not None or value2 is not None:
        return 100
    else:
        return None


def calculate_all_percentage_differences(pair):
    """
    For each statistical metric this calculates the percentage difference between two articles
    represented by a pair object. It updates the pair object with these calculated differences and
    an average count difference, then saves the changes.
    :param pair:
    :return:
    """
    stat1 = pair.article1
    stat2 = pair.article2
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


class ArticleUpdate:
    def __init__(self, text_body, article_model):
        self.text_body = text_body  # Added by trafilatura
        self.linguistic_stats = None
        self.article_model = article_model

    def get_statistics(self):
        self.linguistic_stats = calculate_statistics(self.text_body)

    def update_stats(self):
        create_update_stats(self.article_model, self.linguistic_stats)
