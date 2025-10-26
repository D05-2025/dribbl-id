from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from pathlib import Path
import csv

from players.models import Player

def to_float(v, default=0.0):
    if v is None:
        return default
    s = str(v).strip()
    if s in ("", "-", "NA", "None"):
        return default
    try:
        return float(s)
    except Exception:
        return default

class Command(BaseCommand):
    help = "Import NBA 2024 per-game players from CSV (Basketball-Reference style)."

    def add_arguments(self, parser):
        parser.add_argument("csv_path", nargs="?", help="Path to CSV file")
        parser.add_argument("--include-tot", action="store_true",
                            help='Include rows with Tm="TOT" (default: skipped)')

    def handle(self, *args, **options):
        rel = options.get("csv_path") or "main/management/commands/NBA_2024_per_game(03-01-2024).csv"
        p = Path(rel)
        if not p.is_absolute():
            p = Path(settings.BASE_DIR) / p
        if not p.exists():
            raise CommandError(f"File tidak ditemukan: {p}")

        include_tot = options.get("include_ttot") or options.get("include_tot")  # tolerate typo
        created = updated = 0

        self.stdout.write(self.style.NOTICE(f"Mengimpor data pemain dari: {p}"))
        with open(p, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                name = row.get("Player")
                team = row.get("Tm")
                pos  = row.get("Pos") or ""

                if not name or not team:
                    continue
                if team == "TOT" and not include_tot:
                    # lewati baris agregat supaya tidak menimpa data per tim
                    continue

                pts = to_float(row.get("PTS"))
                reb = to_float(row.get("TRB") or row.get("REB"))
                ast = to_float(row.get("AST"))

                obj, is_created = Player.objects.update_or_create(
                    name=name,
                    team=team,                # lookup unik: (name, team)
                    defaults={
                        "position": pos,
                        "points_per_game": pts,
                        "rebounds_per_game": reb,
                        "assists_per_game": ast,
                    },
                )
                created += int(is_created)
                updated += int(not is_created)

        self.stdout.write(self.style.SUCCESS(f"Selesai. Created: {created}, Updated: {updated}"))