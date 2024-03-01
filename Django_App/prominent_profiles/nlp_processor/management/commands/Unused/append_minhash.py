from django.core.management.base import BaseCommand
from profiles_app.models import Article as ArticleModel
from datasketch import MinHash
import trafilatura

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
    help = 'Append minhash to existing articles'

    def handle(self, *args, **options):
        # Articles from database
        articles = ArticleModel.objects.all()

        # for url in each article fetched
        for article in articles:
            downloaded = trafilatura.fetch_url( article.url)

            article_text = trafilatura.extract(downloaded, favour_recall=True,
                                               include_comments=False, include_images=False,
                                               include_tables=False)
            if article_text is not None:
                minhash = MinHash()
                for word in article_text.split():
                    minhash.update(word.encode('utf-8'))
                minhash_signature = minhash.digest().tostring().hex()
                print(f"MinHash Signature for article with ID {article.id}: {minhash_signature}")
                # update database object with minhash_signature populated
                article.minhash_signature = minhash_signature
                article.save()

                self.stdout.write(self.style.SUCCESS(
                    f'Successfully updated MinHash for article with ID {article.id}'))
