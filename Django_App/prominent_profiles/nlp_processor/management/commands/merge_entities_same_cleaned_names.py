from collections import defaultdict

from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand
from django.db import transaction
from profiles_app.models import Entity, BoundMention, BingEntity, OverallSentiment

from Django_App.prominent_profiles.profiles_app.models import EntityHistory


def clean_entity_name(entity_name):
    """
    This is the improved clean entity process that has now been adopted as of 20th Jan into the
    main pipeline, but I wanted to resolve these issues on the current database.
    """

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

    # Remove spaces at the start and end of the string
    cleaned_name = cleaned_name.strip()

    return cleaned_name


class Command(BaseCommand):
    help = 'Merge entities with the same cleaned names'

    """
    Cleans and organises entities by their cleaned name.
    Iterates over entities that match when cleaned.
    Merges into master entity.
    This *should* be a one-off as clean_entity_name functionality is in main job now
    """

    def handle(self, *args, **options):
        entities = Entity.objects.all()

        entities_by_cleaned_name = defaultdict(list)

        for entity in entities:
            cleaned_name = clean_entity_name(entity.name)
            entities_by_cleaned_name[cleaned_name].append(entity)

        for cleaned_name, entity_list in entities_by_cleaned_name.items():

            if len(entity_list) > 1:
                print(" ")
                input("Press Enter to continue...")
                self.stdout.write(self.style.SUCCESS("Continuing with the rest of the script..."))
                print(" ")
                for i in range(len(entity_list)):
                    for j in range(i + 1, len(entity_list)):

                        master_entity = entity_list[i]
                        secondary_entity = entity_list[j]

                        print(f"Master Entity: {master_entity.name}")
                        print(f"Secondary Entity: {secondary_entity.name}")

                        with transaction.atomic():
                            try:
                                # Update references
                                if BoundMention.objects.filter(entity=secondary_entity).exists():
                                    BoundMention.objects.filter(entity=secondary_entity).update(
                                        entity=master_entity)

                                if OverallSentiment.objects.filter(
                                        entity=secondary_entity).exists():
                                    OverallSentiment.objects.filter(entity=secondary_entity).update(
                                        entity=master_entity)

                                if BingEntity.objects.filter(entity=secondary_entity).exists():
                                    BingEntity.objects.filter(entity=secondary_entity).update(
                                        entity=master_entity)

                                if EntityHistory.objects.filter(
                                        merged_into=secondary_entity).exists():
                                    EntityHistory.objects.filter(
                                        merged_into=secondary_entity).update(
                                        merged_into=master_entity)

                                # Master entity inheritance
                                master_entity.name = f"{master_entity.name}"
                                master_entity.type = master_entity.type or secondary_entity.type
                                master_entity.app_visible = master_entity.app_visible or secondary_entity.app_visible

                                # Save changes, delete secondary
                                master_entity.save()

                                if Entity.objects.filter(pk=secondary_entity.pk).exists():
                                    secondary_entity.delete()

                                self.stdout.write(self.style.SUCCESS(
                                    f"Entities {master_entity.name} and {secondary_entity.name} "
                                    f"merged successfully."))

                            except ObjectDoesNotExist as e:
                                self.stdout.write(self.style.WARNING(
                                    f"Skipping merge for {master_entity.name} and {secondary_entity.name}: {e}"))

#  Example Runs...

#   ameek@Anthonys-Laptop prominent_profiles % python manage.py merge_entities_same_cleaned_names
#
#
# Master Entity: David Cameron
# Secondary Entity: David Cameron '
#
#
# Master Entity: Rishi Sunak '
# Secondary Entity: Rishi Sunak
# Master Entity: Rishi Sunak '
# Secondary Entity: Rishi Sunak
# Master Entity: Rishi Sunak
# Secondary Entity: Rishi Sunak
#
#
# Master Entity: Donald Tusk
# Secondary Entity: Donald Tusk '
#
#
# Master Entity: Robert Jenrick
# Secondary Entity: Robert Jenrick '
#
#
# Master Entity: Prince William
# Secondary Entity: Prince William '
# Master Entity: Prince William
# Secondary Entity: Prince William
# Master Entity: Prince William
# Secondary Entity: Prince William's '
# Master Entity: Prince William '
# Secondary Entity: Prince William
# Master Entity: Prince William '
# Secondary Entity: Prince William's '
# Master Entity: Prince William
# Secondary Entity: Prince William's '
#
#
# Master Entity: Prince Harry
# Secondary Entity: Prince Harry'
# Master Entity: Prince Harry
# Secondary Entity: Prince Harry '
# Master Entity: Prince Harry
# Secondary Entity: Prince Harry
# Master Entity: Prince Harry'
# Secondary Entity: Prince Harry '
# Master Entity: Prince Harry'
# Secondary Entity: Prince Harry
# Master Entity: Prince Harry '
# Secondary Entity: Prince Harry
#
#
# Master Entity: King Charles'
# Secondary Entity: King Charles
#
#
# Master Entity: Omid Scobie
# Secondary Entity: Omid Scobie '
#
#
# Master Entity: Meghan Markle '
# Secondary Entity: Meghan Markle


# ------------------------------------


# (Project) ameek@Anthonys-Laptop prominent_profiles % python manage.py merge_entities_same_cleaned_names
#
# Press Enter to continue...
# Continuing with the rest of the script...
#
# Master Entity: King Charles'
# Secondary Entity: King Charles
# Entities King Charles' and King Charles merged successfully.
#
# Press Enter to continue...
# Continuing with the rest of the script...
#
# Master Entity: Omid Scobie
# Secondary Entity: Omid Scobie '
# Entities Omid Scobie and Omid Scobie ' merged successfully.
#
# Press Enter to continue...
# Continuing with the rest of the script...
#
# Master Entity: Meghan Markle '
# Secondary Entity: Meghan Markle
# Entities Meghan Markle ' and Meghan Markle merged successfully.
# Master Entity: Meghan Markle '
# Secondary Entity: Meghan Markle
# Entities Meghan Markle ' and Meghan Markle  merged successfully.
# Master Entity: Meghan Markle '
# Secondary Entity: Meghan Markle'
# Entities Meghan Markle ' and Meghan Markle' merged successfully.
# Master Entity: Meghan Markle
# Secondary Entity: Meghan Markle
# Entities Meghan Markle and Meghan Markle  merged successfully.
# Master Entity: Meghan Markle
# Secondary Entity: Meghan Markle'
# Entities Meghan Markle and Meghan Markle' merged successfully.
# Master Entity: Meghan Markle
# Secondary Entity: Meghan Markle'
# Entities Meghan Markle  and Meghan Markle' merged successfully.
#
# Press Enter to continue...
# Continuing with the rest of the script...
#
# Master Entity: Ellen Degeneres
# Secondary Entity: Ellen Degeneres'
# Entities Ellen Degeneres and Ellen Degeneres' merged successfully.
#
# Press Enter to continue...
# Continuing with the rest of the script...
#
# Master Entity: Kate Middleton
# Secondary Entity: Kate Middleton '
# Entities Kate Middleton and Kate Middleton ' merged successfully.
#
# Press Enter to continue...
# Continuing with the rest of the script...
#
# Master Entity: Fiona Brown
# Secondary Entity: Fiona Brown '
# Entities Fiona Brown and Fiona Brown ' merged successfully.
#
# Press Enter to continue...
# Continuing with the rest of the script...
#
# Master Entity: The Sussexes
# Secondary Entity: The Sussexes'
# Entities The Sussexes and The Sussexes' merged successfully.
#
# Press Enter to continue...
# Continuing with the rest of the script...
#
# Master Entity: Welsh Labour
# Secondary Entity: Welsh Labour '
# Entities Welsh Labour and Welsh Labour ' merged successfully.
#
# Press Enter to continue...
# Continuing with the rest of the script...
#
# Master Entity: Harry Styles
# Secondary Entity: Harry Styles'
# Entities Harry Styles and Harry Styles' merged successfully.
#
# Press Enter to continue...
# Continuing with the rest of the script...
#
# Master Entity: Selena Gomez's '
# Secondary Entity: Selena Gomez
# Entities Selena Gomez's ' and Selena Gomez merged successfully.
#
# Press Enter to continue...
# Continuing with the rest of the script...
#
# Master Entity: Sarah Ferguson
# Secondary Entity: Sarah Ferguson '
# Entities Sarah Ferguson and Sarah Ferguson ' merged successfully.
#
# Press Enter to continue...
# Continuing with the rest of the script...
#
# Master Entity: Harry Potter
# Secondary Entity: Harry Potter'
# Entities Harry Potter and Harry Potter' merged successfully.
#
# Press Enter to continue...
# Continuing with the rest of the script...
#
# Master Entity: Donald Trump
# Secondary Entity: Donald Trump
# Entities Donald Trump and Donald Trump  merged successfully.
#
# Press Enter to continue...
# Continuing with the rest of the script...
#
# Master Entity: Patrick Hillery
# Secondary Entity: Patrick Hillery
# Entities Patrick Hillery and Patrick Hillery merged successfully.
#
# Press Enter to continue...
# Continuing with the rest of the script...
#
# Master Entity: President Trump
# Secondary Entity: President Trump
# Entities President Trump and President Trump merged successfully.
#
# Press Enter to continue...
# Continuing with the rest of the script...
#
# Master Entity: Paula Vennells
# Secondary Entity: Paula Vennells'
# Entities Paula Vennells and Paula Vennells' merged successfully.
#
# Press Enter to continue...
# Continuing with the rest of the script...
#
# Master Entity: Michael Shanks'
# Secondary Entity: Michael Shanks
# Entities Michael Shanks' and Michael Shanks merged successfully.
#
# Press Enter to continue...
# Continuing with the rest of the script...
#
# Master Entity: Tina Fey
# Secondary Entity: Tina Fey's '
# Entities Tina Fey and Tina Fey's ' merged successfully.
