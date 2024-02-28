EXPONENTIAL_K_VALUE = 3
MENTION_REQ_PER = 0.20
ENTITY_THRESHOLD_PERCENT = 0.30
MERGE_REMOVAL_INDICATOR = -200
COMBINED_REMOVAL_INDICATOR = -100
COMBINED_CLUSTER_ID_SEPARATOR = '0000'

# 3 days seems the appropriate trade-off given overhead of combinations vs our existing
#  SimilarArticlePairs in publication dates.
SIMILAR_SEARCH_DAYS = 3
PREVIEW_IMG_TIMEOUT = 4
F_COREF_DEVICE = 'cpu'

# Memory constraints on droplet with only 4GB to run nginx, django, celery, redis, serve vue.
# ARTICLE_CHUNK_SIZE = 10
# ARTICLE_BATCH_SIZE = 10
# ARTICLE_THREADS = 1

ARTICLE_CHUNK_SIZE = 30
ARTICLE_BATCH_SIZE = 30
ARTICLE_THREADS = 1