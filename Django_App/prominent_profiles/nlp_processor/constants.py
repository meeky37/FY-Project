"""
This module contains constants that will tweak the behaviour of the NLP process and its resource
usage depending on environment.

If the behaviour is being tweaked, then it is worth noting that there would then be inconsistency
between the existing articles analysis and new articles - reprocessing all articles may then take a
significant amount of time (many days given database size 29th Feb) and those articles may no
longer be available at the URLs they were originally.
"""

# Scaling is used in PPs NLP logic to emphasise confident NewsSentiment outcomes (and reduce the
# impact of less confident results on overall score).
EXPONENTIAL_K_VALUE = 3

# The threshold of entity mentioned sentences / total article sentences for an entity to be
# analysed. Less than 20% could lead to misleading results as the bound mentions will be too low
# to be representative.
MENTION_REQ_PER = 0.20

# The threshold for an entity to match to a cluster - reasonably low because not all mentions in
# a coref cluster will match entity name.
# Example: 'Rishi Sunak' wouldn't match The PM, Prime Minister, Leader of the country etc.
# Example 2: ['Keir Starmer', 'Starmer', 'Keir Starmer', 'him', 'Sir Keir', 'the Labour leader',
#  'Keir Starmer (left)', 'him', 'the Labour leader', "Sir Keir Starmer's", 'Starmer', 'Sir Keir',
#  'the Labour leader', 'Keir', 'Sir Keir', 'Sir Keir'] has just 0.375 match rate to 'Starmer'
ENTITY_THRESHOLD_PERCENT = 0.30

# Indicator if entity reference is a substring of a different entity_reference in a coreference
# cluster e.g. 'Keir', 'Keir Starmer' -> 'Keir Starmer'
MERGE_REMOVAL_INDICATOR = -200

# Indicators for when two or more entities have been combined into a single entity due to their
# concatenated form being found within the coreference cluster text.
COMBINED_REMOVAL_INDICATOR = -100
COMBINED_CLUSTER_ID_SEPARATOR = '0000'

# 3 days seems the appropriate trade-off given overhead of combinations vs our existing
# SimilarArticlePairs in publication dates (which were not calculated with this restriction).
# The trade-off is time to check fuzzy hash + linguistic statistics against all other article
# statistics vs the time to process and UX risk of duplicate article existence.
SIMILAR_SEARCH_DAYS = 3

# The number of seconds we try to get a preview image for the web app.
# NB: In case of error the article can still be represented in the article without
PREVIEW_IMG_TIMEOUT = 4

# For similarity check for an article object.
# My thinking is if it is taking more than e.g. 60 seconds then take the risk of it being a
# duplicate in return for less disruption to the pipeline.
SIMILARITY_TIMEOUT = 60

# When running locally on my Macbook Pro the Metal Performance Shaders (MPS) backend for GPU
# training acceleration can be used by FCoref for faster performance. My DO droplet is
# not this capable so 'cpu' config.
F_COREF_DEVICE = 'cpu'

# Memory constraints on droplet with only 4GB to run nginx, django, celery, redis, serve vue.
# ARTICLE_CHUNK_SIZE = 10
# ARTICLE_BATCH_SIZE = 10
# ARTICLE_THREADS = 1

# Torch really requires 8GB to run free of SIGNAL 9-Memory errors - by increasing the server
# resources to 4 vCPUs and 8GB from 2 and 4GB respectively; the scrape_articles_concurrent.py job
# can handle higher chunk, batch and threading.
ARTICLE_CHUNK_SIZE = 30
ARTICLE_BATCH_SIZE = 30
ARTICLE_THREADS = 2
