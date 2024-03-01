import requests
from django.core.management.base import BaseCommand
from nlp_processor.bing_api import get_bing_entity_info, insert_into_bing_entity_table
from profiles_app.models import Entity, BingEntity


def get_wikipedia_image_url(wiki_url):
    """
    Fetches the main image URL from a Wikipedia page using the Wikipedia API. The function
    extracts the page title from the provided Wikipedia URL, queries the Wikipedia API for
    page images, and gets main image_url.

    :param wiki_url: A string containing the full URL of the Wikipedia page from which to fetch the
                     main image.

    :return: A string containing the URL of the main image on the Wikipedia page, or None if the
             image cannot be fetched.
    """
    session = requests.Session()
    url = "https://en.wikipedia.org/w/api.php"

    # The title comes from the wiki url that the bing entity api provided me with.
    page_title = wiki_url.split("/")[-1]

    params = {
        "action": "query",
        "format": "json",
        "prop": "pageimages",
        "titles": page_title,
        "pithumbsize": 250
        # Set to 250 as that is max used on site currently - let's not get bigger than we need!
    }

    try:
        response = session.get(url=url, params=params)
        data = response.json()
        page_id = next(iter(data['query']['pages']))
        image_url = data['query']['pages'][page_id].get('thumbnail', {}).get('source', None)
        print(image_url)
        return image_url
    except Exception as e:
        print(f"Error fetching Wikipedia image: {e}")
        return None


def get_wikipedia_url_from_contractual_rules(contractual_rules):
    """
    Extracts the Wikipedia URL for an entity from its contractual rules metadata. This function
    iterates over the contractual rules provided by the Bing Entity Search API, looking for a
    media attribution rule that contains a Wikipedia URL.

    :param contractual_rules: A list or dictionary containing the contractual rules metadata
    from Bing API.
    :return: A string containing the Wikipedia URL if found; otherwise, returns None.
    """

    for rule in contractual_rules:
        if (rule.get('_type') == 'ContractualRules/MediaAttribution' and 'wikipedia.org'
                in rule.get('url', '')):
            return rule['url']
    return None


class Command(BaseCommand):
    """
    A Django management command to fetch and update Bing entity data for entities marked as visible
    within the application. For each visible entity, the command checks for existing Bing entity
    information. If found, it attempts to update the entity with a better image URL from Wikipedia.
    If not found, it fetches the data from Bing, inserts it, and then attempts the image update.
    """

    help = 'Fetch and insert Bing entity and Wikipedia source picture data for visible entities.'

    def handle(self, *args, **options):
        visible_entities = Entity.objects.filter(app_visible=True)

        for entity in visible_entities:
            entity_name = entity.name
            entity_id = entity.id
            print(entity_id)

            # Checking if BingEntity with same name already exists
            existing_bing_entity = BingEntity.objects.filter(entity=entity).first()

            if existing_bing_entity:
                print(f"Bing entity info for '{entity_name}' already exists.")

                wiki_url = get_wikipedia_url_from_contractual_rules(
                    existing_bing_entity.contractual_rules)
                if wiki_url and not existing_bing_entity.improved_image_url:
                    new_image_url = get_wikipedia_image_url(wiki_url)
                    if new_image_url:
                        existing_bing_entity.improved_image_url = new_image_url
                        existing_bing_entity.save()
                        print(f"Added an improved image URL for {entity_name}")

            else:
                bing_entity_info = get_bing_entity_info(entity_name)

                if bing_entity_info:
                    insert_into_bing_entity_table(entity_id, bing_entity_info)
                    new_bing_entity = BingEntity.objects.filter(entity=entity).first()
                    wiki_url = get_wikipedia_url_from_contractual_rules(
                        new_bing_entity.contractual_rules)
                    new_image_url = get_wikipedia_image_url(wiki_url)
                    if new_image_url:
                        existing_bing_entity.improved_image_url = new_image_url
                        existing_bing_entity.save()
                        print(f"Added an improved image URL for {entity_name}")

                else:
                    print(f"Failed to fetch Bing entity info for '{entity_name}'")
