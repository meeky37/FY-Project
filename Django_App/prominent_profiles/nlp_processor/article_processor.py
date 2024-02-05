# nlp_processor/article_processor.py
from datetime import timezone, timedelta, datetime

import requests
from bs4 import BeautifulSoup
from django.db.models import Q, F

from .article_update import calculate_statistics, calculate_all_percentage_differences
from .models import ArticleStatistics, SimilarArticlePair
from profiles_app.models import Article as ArticleModel
from nlp_processor.sentiment_resolver import SentimentAnalyser
import math
import re
from functools import reduce
from textblob import TextBlob
from collections import defaultdict
from .constants import (ENTITY_THRESHOLD_PERCENT,
                        MENTION_REQ_PER,
                        MERGE_REMOVAL_INDICATOR,
                        COMBINED_REMOVAL_INDICATOR,
                        COMBINED_CLUSTER_ID_SEPARATOR,
                        SIMILAR_SEARCH_DAYS,
                        PREVIEW_IMG_TIMEOUT)
from urllib.parse import urlparse
import urllib.robotparser
import ppdeep
from itertools import product


def can_fetch_url(url_to_check):
    """Determine if the URL can be fetched by all crawlers - adding politeness / adherence to robot
    policy."""
    parsed_url = urlparse(url_to_check)
    base_url = parsed_url.scheme + "://" + parsed_url.netloc
    rules = urllib.robotparser.RobotFileParser()
    rules.set_url(base_url + "/robots.txt")
    rules.read()
    return rules.can_fetch("*", url_to_check)


def get_preview_image_url(url):
    try:
        response = requests.get(url, timeout=PREVIEW_IMG_TIMEOUT)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')

            og_image = soup.find('meta', property='og:image')
            if og_image:
                return og_image['content']

            # Twitter Card image tag
            twitter_image = soup.find(name='twitter:image')
            if twitter_image:
                return twitter_image['content']

    except Exception as e:
        print(f"Error fetching preview image URL: {e}")


def merge_positions(entities, word):
    """Merge all instances of the same entity into a single entry with multiple
    positions. Where same means a lowercase word match. Place them into an
    'entities' dictionary."""
    entity_key = (word.text + word.label_).lower()
    if entity_key in entities:
        entities[entity_key][1].append([word.start_char, word.end_char])
    else:
        entities[entity_key] = [word.text, [[word.start_char, word
        .end_char]], word.label_]
    return entities


def cleanse_cluster_text(cluster_text):
    return [word.strip() for word in cluster_text if word.lower().strip() not
            in undesired_words]


undesired_words = ["i", "he", "his", "she", "they", "it", "this", "that",
                   "these", "those", "the", "a", "an", "of"]


def remove_titles(text):
    title_pattern = r"^(Mr|Mrs|Ms|Miss|Dr|Prof|Rev|Capt|Sir|Madam|Mx|Esq|Hon|Gen|Col|Sgt|Fr|Sr|Jr|Lord|Lady)\s"
    text = re.sub(title_pattern, "", text)

    '''10th Nov adding as:
        {'Entity Name': 'Keith', 'Positions': [[11664, 11669], [12301, 12306], [14453, 14458], 
        [15005, 15010], [15286, 15291]], 'Label': 'PERSON', 'Num Positions': 5, 'Cluster Info': 
        {'Cluster ID': 12, 'Cluster Text': ['Keith', 'Keith', 'Keith', 'Keith', 'Hugo Keith KC',
        'Keith', 'Keith', 'Keith'], 'Cluster Positions': [(11664, 11669), (12301, 12306), 
        (12312, 12314), (13026, 13031), (13464, 13469), (14374, 14387), (14453, 14458),
        (15005, 15010), (15286, 15291)]}}
        would have been updated to Hugo Keith had it not been for KC which made it 3 words'''

    # Pattern for titles at the end
    title_pattern_end = r"\s*(KC|QC)\s*$"
    text = re.sub(title_pattern_end, "", text)
    return text


def insert_intervals(initial_list, new_values):
    """The insert_intervals function enables the segmentation of sentences provided by
    TextBlob (as shown in the cell below) to be further divided into smaller boundaries. This
     division is based on the identification of specific points where it is deemed necessary
     to split sentences, particularly within the context of news articles."""

    def insert_recursive(intervals, values):
        if not values:
            return intervals  # Base case: Return the intervals when there are no more values to insert.

        value = values[0]
        result = []
        for interval in intervals:
            if interval[0] <= value <= interval[1]:
                # If the value falls within an existing interval, split the interval into two parts.
                # The first part goes from the interval's start to the value (inclusive), and
                # the second part goes from the value+1 to the interval's end.
                if interval[0] < value:
                    # To mess around with intervals change value + - offset here.
                    result.append((interval[0], value))
                if value < interval[1]:
                    # To mess around with intervals change value + - offset here.
                    result.append((value + 1, interval[1]))
            else:
                # If the value doesn't fall within the interval, keep the interval as is.
                result.append(interval)
        # Recursively process other values.
        return insert_recursive(result, values[1:])

        # Recursive function call

    updated_list = insert_recursive(initial_list, new_values)
    return updated_list


def is_substring(entity1, entity2):
    return entity1.lower() in entity2.lower() or entity2.lower() in entity1.lower()


def combine_entities(entities, cluster_text):
    combined_entity = None

    for entity1 in entities:
        for entity2 in entities:
            if entity1 != entity2:
                combined1 = entity1 + ' ' + entity2
                combined2 = entity2 + ' ' + entity1

                if combined1 in cluster_text or combined2 in cluster_text:
                    combined_entity = combined1 if combined1 in cluster_text \
                        else combined2
                    break

    return combined_entity


def update_entity_name(entry):
    """Calls remove titles and removes possessives before checking if an entity name is a
     substring of a 2 word entry in the coref cluster e.g. Johnson should become Boris Johnson"""

    entity_name = entry['Entity Name']
    cluster_text = entry['Cluster Info']['Cluster Text']

    for text in cluster_text:
        # Remove titles as not relevant
        text = remove_titles(text)
        # Replaces left / right quotation mark with standard single quotation mark
        text = text.replace('’', "'").replace('‘', "'")
        # Remove possessive markers for comparison
        text = text.replace("’s", "")
        # Remove space and quote
        text = text.replace(" '", "")
        # Check if the current entity name is a substring of a 2-word cluster text entry
        if len(text.split()) == 2 and entity_name in text:
            entry['Entity Name'] = text
            break
    return entry


def clean_up_substrings(clustered_entities):
    longest_names = {}
    entities_to_keep = []

    # Identify longest names in cluster ID and remove shorter ones
    for entity in clustered_entities:
        cluster_id = entity['Cluster Info']['Cluster ID']
        entity_name = entity['Entity Name']
        current_longest = longest_names.get(cluster_id, "")

        if len(entity_name) > len(current_longest):
            # Remove the shorter entity without adding it to the list of entities to keep
            if current_longest:
                entities_to_keep = [e for e in clustered_entities if
                                    e['Cluster Info']['Cluster ID'] != cluster_id]
            longest_names[cluster_id] = entity_name

            # Add the entity to the list of entities to keep
            entities_to_keep.append(entity)

    # Set merge indicator for entities with more than one associated name in the original list
    for entity in clustered_entities:
        cluster_id = entity['Cluster Info']['Cluster ID']
        if len([e for e in entities_to_keep if
                e['Cluster Info']['Cluster ID'] == cluster_id]) > 1:
            entity['Num Positions'] = int(MERGE_REMOVAL_INDICATOR)
            entity['Positions'] = int(MERGE_REMOVAL_INDICATOR)
    return entities_to_keep


def create_entity_entry(entity_name, positions, label, num_positions):
    return {
        'Entity Name': entity_name,
        'Positions': positions,
        'Label': label,
        'Num Positions': num_positions,
        'Cluster Info': []
    }


class Article:
    # MENTION_REQ_PER = 0.20 - Moved to constants.py
    # ENTITY_THRESHOLD_PERCENT = 0.30 - Moved to constants.py

    def __init__(self, url, headline, text_body, NER, date, author, site_name):
        self.url = url
        self.NER = NER
        self.headline = headline
        self.image_url = None
        self.description = None
        self.text_body = text_body  # Added by trafilatura
        self.coref_clusters = None
        self.people_entities = None  # NER results here.
        self.sentence_bounds = None
        self.num_sentences = None
        self.mention_threshold = None
        self.entity_to_cluster_mapping = []
        self.clustered_entities = None
        self.database_candidate = False
        self.database_id = None
        self.bounds_sentiment = None
        self.sentiment_analyser = None
        self.publication_date = date
        self.author = author
        self.site_name = site_name
        self.linguistic_stats = None

    def set_sentiment_analyser(self, sa):

        if sa is None:
            self.sentiment_analyser = SentimentAnalyser()
        else:
            self.sentiment_analyser = sa

    def get_bounds_sentiment(self):
            self.bounds_sentiment = self.sentiment_analyser.process_clustered_entities(
                clustered_entities=self.clustered_entities, sentence_bounds=self.sentence_bounds,
                article_text=self.text_body, database_id=self.database_id,
                debug=False)

    def print_clustered_entities(self):
        for entry in self.clustered_entities:
            print(entry)
            print()

    def print_entity_to_cluster_mapping(self):
        for entry in self.entity_to_cluster_mapping:
            print(entry)
            print()

    def determine_entity_to_cluster_mapping(self):

        """
        Removing pronouns & other 'useless words' (his, her, he, I etc) then doing a % match rate on
        entity text across cluster entries for each entity. If match rate % exceeds threshold
        pair them.

        Improvement: Spliting the entity names into part words e.g. Sadiq Khan will be split into
        Sadiq and Khan for evaluation purposes. This way if they are mostly mentioned by first
        or second name the match still has an opportunity to take place.
        """

        for entity_type, entities in self.people_entities.items():
            for entity in entities:
                entity_name, positions, label, num_positions = entity
                entity_entry = create_entity_entry(entity_name, positions, label,
                                                   num_positions)
                self.process_clusters_for_entity(entity_entry, entity_name)

    def process_clusters_for_entity(self, entity_entry, entity_name):
        cluster_id = 0
        for index, (cluster_text, cluster_positions, _) in self.coref_clusters:
            cluster_id += 1

            cluster_text = cleanse_cluster_text(cluster_text)
            cleaned_cluster_text = [remove_titles(text) for text in cluster_text]

            # Check if the length of cleaned_cluster_text is less than 4 elements
            if len(cleaned_cluster_text) < 4:
                continue  # Skip this cluster and move to the next one

            total_coref_words = " ".join(cleaned_cluster_text)
            entity_parts = entity_name.split()
            max_percentage = 0.0

            winning_entity_part = None
            for entity_part in entity_parts:
                entity_count = total_coref_words.count(entity_part)
                #  How well the entity name matches the cluster.
                percentage = entity_count / len(cleaned_cluster_text)

                # Is this a better match than the previous best match? If so
                # make this the new best match.
                if percentage > max_percentage:
                    max_percentage = percentage

            if max_percentage >= ENTITY_THRESHOLD_PERCENT:
                cluster_entry = {
                    'Cluster ID': cluster_id,
                    'Cluster Text': cluster_text,
                    'Cluster Positions': cluster_positions
                }

                entity_entry['Cluster Info'] = cluster_entry
                self.entity_to_cluster_mapping.append(entity_entry)
                break

    def set_coref_clusters(self, sorted_combined_clusters):
        # Add an ID to each cluster
        self.coref_clusters = list(enumerate(sorted_combined_clusters))

    def source_ner_people(self):

        """SpaCy is a popular NLP library that offers pre-trained models for various languages, and
            its NER component is capable of recognising and categorising named entities within text.
            It is utilised here to identify PERSON entities"""

        NER = self.NER
        article_text = self.text_body
        article = NER(article_text)

        '''# Recommended mention - 'Discard a cluster c in a document d if |Mc| ≤ 0.2|Sd|,  
        where |...| is the number of mentions of a cluster (Mc) and sentences in a document (Sd)
        (NEWS-MTSC approach)'''

        entity_types = ["CARDINAL", "DATE", "EVENT", "FAC", "GPE", "LANGUAGE", "LAW",
                        "LOC", "MONEY", "NORP", "ORDINAL", "ORG", "PERCENT",
                        "PERSON", "PRODUCT", "QUANTITY", "TIME", "WORK_OF_ART"]

        entity_type_to_entities = {
            entity_type: [
                [
                    entity_text,
                    positions,
                    label,
                    len(positions)
                ] for entity_text, positions, label in reduce(
                    merge_positions,
                    filter(lambda word: word.label_ == entity_type, article.ents),
                    {}
                ).values()
            ] for entity_type in entity_types
        }

        for entity_type, entities in entity_type_to_entities.items():
            # print(f"Entity Type: {entity_type}")
            for entity in entities:
                entity_text, positions, label, num_positions = entity
                # print(f"Entity: {entity_text}")
                # print(f"Positions: {positions}")
                # print(f"Label: {label}")
                # print(f"Number of Positions: {num_positions}")
                # print()

        people_entities = {entity_type: entity_info for entity_type, entity_info in
                           entity_type_to_entities.items() if entity_type == 'PERSON'}

        for entity in entity_type_to_entities[entity_type]:
            entity_text, positions, label, num_positions = entity
            if entity_type not in people_entities:
                people_entities[entity_type] = []
            people_entities[entity_type].append({
                'Entity': entity_text,
                'Positions': positions,
                'Label': label,
                'Number of Positions': num_positions
            })

        self.people_entities = people_entities

    def determine_sentences(self):

        """
        Process the article text, tokenise by sentence and add custom adjustments to the
        tokenisation using insert intervals below.
        spaCy was not satisfactory for accurately tokenising for sentence start / end
        characters. Trying textblob instead. TextBlob is a Python library for processing textual
        data that is bulit upon NLTK.

        TextBlob can provide me with the start and end of sentences by using the sentences
        attribute of a TextBlob object. This attribute returns a list of Sentence objects, each
        of which has a start and end property that indicates the index of the first and last
        character of the sentence within the original text."""

        # Process the article text and adjust tokenization
        article_text = self.text_body
        blob = TextBlob(article_text)
        sentences = blob.sentences

        # Determine custom tokenization:
        hyphen_sentences = re.split(r'\n-', article_text)
        # In testing article a new line and '-' hyphen use typically means consider
        # a different sentence.
        hyphen_nl_pos = [pos for pos, char in enumerate(article_text) if
                         article_text[pos:pos + 2] == '\n-']
        extra_split = hyphen_nl_pos

        sentence_bounds = [(int(sentence.start), int(sentence.end)) for sentence
                           in sentences]

        # Insert custom intervals
        updated_list = insert_intervals(sentence_bounds, extra_split)

        self.sentence_bounds = updated_list
        self.num_sentences = len(list(sentence_bounds))
        self.mention_threshold = math.floor(self.num_sentences * MENTION_REQ_PER)

    def entity_cluster_map_consolidation(self):
        """
        Purposes of below code:

        1. Substring Matching: If one entity is a substring of another entity, they
        are considered as candidates for consolidation. For example, if "Rishi" is a
        substring of "Rishi Sunak," the code merges them into the longer version, "Rishi Sunak."

        2. First and Second Name Combination: If there are two entities, one
        representing the first name and the other representing the last name, and
        they share the same coreference cluster, the code attempts to combine them
        into a single entity.

        3. 9th November - add while loop to see if continuing consolidation until no more
        consolidation takes place results in a better consolidation as theorised.

        4. 16th November - resolve instances of 'King\n11:43' which should be King.

        """

        cluster_dict = defaultdict(list)
        for entry in self.entity_to_cluster_mapping:
            entity_name = entry['Entity Name']
            cluster_id = entry['Cluster Info']['Cluster ID']
            cluster_dict[cluster_id].append(entry)

        # While loop to continue consolidation until no more consolidation can be done
        consolidation_done = True
        while consolidation_done:
            consolidation_done = False
            for cluster_id, entries in cluster_dict.items():
                if len(entries) > 1:
                    combined_entry = None
                    for i, entry1 in enumerate(entries):
                        for j, entry2 in enumerate(entries):
                            entry1 = update_entity_name(entry1)
                            entry2 = update_entity_name(entry2)

                            if i < j:
                                entity_1_name = entry1['Entity Name']
                                entity_2_name = entry2['Entity Name']

                                cluster_text = entries[0]['Cluster Info']['Cluster Text']
                                combined_entity = combine_entities([entity_1_name,
                                                                    entity_2_name],
                                                                   cluster_text)

                                if is_substring(entity_1_name, entity_2_name):
                                    if len(entity_1_name) > len(entity_2_name):
                                        if entry2 in entries:
                                            entries.remove(entry2)
                                        # Coreference cluster will be used anyway -200 to
                                        # indicate merge via removal.
                                        entry1['Num Positions'] = int(MERGE_REMOVAL_INDICATOR)
                                        entry1['Positions'] = int(MERGE_REMOVAL_INDICATOR)

                                    else:
                                        if entry1 in entries:
                                            entries.remove(entry1)
                                        # Coreference cluster will be used anyway -200 to
                                        # indicate merge via removal.
                                        entry2['Num Positions'] = int(MERGE_REMOVAL_INDICATOR)
                                        entry2['Positions'] = int(MERGE_REMOVAL_INDICATOR)

                                    consolidation_done = True
                                    # exit inner for loop
                                    break
                                elif combined_entity in cluster_text:
                                    combined_entry = {
                                        'Entity Name': combined_entity,
                                        # Coreference cluster will be used anyway -100 to
                                        # indicate merge via combined entity.
                                        'Positions': int(COMBINED_REMOVAL_INDICATOR),
                                        'Label': entry1['Label'],
                                        # Coreference cluster will be used anyway -100 to
                                        # indicate merge via combined entity.
                                        'Num Positions': int(COMBINED_REMOVAL_INDICATOR),
                                        'Cluster Info': entry1['Cluster Info']
                                    }
                                    entries.remove(entry1)
                                    entries.remove(entry2)
                                    consolidation_done = True
                                    # exit inner for loop
                                    break
                        if combined_entry:
                            entries.append(combined_entry)
                        if consolidation_done:
                            # exit outer for loop
                            break

            '''
            Now look across cluster ids (above we stayed within a cluster id) for substrings of
            entity names and merge together cluster ids, positions and text.
            '''
            for cluster_id1, entries1 in cluster_dict.items():
                for cluster_id2, entries2 in cluster_dict.items():
                    if cluster_id1 != cluster_id2:  # Prevents comparing entries within the same
                        # cluster
                        for entry1 in entries1:
                            for entry2 in entries2:
                                entry1 = update_entity_name(entry1)
                                entry2 = update_entity_name(entry2)

                                entity_1_name = entry1['Entity Name']
                                entity_2_name = entry2['Entity Name']
                                # Check if an entity name is a substring of another.
                                if entity_1_name in entity_2_name or entity_2_name in entity_1_name:
                                    print('cross cluster merge triggered!')
                                    print(entity_1_name)
                                    print(entity_2_name)
                                    # Combine cluster IDs with '0000' in between as a strong
                                    # indicator.
                                    combined_cluster_id = f"{entry1['Cluster Info']['Cluster ID']}{COMBINED_CLUSTER_ID_SEPARATOR}{entry2['Cluster Info']['Cluster ID']}"

                                    # Set the new cluster ID
                                    entry1['Cluster Info']['Cluster ID'] = combined_cluster_id
                                    entry2['Cluster Info']['Cluster ID'] = combined_cluster_id

                                    # Append cluster texts and positions to entry 1.
                                    entry1['Cluster Info']['Cluster Text'].extend(
                                        entry2['Cluster Info']['Cluster Text'])
                                    entry1['Cluster Info']['Cluster Positions'].extend(
                                        entry2['Cluster Info']['Cluster Positions'])

                                    if len(entity_2_name) > len(entity_1_name):
                                        entry1['Entity Name'] = entity_2_name
                                    entries2.remove(entry2)
                                    consolidation_done = True

        clustered_entities = [entry for entries in cluster_dict.values() for entry in entries]

        before_len = len(clustered_entities)

        cleaned_entities = []

        # Resolve \n in entity name instances and any below mention threshold.
        for entity in clustered_entities:
            entity_name = entity['Entity Name']
            cleaned_name = re.split(r'\n\d*:', entity_name)[0].strip()

            entity_name = remove_titles(cleaned_name)

            '''Found 'Entity Name': 'Reginald D. Hunter’s' - handle removing 's from last word'''

            # Replaces left / right quotation mark with standard single quotation mark
            entity_name = entity_name.replace('’', "'").replace('‘', "'")

            # Handle the relatively common case of Meghan Markle '  i.e the space then quote mark
            entity_name = entity_name.rstrip("'")

            # Split the entity name into words
            words = entity_name.split()

            # Check if the last word ends with 's, and if so, remove it
            if words and words[-1].endswith("'s"):
                words[-1] = words[-1][:-2]  # Remove 's from the last word

            # Join the words back into the entity name
            cleaned_name = ' '.join(words)

            # Capitalise the first letter of each word and make the rest lowercase
            cleaned_name = ' '.join(word.capitalize() for word in words)

            # Remove spaces @ start and end string
            cleaned_name = cleaned_name.strip()

            # Replace the original entity name with the cleaned name
            entity['Entity Name'] = cleaned_name

            cluster_positions = entity['Cluster Info']['Cluster Positions']
            cluster_id = entity['Cluster Info']['Cluster ID']

            # Count the number of entries in cluster_positions
            num_entries = len(cluster_positions)

            # Check if the number of entries is below the threshold
            if num_entries < self.mention_threshold:
                print(f"Cluster ID {cluster_id} has {num_entries} entries, which is below the "
                      f"threshold of {self.mention_threshold}.")
                # print(f"Removing entity {entity['Entity Name']} with Cluster ID {cluster_id} due "
                #       f"to low mention count:")
                # print(entity['Cluster Info'])
                clustered_entities.remove(entity)
                continue

            # At most, an entity should have the first, middle and last name.
            if len(cleaned_name.split()) > 3:
                print(f"Cluster ID {cluster_id} has {num_entries} entries, which is below the "
                      f"threshold of {self.mention_threshold}.")
                print(
                    f"Removing entity {entity['Entity Name']} with Cluster ID {cluster_id} due "
                    f"to low mention count:")
                # print(entity['Cluster Info'])
                clustered_entities.remove(entity)
                continue

            # If the entity is not removed, add it to the cleaned list
            cleaned_entities.append(entity)

        clustered_entities = cleaned_entities
        new_length = len(clustered_entities)

        # print(f"number of entities before mention threshold: {before_len}")
        # print(f"number of entities after mention threshold: {new_length}")

        clustered_entities = clean_up_substrings(clustered_entities)

        self.clustered_entities = clustered_entities

        # Is this article going to go on the web app? If clustered_entities > 0 then yes so get
        # article parts and insert into database.
        if new_length > 0:
            self.set_database_candidate_true()

    def set_database_candidate_true(self):
        self.database_candidate = True

    def get_average_sentiment_results(self):
        self.sentiment_analyser.average_sentiment_results(self.database_id, self.bounds_sentiment,
                                                          self
                                                          .text_body)

    def save_to_database(self):
        try:

            self.image_url = get_preview_image_url(self.url)

            article_model = ArticleModel.objects.create(
                headline=self.headline,
                url=self.url,
                image_url=self.image_url,
                publication_date=self.publication_date,
                author=self.author,
                site_name=self.site_name
            )
            article_model.save()
            self.database_id = article_model.id

            stats_model = ArticleStatistics.objects.create(
                article=article_model,
                fuzzy_hash=self.linguistic_stats["fuzzy_hash"],
                word_count=self.linguistic_stats["word_count"],
                terms_count=self.linguistic_stats["terms_count"],
                vocd=self.linguistic_stats["vocd"],
                yulek=self.linguistic_stats["yulek"],
                simpsond=self.linguistic_stats["simpsond"],
                the_count=self.linguistic_stats["the_count"],
                and_count=self.linguistic_stats["and_count"],
                is_count=self.linguistic_stats["is_count"],
                of_count=self.linguistic_stats["of_count"],
                in_count=self.linguistic_stats["in_count"],
                to_count=self.linguistic_stats["to_count"],
                it_count=self.linguistic_stats["it_count"],
                that_count=self.linguistic_stats["that_count"],
                with_count=self.linguistic_stats["with_count"],
            )
            stats_model.save()
        except Exception as e:
            print(f"Error saving article to the database: {e}")

    def set_db_processed(self, is_processed, similar_rejection):
        if self.database_id is not None:
            try:
                ArticleModel.objects.filter(id=self.database_id).update(processed=is_processed,
                                                                        similar_rejection=
                                                                        similar_rejection)
            except ArticleModel.DoesNotExist:
                print(f"Article with id {self.database_id} does not exist.")
        else:
            print(
                "Cannot set processed and similar_rejection flags as the article obj doesn't have "
                "a database ID.")

    def get_statistics(self):
        self.linguistic_stats = calculate_statistics(self.text_body)

    def check_similarity(self):

        similar = False
        """3 days seems the appropriate trade-off given overhead of combinations vs our existing
        #  SimilarArticlePairs in publication dates."""
        # search_window = datetime.now(timezone.utc) - timedelta(days=SIMILAR_SEARCH_DAYS) SILLY SILLY SILLY!

        search_window = self.publication_date - timedelta(days=SIMILAR_SEARCH_DAYS)

        # Typically, duplicates are near in publication date!
        all_stats_window = ArticleStatistics.objects.filter(
            article__publication_date__gte=search_window
        )
        print(search_window)

        article_stats_for_this_article = ArticleStatistics.objects.filter(
            article_id=self.database_id)

        # Comparing the article_stats_for_this_article with all other stats
        for stat1, stat2 in product(all_stats_window, article_stats_for_this_article):
            fuzzy_hash1 = stat1.fuzzy_hash
            fuzzy_hash2 = stat2.fuzzy_hash

            if stat1.article_id >= stat2.article_id:
                continue

            similarity_score = ppdeep.compare(fuzzy_hash1, fuzzy_hash2)

            # Check if SimilarArticlePair already exists
            existing_pair = SimilarArticlePair.objects.filter(
                Q(Q(article1_id=stat1.article_id) & Q(article2_id=stat2.article_id)) |
                Q(Q(article1_id=stat2.article_id) & Q(article2_id=stat1.article_id)),
                Q(hash_similarity_score__gte=90) |
                (
                        Q(hash_similarity_score__gte=65, words_diff__lt=10, terms_diff__lt=10,
                          vocd_diff__lt=5, yulek_diff__lt=10, simpsond_diff__lt=10,
                          the_diff__lt=20, and_diff__lt=20, is_diff__lt=20,
                          of_diff__lt=20, in_diff__lt=20, to_diff__lt=20,
                          it_diff__lt=20, that_diff__lt=20, with_diff__lt=20
                          )
                )
            ).exists()

            if existing_pair:
                print(
                    f"Similarity pair exists between Article {stat1.article_id} and Article {stat2.article_id}. Ignoring.")
                similar = True
                return similar

            elif similarity_score >= 65:
                # Need to make a new SimilarArticlePair - this article goes into article 2 as it
                # won't have any boundSentiment data and article2 similar are skipped in django
                # views.
                pair = SimilarArticlePair(article1=stat1, article2=stat2,
                                          hash_similarity_score=similarity_score)
                pair.save()
                print(f"Similarity pair stored: {pair}")

                calculate_all_percentage_differences(pair)
                saved_pair = SimilarArticlePair.objects.get(pk=pair.id)

                # Can be a weaker strictness as this is determining whether to ignore and never
                # see again.
                # If lots of similar articles slips through we can tighten this up in
                # views command.
                if (
                        saved_pair.hash_similarity_score >= 90 or
                        (
                                saved_pair.hash_similarity_score >= 65 and
                                saved_pair.words_diff < 10 and
                                saved_pair.terms_diff < 10 and
                                saved_pair.vocd_diff < 5 and
                                saved_pair.yulek_diff < 10 and
                                saved_pair.simpsond_diff < 10 and
                                saved_pair.the_diff < 20 and
                                saved_pair.and_diff < 20 and
                                saved_pair.is_diff < 20 and
                                saved_pair.of_diff < 20 and
                                saved_pair.in_diff < 20 and
                                saved_pair.to_diff < 20 and
                                saved_pair.it_diff < 20 and
                                saved_pair.that_diff < 20 and
                                saved_pair.with_diff < 20
                        )
                ):
                    print(f"New pair meets similar criteria!")
                    similar = True
                    return similar

        return similar
