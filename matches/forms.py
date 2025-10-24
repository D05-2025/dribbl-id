from django import forms
from .models import Team, Player, Match, PlayerBoxScore
from django.db.models import Q


# --- Tambahkan util kelas dark ---
_BASE_INPUT  = "block w-full rounded-md bg-neutral-900 text-neutral-100 placeholder-neutral-400 border border-neutral-700 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/40 px-3 py-2"
_BASE_SELECT = _BASE_INPUT + " appearance-none"


# =========================
# Team & Player
# =========================
class TeamForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = ["name", "city", "short_name"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # urutkan pilihan otomatis
        self.fields["name"].widget.attrs.update({"placeholder": "Nama tim", "class": _BASE_INPUT})
        self.fields["city"].widget.attrs.update({"placeholder": "Kota (opsional)", "class": _BASE_INPUT})
        self.fields["short_name"].widget.attrs.update({"placeholder": "Singkatan (3–5 huruf)", "class": _BASE_INPUT})


class PlayerForm(forms.ModelForm):
    team = forms.CharField(max_length=100, label="Team")

    class Meta:
        model = Player
        fields = ["team", "full_name", "jersey_number", "position", "is_active"]
        widgets = {
            "jersey_number": forms.NumberInput(attrs={"min": 0, "step": 1}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["team"].widget.attrs.update({"placeholder": "Nama tim", "class": _BASE_INPUT})
        self.fields["full_name"].widget.attrs.update({"placeholder": "Nama lengkap", "class": _BASE_INPUT})
        self.fields["jersey_number"].widget.attrs.update({"class": _BASE_INPUT})
        self.fields["position"].widget.attrs.update({"class": _BASE_SELECT})
        self.fields["is_active"].widget.attrs.update({"class": "h-4 w-4"})


# =========================
# Match
# =========================
class MatchForm(forms.ModelForm):
    home_team = forms.CharField(max_length=100, label="Home Team")
    away_team = forms.CharField(max_length=100, label="Away Team")

    class Meta:
        model = Match
        fields = ["home_team", "away_team", "tipoff_at", "venue", "image_url", "status"]
        widgets = {
            "tipoff_at": forms.DateTimeInput(attrs={"type": "datetime-local"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["home_team"].widget.attrs.update({"placeholder": "Nama tim kandang", "class": _BASE_INPUT})
        self.fields["away_team"].widget.attrs.update({"placeholder": "Nama tim tandang", "class": _BASE_INPUT})

    def clean(self):
        cleaned = super().clean()
        h = cleaned.get("home_team")
        a = cleaned.get("away_team")
        if h and a and h == a:
            self.add_error("away_team", "Tim kandang dan tandang tidak boleh sama.")
        return cleaned



class MatchScoreForm(forms.ModelForm):
    class Meta:
        model = Match
        fields = [
            "q1_home", "q1_away", "q2_home", "q2_away",
            "q3_home", "q3_away", "q4_home", "q4_away",
            "ot1_home", "ot1_away", "ot2_home", "ot2_away", "ot3_home", "ot3_away",
        ]
        widgets = {
            k: forms.NumberInput(attrs={"min": 0, "step": 1})
            for k in [
                "q1_home","q1_away","q2_home","q2_away","q3_home","q3_away","q4_home","q4_away",
                "ot1_home","ot1_away","ot2_home","ot2_away","ot3_home","ot3_away",
            ]
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for f in self.fields.values():
            f.widget.attrs.update({"class": _BASE_INPUT})

# =========================
# Player Box Score
# =========================

class PlayerBoxScoreForm(forms.ModelForm):
    # Player sebagai dropdown
    player = forms.ModelChoiceField(
        queryset=Player.objects.none(),  # akan di-set di __init__
        empty_label="Pilih pemain…",
        label="Player",
        widget=forms.Select(attrs={"class": _BASE_SELECT}),
    )
    team = forms.CharField(max_length=100, label="Team")

    def __init__(self, *args, **kwargs):
        self.match = kwargs.pop('match', None)
        super().__init__(*args, **kwargs)
        if self.match:
            # Filter player choices to players from home and away teams
            self.fields['player'].queryset = Player.objects.filter(
                team__in=[self.match.home_team, self.match.away_team]
            ).order_by("full_name")
    class Meta:
        model = PlayerBoxScore
        fields = [
            "player", "team", "is_starter", "minutes",
            "pts", "reb", "ast", "stl", "blk", "tov", "pf",
            "fg_made", "fg_att", "tp_made", "tp_att", "ft_made", "ft_att",
            "plus_minus",
        ]
        widgets = {
            "minutes":  forms.NumberInput(attrs={"min": 0, "step": 1}),  # akan dioverride ke TextInput di __init__
            "pts":      forms.NumberInput(attrs={"min": 0, "step": 1}),
            "reb":      forms.NumberInput(attrs={"min": 0, "step": 1}),
            "ast":      forms.NumberInput(attrs={"min": 0, "step": 1}),
            "stl":      forms.NumberInput(attrs={"min": 0, "step": 1}),
            "blk":      forms.NumberInput(attrs={"min": 0, "step": 1}),
            "tov":      forms.NumberInput(attrs={"min": 0, "step": 1}),
            "pf":       forms.NumberInput(attrs={"min": 0, "step": 1}),
            "fg_made":  forms.NumberInput(attrs={"min": 0, "step": 1}),
            "fg_att":   forms.NumberInput(attrs={"min": 0, "step": 1}),
            "tp_made":  forms.NumberInput(attrs={"min": 0, "step": 1}),
            "tp_att":   forms.NumberInput(attrs={"min": 0, "step": 1}),
            "ft_made":  forms.NumberInput(attrs={"min": 0, "step": 1}),
            "ft_att":   forms.NumberInput(attrs={"min": 0, "step": 1}),
        }

    def __init__(self, *args, **kwargs):
        self.match = kwargs.pop('match', None)
        super().__init__(*args, **kwargs)
        # minutes: ubah jadi text agar bisa mm:ss
        self.fields["minutes"].widget = forms.TextInput(
            attrs={"class": _BASE_INPUT, "placeholder": "mm:ss (mis. 32:15) atau angka menit"}
        )
        # styling team input
        self.fields["team"].widget.attrs.update({"class": _BASE_INPUT, "placeholder": "Nama tim"})
        # styling angka
        for k, f in self.fields.items():
            if isinstance(f.widget, forms.NumberInput):
                f.widget.attrs.update({"class": _BASE_INPUT})
        # checkbox
        self.fields["is_starter"].widget.attrs.update({"class": "h-4 w-4"})

        # saat edit, tampilkan minutes sebagai mm:ss
        if self.instance and self.instance.pk and self.instance.minutes:
            total_sec = int(round(float(self.instance.minutes) * 60))
            m, s = divmod(total_sec, 60)
            self.initial["minutes"] = f"{m:02d}:{s:02d}"

        if self.match:
            # Set initial team value if editing
            if self.instance and self.instance.pk:
                self.initial['team'] = self.instance.team

    def clean(self):
        cleaned = super().clean()

        # --- validasi player di team terpilih ---
        team_name = cleaned.get("team")
        player_obj = cleaned.get("player")

        if not team_name:
            self.add_error("team", "Masukkan nama tim.")
            return cleaned

        if not player_obj:
            self.add_error("player", "Pilih pemain.")
            return cleaned

        # pastikan pemain di team yang dipilih
        if player_obj.team != team_name:
            self.add_error("player", "Pemain tidak berada di tim yang dipilih.")
            return cleaned

        # --- minutes: izinkan 'mm:ss' atau angka ---
        raw_minutes = (cleaned.get("minutes") or "").strip()
        try:
            if isinstance(raw_minutes, str) and ":" in raw_minutes:
                m, s = map(int, raw_minutes.split(":"))
                if m < 0 or s < 0 or s >= 60:
                    raise ValueError
                minutes = m + s / 60
            else:
                minutes = float(raw_minutes) if raw_minutes != "" else 0.0
        except ValueError:
            self.add_error("minutes", "Gunakan angka atau format mm:ss yang valid, contoh 25:30.")
            return cleaned

        if minutes < 0:
            raise forms.ValidationError("Menit bermain tidak boleh negatif.")

        cleaned["minutes"] = minutes

        # --- validasi statistik logis ---
        fg_made = cleaned.get("fg_made") or 0
        fg_att  = cleaned.get("fg_att")  or 0
        tp_made = cleaned.get("tp_made") or 0
        tp_att  = cleaned.get("tp_att")  or 0
        ft_made = cleaned.get("ft_made") or 0
        ft_att  = cleaned.get("ft_att")  or 0

        if fg_made > fg_att:
            raise forms.ValidationError("FG made tidak boleh melebihi FG attempt.")
        if tp_made > tp_att:
            raise forms.ValidationError("3PT made tidak boleh melebihi 3PT attempt.")
        if ft_made > ft_att:
            raise forms.ValidationError("FT made tidak boleh melebihi FT attempt.")

        return cleaned


