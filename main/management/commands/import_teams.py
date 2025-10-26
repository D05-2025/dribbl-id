import csv
from django.core.management.base import BaseCommand
from teams.models import Team

class Command(BaseCommand):
    help = 'Imports data from a CSV file into Team'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='The path to the CSV file')

    def handle(self, *args, **options):
        csv_file_path = options['csv_file']

        with open(csv_file_path, 'r') as file:
            reader = csv.reader(file)
            header = next(reader)  # Skip the header row

            for row in reader:
                Team.objects.create(
                    name=row[0],
                    logo=row[1],
                    region=row[2],
                    founded=row[3],
                    description=row[4]
                )
        self.stdout.write(self.style.SUCCESS('Data imported successfully!'))