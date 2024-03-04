"""
This module interacts with the Bing API to retrieve and manage entity and news article data for PP.

Functionality:

1. Fetch detailed information about 'app_visible' profiles from Bing's Entity Search API, including
their names, descriptions, image URLs This information is used to enrich website content and UX
by providing relevant contextual data.

2. Insert entity information fetched from Bing into a Django database,
 specifically into a table designed to store Bing entity data. This is only for entites that
 currently don't have a bing entity record to save on redundant API calls.

3. Fetch news articles related to specific search terms from Bing's News Search API.
This is utilised in a daily django job to get fresh articles to keep web app content relevant.

NB: The module's functionality is dependent on the availability and response format of the Bing
API and is subject to its rate limits (approx. 1000 free requests per month, but my Azure account has
$200 of student credit using my UoB email if search terms were increased) and terms of use.
"""

from .config import BING_API_KEY
from profiles_app.models import BingEntity, Entity
import requests
import time


def get_bing_entity_info(entity_name):
    """
    Photos (and descriptions) of an entity are a core part of website interaction the bing api
    provides these (typically Wikipedia) - since I already had a bing API key for the article
    search this seemed the least complex option.

    :param entity_name: The name of the entity to search for.
    :return: Dict or None: A dictionary containing entity details -> name, description, image URL,
    web search URL, Bing ID, contractual rules, and entity type hints or None if the entity is not
    found or an error occurs.
    """
    search_url = "https://api.bing.microsoft.com/v7.0/entities"

    headers = {
        "Ocp-Apim-Subscription-Key": BING_API_KEY,
    }

    params = {
        "q": entity_name,
        "responseFilter": "entities",
        "mkt": "en-US"
    }
    # NB: en-US Only market it works for (still has no problem with UK politicians, royals, etc.)

    try:

        print(requests.get(search_url, headers=headers, params=params))
        response = requests.get(search_url, headers=headers, params=params)
        response.raise_for_status()

        if not response.text or 'entities' not in response.json():
            # print("Invalid response format.")
            return None

        bing_data = response.json()
        print(bing_data)
        entity_info = {
            "name": bing_data['entities']['value'][0].get('name', ''),
            "description": bing_data['entities']['value'][0].get('description', ''),
            "image_url": bing_data['entities']['value'][0].get('image', {}).get('thumbnailUrl', ''),
            "web_search_url": bing_data['entities']['value'][0].get('webSearchUrl', ''),
            "bing_id": bing_data['entities']['value'][0].get('bingId', ''),
            "contractual_rules": bing_data['entities']['value'][0].get('contractualRules', []),
            "entity_type_display_hint": bing_data['entities']['value'][0].get(
                'entityPresentationInfo', {}).get('entityTypeDisplayHint', ''),
            "entity_type_hints": bing_data['entities']['value'][0].get('entityPresentationInfo',
                                                                       {}).get('entityTypeHints',
                                                                               []),
        }

        return entity_info

    except requests.exceptions.HTTPError as e:
        print(f"HTTPError: {e.response.status_code} - {e.response.text}")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

    return None


def insert_into_bing_entity_table(entity_id, bing_entity_info):
    """
    :param entity_id: The database ID of the entity in the Entity table.
    :param bing_entity_info:
    :return: A dictionary containing information about the entity retrieved
        from Bing's Entity Search API (see get_entity_info)
    """
    entity_instance = Entity.objects.get(id=entity_id)

    try:
        bing_entity = BingEntity.objects.create(
            entity=entity_instance,
            name=bing_entity_info['name'],
            description=bing_entity_info['description'],
            image_url=bing_entity_info['image_url'],
            web_search_url=bing_entity_info['web_search_url'],
            bing_id=bing_entity_info['bing_id'],
            contractual_rules=bing_entity_info['contractual_rules'],
            entity_type_display_hint=bing_entity_info['entity_type_display_hint'],
            entity_type_hints=bing_entity_info['entity_type_hints'],
        )
        print(f"Bing entity '{bing_entity.name}' inserted successfully.")
    except Exception as e:
        print(f"Error inserting Bing entity: {e}")


def entity_db_id_exists_in_bing(entity_db_id):
    """
    Check if given entity_id exists already in the Bing table.
    The purpose of this is I am limited to 1000 bing requests per month (Free Tier) and it is
    somewhat wasteful to pull the same info continuously - unless the entity has changed
    life/died etc!

    :param entity_db_id:
    :return: bool: True if the entity exists in the BingEntity table, False otherwise.
    """
    try:

        exists = BingEntity.objects.filter(entity_id=entity_db_id).exists()
        return exists
    except Exception as e:
        print("Error checking if entity_db_id exists:", e)
        return False


def fetch_articles(search_term):
    """
    Fetches news articles from Bing's News Search API based on a given search term.

    :param search_term: The term to search Bing News API for.
    :return: tuple: A tuple containing two elements; a list of dictionaries, each representing an
     article with its URL, title, and description, and a list of raw search result data from Bing.

     NB: Lack of variety (threads online discuss this) so duplicate protection in place to save on
     API calls.
     MSN has scraping protections in place or trafilatura can't read from it for some other reason.
    """

    search_url = "https://api.bing.microsoft.com/v7.0/news/search"
    headers = {"Ocp-Apim-Subscription-Key": BING_API_KEY}
    results_to_fetch = 500
    count = 100
    articles = []
    search_results_list = []
    duplicate_urls = set()
    duplicate_count = 0
    max_duplicate_count = 25
    skip_future_calls = False

    for offset in range(0, results_to_fetch, count):
        if skip_future_calls:
            break
        time.sleep(1)
        params = {
            "q": search_term,
            "count": count,
            "offset": offset,
            "freshness": "day",
            "textDecorations": True,
            "textFormat": "HTML",
            "sortBy": "Date"
        }

        try:
            response = requests.get(search_url, headers=headers, params=params)
            response.raise_for_status()
            search_results = response.json()
            search_results_list.append(search_results)

            if "value" in search_results:
                i = 0
                for article in search_results["value"]:
                    i += 1
                    # print(i)
                    url = article["url"]

                    # There have been no successful trafilatura extractions of MSN text
                    if not url.startswith("https://www.msn.com"):
                        if url in duplicate_urls:
                            duplicate_count += 1
                            if duplicate_count >= max_duplicate_count:
                                # print(f"Stopping due to {max_duplicate_count} or more duplicate
                                # URLs.")
                                skip_future_calls = True
                        else:
                            duplicate_urls.add(url)
                            duplicate_count = 0

                            title = article["name"]
                            description = article["description"]
                            articles.append(
                                {"url": url, "title": title, "description": description})
            else:
                print("No search results found.")
        except requests.exceptions.HTTPError as e:
            print(f"HTTPError: {e.response.status_code} - {e.response.text}")
        except Exception as e:
            print(f"An error occurred: {str(e)}")

    return articles, search_results_list
