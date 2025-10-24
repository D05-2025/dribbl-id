# matches/models.py
from django.db import models
from django.core.exceptions import ValidationError
import uuid

# ---------------------------
# Master Data
# ---------------------------
class Team(models.Model):
    name = models.CharField(max_length=100, unique=True)
    city = models.CharField(max_length=100, blank=True)
    short_name = models.CharField(max_length=10, blank=True, help_text="Singkatan, mis. 'LAL', 'BOS'")

    class Meta:
        ordering = ["name"]

    def __str__(self):
        if self.short_name:
            return f"{self.short_name}"
        return self.name


class Player(models.Model):
    class Position(models.TextChoices):
        PG = "PG", "Point Guard"
        SG = "SG", "Shooting Guard"
        SF = "SF", "Small Forward"
        PF = "PF", "Power Forward"
        C  = "C",  "Center"

    team = models.CharField(max_length=100)
    full_name = models.CharField(max_length=120)
    jersey_number = models.PositiveIntegerField(null=True, blank=True)
    position = models.CharField(max_length=2, choices=Position.choices, default=Position.SG)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ("team", "full_name")
        ordering = ["team", "full_name"]

    def __str__(self):
        return f"{self.full_name} ({self.team})"


class Season(models.Model):
    """Contoh: 2025–2026"""
    name = models.CharField(max_length=30, unique=True)   # e.g. "2025/26"
    start_date = models.DateField()
    end_date = models.DateField()

    class Meta:
        ordering = ["-start_date"]

    def __str__(self):
        return self.name


# ---------------------------
# Game / Match
# ---------------------------
class Match(models.Model):
    class Status(models.TextChoices):
        SCHEDULED = "scheduled", "Scheduled"
        LIVE      = "live", "Live"
        FINISHED  = "finished", "Finished"
        CANCELED  = "canceled", "Canceled"

    uuid = models.UUIDField(editable=False, unique=True, db_index=True, default=uuid.uuid4)
    season = models.ForeignKey(Season, on_delete=models.SET_NULL, null=True, blank=True, related_name="matches")
    home_team = models.CharField(max_length=100)
    away_team = models.CharField(max_length=100)
    tipoff_at = models.DateTimeField(db_index=True, help_text="Waktu mulai pertandingan (tip-off)")
    venue = models.CharField(max_length=120, blank=True, db_index=True)
    image_url = models.URLField(blank=True, help_text="URL gambar pertandingan dari Google")
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.SCHEDULED, db_index=True)

    # Skor total
    home_score = models.PositiveSmallIntegerField(default=0)
    away_score = models.PositiveSmallIntegerField(default=0)

    # Skor per kuarter (opsional, memudahkan tampilan box score sederhana)
    q1_home = models.PositiveSmallIntegerField(null=True, blank=True)
    q1_away = models.PositiveSmallIntegerField(null=True, blank=True)
    q2_home = models.PositiveSmallIntegerField(null=True, blank=True)
    q2_away = models.PositiveSmallIntegerField(null=True, blank=True)
    q3_home = models.PositiveSmallIntegerField(null=True, blank=True)
    q3_away = models.PositiveSmallIntegerField(null=True, blank=True)
    q4_home = models.PositiveSmallIntegerField(null=True, blank=True)
    q4_away = models.PositiveSmallIntegerField(null=True, blank=True)

    # Dukungan OT (pakai sampai 3 OT, tambah lagi kalau perlu)
    ot1_home = models.PositiveSmallIntegerField(null=True, blank=True)
    ot1_away = models.PositiveSmallIntegerField(null=True, blank=True)
    ot2_home = models.PositiveSmallIntegerField(null=True, blank=True)
    ot2_away = models.PositiveSmallIntegerField(null=True, blank=True)
    ot3_home = models.PositiveSmallIntegerField(null=True, blank=True)
    ot3_away = models.PositiveSmallIntegerField(null=True, blank=True)

    class Meta:
        ordering = ["-tipoff_at"]
        constraints = [
            models.CheckConstraint(
                check=~models.Q(home_team=models.F("away_team")),
                name="match_home_neq_away",
            )
        ]
        indexes = [
            models.Index(fields=["home_team", "away_team"]),
            models.Index(fields=["status", "tipoff_at"]),
        ]

    def __str__(self):
        return f"{self.away_team} @ {self.home_team} — {self.tipoff_at:%Y-%m-%d %H:%M}"

    @property
    def went_to_ot(self) -> bool:
        return any(v is not None for v in [self.ot1_home, self.ot1_away, self.ot2_home, self.ot2_away, self.ot3_home, self.ot3_away])

    def recalc_totals_from_periods(self, save=True):
        """Opsional helper untuk menjumlah ulang total dari per-kuarter/OT."""
        parts_home = [self.q1_home, self.q2_home, self.q3_home, self.q4_home, self.ot1_home, self.ot2_home, self.ot3_home]
        parts_away = [self.q1_away, self.q2_away, self.q3_away, self.q4_away, self.ot1_away, self.ot2_away, self.ot3_away]
        self.home_score = sum(p or 0 for p in parts_home)
        self.away_score = sum(p or 0 for p in parts_away)
        if save:
            self.save(update_fields=["home_score", "away_score"])
    
    @property
    def is_live(self) -> bool:
        return self.status == self.Status.LIVE

    @property
    def is_finished(self) -> bool:
        return self.status == self.Status.FINISHED

    @property
    def is_scheduled(self) -> bool:
        return self.status == self.Status.SCHEDULED


# ---------------------------
# Box Score (stat pemain per pertandingan)
# ---------------------------
class PlayerBoxScore(models.Model):
    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name="box_scores")
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name="box_scores")
    team = models.CharField(max_length=100)

    # Basic info
    is_starter = models.BooleanField(default=False)
    minutes = models.DecimalField(max_digits=4, decimal_places=2, default=0.0, help_text="Menit bermain (desimal, mis. 32.5 untuk 32:30)")

    # Scoring
    pts = models.PositiveSmallIntegerField(default=0)
    reb = models.PositiveSmallIntegerField(default=0)
    ast = models.PositiveSmallIntegerField(default=0)
    stl = models.PositiveSmallIntegerField(default=0)
    blk = models.PositiveSmallIntegerField(default=0)
    tov = models.PositiveSmallIntegerField(default=0)
    pf = models.PositiveSmallIntegerField(default=0)

    # Shooting stats
    fg_made = models.PositiveSmallIntegerField(default=0)
    fg_att = models.PositiveSmallIntegerField(default=0)
    tp_made = models.PositiveSmallIntegerField(default=0)
    tp_att = models.PositiveSmallIntegerField(default=0)
    ft_made = models.PositiveSmallIntegerField(default=0)
    ft_att = models.PositiveSmallIntegerField(default=0)

    # Advanced
    plus_minus = models.SmallIntegerField(default=0)

    class Meta:
        unique_together = ("match", "player")
        ordering = ["-is_starter", "-minutes", "player__full_name"]
        indexes = [
            models.Index(fields=["match", "team"]),
            models.Index(fields=["player"]),
        ]

    def __str__(self):
        return f"{self.player} - {self.match}"

    @property
    def fg_pct(self) -> float:
        return self.fg_made / self.fg_att if self.fg_att > 0 else 0.0

    @property
    def tp_pct(self) -> float:
        return self.tp_made / self.tp_att if self.tp_att > 0 else 0.0

    @property
    def ft_pct(self) -> float:
        return self.ft_made / self.ft_att if self.ft_att > 0 else 0.0

