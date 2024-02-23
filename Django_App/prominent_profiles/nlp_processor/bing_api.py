from .config import BING_API_KEY
from profiles_app.models import BingEntity, Entity
import requests
import time


def get_bing_entity_info(entity_name):
    search_url = "https://api.bing.microsoft.com/v7.0/entities"

    headers = {
        "Ocp-Apim-Subscription-Key": BING_API_KEY,
    }

    params = {
        "q": entity_name,
        "responseFilter": "entities",
        "mkt": "en-US"
    }

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
    try:
        # Check if given entity_id exists already in the Bing table
        exists = BingEntity.objects.filter(entity_id=entity_db_id).exists()
        return exists
    except Exception as e:
        print("Error checking if entity_db_id exists:", e)
        return False


# ---------
# Adapt for Django

def fetch_articles(search_term):
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
                    print(i)
                    url = article["url"]

                    if not url.startswith("https://www.msn.com"):
                        if url in duplicate_urls:
                            duplicate_count += 1
                            if duplicate_count >= max_duplicate_count:
                                print(
                                    f"Stopping due to {max_duplicate_count} or more duplicate URLs.")
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
