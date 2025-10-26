from django.core.management.base import BaseCommand
from players.models import Player
import csv

class Command(BaseCommand):
    help = 'Import NBA players data from CSV'

    def handle(self, *args, **kwargs):
        file_path = 'NBA_2024_per_game(03-01-2024).csv'  # pastikan nama file sama
        with open(file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            Player.objects.all().delete()  # opsional: hapus data lama

            for row in reader:
                Player.objects.create(
                    name=row['Player'],
                    position=row['Pos'],
                    team=row['Tm'],
                    points_per_game=float(row['PTS']),
                    assists_per_game=float(row['AST']),
                    rebounds_per_game=float(row['TRB'])
                )
        self.stdout.write(self.style.SUCCESS('✅ Players imported successfully!'))
