from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from players.models import Player
from pathlib import Path
import csv

class Command(BaseCommand):
    help = "Import player statistics from a CSV file (NBA 2024)"

    def add_arguments(self, parser):
        parser.add_argument("csv_path", nargs="?", help="Path to CSV file")

    def handle(self, *args, **options):
        csv_path = options.get("csv_path") or "main/management/commands/NBA_2024_per_game(03-01-2024).csv"
        p = Path(csv_path)
        if not p.is_absolute():
            p = Path(settings.BASE_DIR) / p

        if not p.exists():
            raise CommandError(f"File tidak ditemukan: {p}")

        self.stdout.write(self.style.NOTICE(f"Mengimpor data pemain dari: {p}"))

        with open(p, newline='', encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            count = 0
            for row in reader:
                # Mapping ke model Player — sesuaikan dengan kolom di CSV
                Player.objects.update_or_create(
                    full_name=row.get("Player"),
                    defaults={
                        "team": row.get("Tm", ""),
                        "position": row.get("Pos", ""),
                        "jersey_number": 0,  # opsional
                        "is_active": True,
                    },
                )
                count += 1

        self.stdout.write(self.style.SUCCESS(f"Import selesai! Total {count} pemain diimpor."))