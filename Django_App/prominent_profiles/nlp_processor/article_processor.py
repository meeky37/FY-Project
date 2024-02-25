import math
import re
from collections import defaultdict
from datetime import timedelta
from functools import reduce
from itertools import product
import urllib.robotparser
from urllib.parse import urlparse

from bs4 import BeautifulSoup
import ppdeep
import requests
from textblob import TextBlob

from django.core.exceptions import ValidationError
from django.db import IntegrityError, OperationalError, DataError
from django.db.models import Q

from nlp_processor.sentiment_resolver import SentimentAnalyser
from profiles_app.models import Article as ArticleModel
from .article_update import calculate_statistics, calculate_all_percentage_differences
from .constants import (ENTITY_THRESHOLD_PERCENT,
                        MENTION_REQ_PER,
                        MERGE_REMOVAL_INDICATOR,
                        COMBINED_REMOVAL_INDICATOR,
                        COMBINED_CLUSTER_ID_SEPARATOR,
                        SIMILAR_SEARCH_DAYS,
                        PREVIEW_IMG_TIMEOUT)
from .models import ArticleStatistics, SimilarArticlePair


def can_fetch_url(url_to_check):
    """Check whether a specific URL (url_to_check) is allowed to be fetched by any web crawler
      (user-agent *) according to the website's robots.txt rules.
    
    Args:
        url_to_check (str): Candidate article url

    Returns:
        bool: True indicates that fetching the URL is allowed for any crawler,
              while False suggests it is disallowed.
    """
    parsed_url = urlparse(url_to_check)
    base_url = parsed_url.scheme + "://" + parsed_url.netloc
    rules = urllib.robotparser.RobotFileParser()
    rules.set_url(base_url + "/robots.txt")
    rules.read()
    return rules.can_fetch("*", url_to_check)


def get_preview_image_url(url):
    """
    Fetches the preview image URL from a given webpage.

    Args:
        url (str): The URL of the webpage.

    Returns:
        str: The URL of the preview image, or an empty string if not found.
    """

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

    except requests.exceptions.Timeout:
        print(f"Error fetching preview image URL ({url}): [Timeout error].")
    except requests.exceptions.HTTPError as e:
        print(f"Error fetching preview image URL ({url}): [HTTP error ({e.response.status_code})].")
    except requests.exceptions.ConnectionError:
        print(f"Error fetching preview image URL ({url}): [Connection error].")
    except requests.exceptions.RequestException:
        print(f"Error fetching preview image URL ({url}): [General request exception].")
    except Exception as e:
        print(f"Error fetching preview image URL ({url}): [Unexpected error: {e}].")


def merge_positions(entities, word):
    """
    Merges instances of the same named entity into a single entry within an 'entities' dictionary, 
    aggregating their occurrences throughout the document.

    Args:
        entities (dict): A dictionary where keys are entity identifiers combining the 
                         entity's text and label in lowercase, and values are lists 
                         containing the entity's original text, a list of position ranges
                         ([start_char, end_char]), and the entity's label.
        word (Token): A spaCy Token object representing an entity, with attributes for text, entity label (label_),
                      and character positions (start_char, end_char).
    Returns:
        dict: The updated 'entities' dictionary with consolidated positions for each named entity.
    """    
    
    entity_key = (word.text + word.label_).lower()
    if entity_key in entities:
        entities[entity_key][1].append([word.start_char, word.end_char])
    else:
        entities[entity_key] = [word.text, [[word.start_char, word
        .end_char]], word.label_]
    return entities


def cleanse_cluster_text(cluster_text):
    """
    Helper function. Cleanses the text of a cluster by filtering out common stopwords
    that are not useful for the purposes of entity recognition and cluster matching. 
    By eliminating these words, the remaining text is more meaningful for identifying
    and matching entities to clusters based on significant content.

    
    Args:
        cluster_text (list of str): The original text of the cluster as a list, where each
                                    element is a word from the cluster.

    Returns:
        list of str: A cleansed list of words from the cluster, with undesired words removed.
    """       
    
    undesired_words = ["i", "he", "his", "she", "they", "it", "this", "that",
                   "these", "those", "the", "a", "an", "of"]

    return [word.strip() for word in cluster_text if word.lower().strip() not
            in undesired_words]



def remove_titles(text):

    """
    Normalises entity name by removing titles facilitating more accurate matching. 
    Entity to cluster matching prefers 2 words i.e hoping for a first and second name.
    Removing the title could reduce an entry for 3 to 2 words.
    
    Args:
        text (str): The original text from which titles and honorifics are to be removed.

    Returns:
        str: The text with common titles and honorifics removed from its beginning and specific titles 
             removed from its end.

    Example: 10th Nov:
    {'Entity Name': 'Keith', 'Positions': [[11664, 11669], [12301, 12306], [14453, 14458], 
    [15005, 15010], [15286, 15291]], 'Label': 'PERSON', 'Num Positions': 5, 'Cluster Info': 
    {'Cluster ID': 12, 'Cluster Text': ['Keith', 'Keith', 'Keith', 'Keith', 'Hugo Keith KC',
    'Keith', 'Keith', 'Keith'], 'Cluster Positions': [(11664, 11669), (12301, 12306), 
    (12312, 12314), (13026, 13031), (13464, 13469), (14374, 14387), (14453, 14458),
    (15005, 15010), (15286, 15291)]}}
    would have been updated to Hugo Keith had it not been for KC which made it 3 words"""
       
    title_pattern = r"^(Mr|Mrs|Ms|Miss|Dr|Prof|Rev|Capt|Sir|Madam|Mx|Esq|Hon|Gen|Col|Sgt|Fr|Sr|Jr|Lord|Lady)\s"
    text = re.sub(title_pattern, "", text)

    # Pattern for titles at the end
    title_pattern_end = r"\s*(KC|QC)\s*$"
    text = re.sub(title_pattern_end, "", text)
    return text


def insert_intervals(initial_list, new_values):
    """The insert_intervals function enables the segmentation of sentences provided by
    TextBlob (as shown in the cell below) to be further divided into smaller boundaries. This
     division is based on the identification of specific points where it is deemed necessary
     to split sentences, particularly within the context of news articles.
     
    Args:
        initial_list (list of tuple): Initial sentence boundaries as a list of (start, end) tuples.
        new_values (list): Positions at which to insert new sentence boundaries, based on specific textual patterns.

    Returns:
        list of tuple: Updated list of sentence boundaries, including the newly inserted boundary points.

    Example:
    initial_list = [(0, 50), (51, 100), (101, 150)]
    new_values = [75, 120] e.g. New line and hyphen points
    updated_list = [(0, 50), (51, 75), (76, 100), (101, 120), (121, 150)]
     """

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
    """
    Check if either entity is a substring of the other, case-insensitively.

    Args:
        entity1 (str): The first entity to compare.
        entity2 (str): The second entity to compare.

    Returns:
        bool: True if either entity1 is a substring of entity2 or vice versa; False otherwise.
    """
    return entity1.lower() in entity2.lower() or entity2.lower() in entity1.lower()

def combine_entities(entities, cluster_text):
    """
    Combines two or more entities into a single entity if their concatenated form is found
    within the cluster text. Helps handle cases where individual names or titles are 
    mentioned separately but refer to the same entity in context.

    Args:
        entities (list): A list of entity names (strings) to be combined.
        cluster_text (str): The text of the cluster containing the entities, used to verify
                            the combined form's presence.

    Returns:
        str: The combined entity name if the concatenation is found in the cluster text;
             otherwise, returns an empty string.
    """

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
    """
    Calls remove titles and removes possessive punctation before checking if an entity name is a
     substring of a 2 word entry in the coref cluster e.g. Johnson should become Boris Johnson
     
    Args:
        entry (dict): A dictionary representing an entity entry, with keys 'Entity Name'
                      and 'Cluster Info' containing cluster text.

    Returns:
        dict: The updated entry with potentially modified 'Entity Name'.
    """

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
    """
    Cleans up substring entities in a list of clustered entities by keeping only the longest entity names
    within each cluster ID. 

    Args:
        clustered_entities (list): List of dictionaries representing clustered entities, where each entity
                                   contains 'Cluster Info' and 'Entity Name' keys.

    Returns:
        list: List of dictionaries representing cleaned-up entities, where only the longest entity names
              within each cluster ID are retained.

    Example: 'Rishi', 'Rishi Sunak' -> 'Rishi Sunak' retained 'Sunak' removed.
    """
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
    """
    Create a dictionary representing an entity entry with the provided parameters.

    Args:
        entity_name (str): The name of the entity.
        positions (int): The positions of the entity.
        label (str): The label of the entity.
        num_positions (int): The number of positions of the entity.

    Returns:
        dict: A dictionary representing the entity entry.
    """

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

        """
            Sets the sentiment analyser for the article object. In the context of a Django job where
            declaring a sentiment analyser class is expensive due to the initialisation of `TargetSentimentClassifier`
            with PyTorch, this method aims to optimise memory usage and performance.

            Previously, each article object instantiated its own sentiment analyser, leading to high memory
            consumption and extra delay for each first-time NewsSentiment use. 
            
            This method allows for the reuse of a sentiment analyser instance.

            If `sa` (sentiment analyser) is `None`, a new `SentimentAnalyser` instance is created and assigned.
            Otherwise, the provided `sa` instance is assigned directly.

            Args:
                sa (SentimentAnalyser or None): The sentiment analyser instance to be set. If `None`, a new
                                                `SentimentAnalyser` instance will be created.

            Returns:
                None
        """
    
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

        for entities in self.people_entities.items():
            for entity in entities:
                entity_name, positions, label, num_positions = entity
                entity_entry = create_entity_entry(entity_name, positions, label,
                                                   num_positions)
                self.process_clusters_for_entity(entity_entry, entity_name)

    def process_clusters_for_entity(self, entity_entry, entity_name):
        cluster_id = 0
        for (cluster_text, cluster_positions, _) in self.coref_clusters:
            cluster_id += 1

            cluster_text = cleanse_cluster_text(cluster_text)
            cleaned_cluster_text = [remove_titles(text) for text in cluster_text]

            # Check if the length of cleaned_cluster_text is less than 4 elements
            if len(cleaned_cluster_text) < 4:
                continue  # Skip this cluster and move to the next one

            total_coref_words = " ".join(cleaned_cluster_text)
            entity_parts = entity_name.split()
            max_percentage = 0.0

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
        """Add an ID to each cluster"""
        self.coref_clusters = list(enumerate(sorted_combined_clusters))

    def source_ner_people(self):

        """SpaCy is a popular NLP library that offers pre-trained models for various languages, and
            its NER component is capable of recognising and categorising named entities within text.
            It is utilised here to identify PERSON entities"""

        NER = self.NER
        article_text = self.text_body
        article = NER(article_text)

        # Recommended mention - 'Discard a cluster c in a document d if |Mc| ≤ 0.2|Sd|,  
        # where |...| is the number of mentions of a cluster (Mc) and sentences in a document (Sd)
        # (NEWS-MTSC approach)

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
        # In testing article a new line and '-' hyphen use typically means consider
        # a different sentence (e.g Daily Mail articles).
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

                
        Modifies:
        - Updates `self.entity_to_cluster_mapping` by consolidating entities based on the criteria
        mentioned above. This attribute should be a list of dictionaries, each representing an 
        entity with keys for 'Entity Name', 'Cluster Info', and related attributes.
        - Alters `self.clustered_entities` to reflect the consolidated state of entities, removing
        duplicates and updating entity names as necessary.

        """

        cluster_dict = defaultdict(list)
        for entry in self.entity_to_cluster_mapping:
            entity_name = entry['Entity Name']
            cluster_id = entry['Cluster Info']['Cluster ID']
            cluster_dict[cluster_id].append(entry)

        # First look within each cluster for substrings of
        # entity names to help merge together positions and text
        # -> Intra-cluster Consolidation

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

            # Now look across cluster ids (above we stayed within a cluster id) for substrings of
            # entity names and merge together cluster ids, positions and text.
            # -> Inter-cluster Consolidation
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
                                    
                                    # Combine cluster IDs with '0000' in between as a combination flag.
                                    combined_cluster_id = (
                                        f"{entry1['Cluster Info']['Cluster ID']}"
                                        f"{COMBINED_CLUSTER_ID_SEPARATOR}"
                                        f"{entry2['Cluster Info']['Cluster ID']}"
                                    )
                                    
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

            # Found 'Entity Name': 'Reginald D. Hunter’s' - handle removing 's from last word

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
                # print(f"Cluster ID {cluster_id} for entity {entity['Entity Name']} has {num_entries} entries, which is below the "
                #       f"threshold of {self.mention_threshold}.")
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
            self.set_database_candidate_true() # Redundant now we add at similarity stage anyway

    def set_database_candidate_true(self):
        """
        Legacy method really - database insertion used to depend on entity threshold being met.
        Now all articles that have article text extracted over 250 are stored but they might 
        be rejected from processing by 'similar_rejection" -> see scrape_articles_concurrent.py.

        Needed to store all articles for foreign reference in SimilarArticlePair model.
        """
        self.database_candidate = True

    def get_average_sentiment_results(self):
        "Getter for average sentiment results -> see sentiment analyser class"
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

        except IntegrityError as e:
            print(f"Database integrity error saving article/stats to the database: {e}")
        except ValidationError as e:
            print(f"Validation error saving article/stats to the database: {e}")
        except OperationalError as e:
            print(f"Database operational error saving article/stats to the database: {e}")
        except DataError as e:
            print(f"Database data error saving article/stats to the database: {e}")
        except (ValueError, TypeError) as e:
            print(f"Value or type error saving article/stats to the database: {e}")

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
        """
        Checks for similarity by comparing the current article with other recently published articles
        in terms of fuzzy hashing, and percentage differences in lingustic features. 
        
        It also checks for the existence of similar article pairs - which was useful for running on my existing database
        before this was incorporated into the scrape_articles_concurrent daily job. 

        The comparison includes metrics such as the percentage difference in the occurrences of words like "the",
        "and", "is", "of", "in", "to", "it", "that", and "with".

        If a similarity threshold is met, the method returns True, indicating a similar article is found.

        Returns:
            bool: True if a similar article is found, False otherwise.
        """

        similar = False
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
                # views command due to the choice of just 65 for storing potential similar pairs
                # in the database.
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
                    print("New pair meets similar criteria!")
                    similar = True
                    return similar

        return similar
