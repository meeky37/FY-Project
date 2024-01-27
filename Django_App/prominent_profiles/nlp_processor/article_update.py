import nltk
import ppdeep
from lexicalrichness import LexicalRichness

from .models import ArticleStatistics


class ArticleUpdate:
    def __init__(self, text_body, article_model):
        self.text_body = text_body  # Added by trafilatura
        self.linguistic_stats = None
        self.article_model = article_model

    def calculate_statistics(self):
        lex = LexicalRichness(self.text_body)
        common_stop_words = ["the", "and", "is", "of", "in", "it", "that", "to", "with"]
        tokens = nltk.word_tokenize(self.text_body)
        stop_word_counts = {word: tokens.count(word) for word in common_stop_words}

        self.linguistic_stats = {
            "fuzzy_hash": ppdeep.hash(self.text_body),
            "word_count": len(tokens),
            "terms_count": lex.terms,
            "vocd": lex.vocd,
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

    def update_stats(self):
        try:
            stats_model, created = ArticleStatistics.objects.update_or_create(
                article=self.article_model,
                defaults={
                    "fuzzy_hash": self.linguistic_stats["fuzzy_hash"],
                    "word_count": self.linguistic_stats["word_count"],
                    "terms_count": self.linguistic_stats["terms_count"],
                    "vocd": self.linguistic_stats["vocd"],
                    "yulek": self.linguistic_stats["yulek"],
                    "simpsond": self.linguistic_stats["simpsond"],
                    "the_count": self.linguistic_stats["the_count"],
                    "and_count": self.linguistic_stats["and_count"],
                    "is_count": self.linguistic_stats["is_count"],
                    "of_count": self.linguistic_stats["of_count"],
                    "in_count": self.linguistic_stats["in_count"],
                    "to_count": self.linguistic_stats["to_count"],
                    "it_count": self.linguistic_stats["it_count"],
                    "that_count": self.linguistic_stats["that_count"],
                    "with_count": self.linguistic_stats["with_count"],
                }
            )

            if not created:
                print(f"ArticleStatistics updated for article {self.article_model.id}")
            else:
                print(f"ArticleStatistics created for article {self.article_model.id}")

        except Exception as e:
            print(f"Error updating ArticleStatistics: {e}")
