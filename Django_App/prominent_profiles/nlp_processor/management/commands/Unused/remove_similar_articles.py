from django.core.management.base import BaseCommand
from profiles_app.models import Article as ArticleModel

"""
Minhash was initially considered for duplicate article detection but after wider reading I 
concluded that fuzzy hashing was more suitable for identifying text that are essentially the same 
but with minor differences (e.g. extraction differences).

Plus, Fuzzy hashing only require one hash value generation and a simple compare method instead of 
generating multiple hash values per document and comparing them across the articles.

The implementation of Minhash was not fully finalised but this code stays here for reference
purposes.
"""


class Command(BaseCommand):

    def retrieve_existing_articles(self):
        """
        Retrieve all existing articles along with their MinHash signatures.
        """
        existing_articles = ArticleModel.objects.exclude(id=self.database_id)
        article_minhash_signatures = []

        for existing_article in existing_articles:
            minhash_signature_str = existing_article.minhash_signature
            article_minhash_signatures.append((existing_article.id, minhash_signature_str))

        return article_minhash_signatures

    def is_similar_to_existing_articles(self, SIMILARITY_THRESHOLD=0.9):
        """
        Check if the current article is similar to any existing articles.
        """
        current_minhash_signature_str = self.minhash_signature
        current_minhash_set = set(current_minhash_signature_str)

        # Retrieve all articles already processed and their MinHash signatures
        existing_articles = self.retrieve_existing_articles()

        # Check similarity with existing articles
        for article_id, minhash_signature_str in existing_articles:
            existing_minhash_set = set(minhash_signature_str)
            intersection_size = len(current_minhash_set.intersection(existing_minhash_set))
            union_size = len(current_minhash_set.union(existing_minhash_set))
            similarity = intersection_size / union_size

            if similarity > SIMILARITY_THRESHOLD:
                print(
                    f"Article {self.headline} is similar to Article {article_id} with similarity {similarity}")
                return True

        return False

    def handle(self, *args, **options):
        articles = ArticleModel.objects.all()

        for article in articles:
            current_minhash = self.create_minhash(article.text)
            similar_articles = self.find_similar_articles(article, current_minhash)

            if similar_articles:
                print(f"Article {article.headline} is similar to:")
                for similar_article in similar_articles:
                    print(f" - {similar_article.headline}")
