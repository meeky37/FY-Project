from django.db.models import F, Q, ExpressionWrapper, fields, Avg, StdDev, Max, Min
from nlp_processor.models import SimilarArticlePair

"""
SimilarArticle pair determination is relatively expensive operation. Here calculate the date 
difference between article pairs and for those that meet the "Likely Duplicates" annotation 
threshold calculate metrics to determine 3 days is more than enough window - Save huge amount of 
time over checking the months of article pairs I have.
"""

# Calculating the date difference between the article pairs
date_diff = ExpressionWrapper(
    F('article2__article__publication_date') - F('article1__article__publication_date'),
    output_field=fields.DurationField()
)

# Annotating the SimilarArticlePair queryset with the date difference
similar_pairs = SimilarArticlePair.objects.filter(
    Q(hash_similarity_score__gte=90) |
    (
        Q(hash_similarity_score__gte=65, words_diff__lt=10, terms_diff__lt=10,
          vocd_diff__lt=5, yulek_diff__lt=10, simpsond_diff__lt=10,
          the_diff__lt=20, and_diff__lt=20, is_diff__lt=20,
          of_diff__lt=20, in_diff__lt=20, to_diff__lt=20,
          it_diff__lt=20, that_diff__lt=20, with_diff__lt=20
          )
    )
).annotate(date_diff=date_diff)

average_date_diff = similar_pairs.aggregate(avg_date_diff=Avg('date_diff'))
std_dev_date_diff = similar_pairs.aggregate(std_dev_date_diff=StdDev('date_diff'))
max_date_diff = similar_pairs.aggregate(max_date_diff=Max('date_diff'))
min_date_diff = similar_pairs.aggregate(min_date_diff=Min('date_diff'))

print(average_date_diff)
print(std_dev_date_diff)
print(max_date_diff)
print(min_date_diff)

#  Results on 29th Jan
# {'avg_date_diff': datetime.timedelta(seconds=36589, microseconds=323843)}
# {'std_dev_date_diff': datetime.timedelta(days=2, seconds=60600, microseconds=394965)}
# {'max_date_diff': datetime.timedelta(days=31)}
# {'min_date_diff': datetime.timedelta(days=-1)}
