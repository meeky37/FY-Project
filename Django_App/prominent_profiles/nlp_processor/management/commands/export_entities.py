
import csv
from django.core.management.base import BaseCommand
from profiles_app.models import Entity

class Command(BaseCommand):
    help = 'Export entities to a CSV file'

    def handle(self, *args, **options):
        entities = Entity.objects.all()

        csv_file_path = 'entities.csv'

        with open(csv_file_path, 'w', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow(['ID', 'Name'])

            for entity in entities:
                csv_writer.writerow([entity.id, entity.name])

        self.stdout.write(self.style.SUCCESS(f'Successfully exported entities to {csv_file_path}'))