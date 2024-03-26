"""
Module: article_utils.py

The helper methods in this module help article_processor.py complete its activity.
They are standalone becuase they do not rely on 'self' context of Article objects.

Functions include checking an articles URL's fetchability against robots.txt rules,
extracting preview images from webpages, merging named entity occurrences, 
cleansing and normalizing text for better entity recognition and manipulating
textual data for enhanced processing efficiency.

"""

import re
import urllib.robotparser
from urllib.error import URLError
from urllib.parse import urlparse

from bs4 import BeautifulSoup
import requests

from .constants import (MERGE_REMOVAL_INDICATOR,
                        PREVIEW_IMG_TIMEOUT)


def can_fetch_url(url_to_check):
    """Check whether a specific URL (url_to_check) is allowed to be fetched by any web crawler
      (user-agent *) according to the website's robots.txt rules.

    Args:
        url_to_check (str): Candidate article url

    Returns:
        bool: True indicates that fetching the URL is allowed for any crawler,
              while False suggests it is disallowed.
    """
    try:
        parsed_url = urlparse(url_to_check)
        base_url = parsed_url.scheme + "://" + parsed_url.netloc
        rules = urllib.robotparser.RobotFileParser()
        rules.set_url(base_url + "/robots.txt")
        rules.read()

        if not (rules.can_fetch("*", url_to_check)):
            print("For the test case add this url as disallowed! ", url_to_check)

        return rules.can_fetch("*", url_to_check)
    except URLError as e:
        print(f"Error fetching robots.txt: {e}")
        return False


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

    return None


def merge_positions(entities, word):
    """
    Merges instances of the same named entity into a single entry within an 'entities' dictionary, 
    aggregating their occurrences throughout the document.

    Args:
        entities (dict): A dictionary where keys are entity identifiers combining the 
                         entity's text and label in lowercase, and values are lists 
                         containing the entity's original text, a list of position ranges
                         ([start_char, end_char]), and the entity's label.
        word (Token): A spaCy Token object representing an entity, with attributes for text,
                     entity label (label_), and character positions (start_char, end_char).
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
                # The first part goes from the interval's start to the value (inclusive).
                # The second part goes from the value+1 to the interval's end.
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
        clustered_entities (list): List of dictionaries representing clustered entities, 
        where each entity contains 'Cluster Info' and 'Entity Name' keys.

    Returns:
        list: List of dictionaries representing cleaned-up entities, where only the longest entity 
        names within each cluster ID are retained.

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


def clean_up_substrings_revised(clustered_entities):
    """
    ***REVISED DUE TO FAILED TEST***
    Cleans up substring entities in a list of clustered entities by keeping only the longest entity names
    within each cluster ID.

    Logic improved via testing (as bug was making it so only one cluster was impacted not all)
    so now grouping by cluster ID first.

    Args:
        clustered_entities (list): List of dictionaries representing clustered entities,
        where each entity contains 'Cluster Info' and 'Entity Name' keys.

    Returns:
        list: List of dictionaries representing cleaned-up entities, where only the longest entity
        names within each cluster ID are retained.

    Example: 'Rishi', 'Rishi Sunak' -> 'Rishi Sunak' retained 'Sunak' removed.
    """

    entities_to_keep = []

    # Group entities by their Cluster ID
    clusters = {}
    for entity in clustered_entities:
        cluster_id = entity['Cluster Info']['Cluster ID']
        if cluster_id not in clusters:
            clusters[cluster_id] = []
        clusters[cluster_id].append(entity)

    cleaned_entities = []
    for cluster_id, entities in clusters.items():
        # Find the entity with the longest name in each cluster
        longest_entity = max(entities, key=lambda e: len(e['Entity Name']))
        entities_to_keep.append(longest_entity)

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
        positions (list of list): The positions of the entity in the text.
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
