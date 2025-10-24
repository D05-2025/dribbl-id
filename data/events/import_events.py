import csv
from events.models import Event

def import_events_from_csv(file_path):
    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            event, created = Event.objects.get_or_create(
                title=row['title'],
                defaults={
                    'description': row['description'],
                    'date': row['date'],
                    'time': row['time'],
                    'location': row['location'],
                    'image_url': row['image_url'],
                    'is_public': row['is_public'].strip().upper() == 'TRUE'
                }
            )

            if created:
                print(f"✅ Event '{event.title}' berhasil ditambahkan.")
            else:
                print(f"⚠️ Event '{event.title}' sudah ada, dilewati.")
