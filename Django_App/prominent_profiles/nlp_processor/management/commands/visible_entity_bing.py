from django.core.management.base import BaseCommand
from profiles_app.models import Entity, BingEntity
from nlp_processor.bing_api import get_bing_entity_info, insert_into_bing_entity_table


class Command(BaseCommand):
    help = 'Fetch and insert Bing entity data for visible entities.'

    def handle(self, *args, **options):
        visible_entities = Entity.objects.filter(app_visible=True)

        for entity in visible_entities:
            entity_name = entity.name
            entity_id = entity.id
            print(entity_id)

            # Checking if BingEntity with same name already exists
            existing_bing_entity = BingEntity.objects.filter(name=entity_name).first()

            if existing_bing_entity:
                print(f"Bing entity info for '{entity_name}' already exists.")
            else:
                bing_entity_info = get_bing_entity_info(entity_name)

                if bing_entity_info:
                    insert_into_bing_entity_table(entity_id, bing_entity_info)

                else:
                    print(f"Failed to fetch Bing entity info for '{entity_name}'")


