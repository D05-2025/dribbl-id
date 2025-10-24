from django import forms
from .models import Player

class PlayerForm(forms.ModelForm):
    class Meta:
        model = Player
        fields = ['name', 'team', 'position', 'points_per_game', 'assists_per_game', 'rebounds_per_game']
        labels = {
            'name': 'Player Name',
            'team': 'Team',
            'position': 'Position',
            'points_per_game': 'Points Per Game',
            'assists_per_game': 'Assists Per Game',
            'rebounds_per_game': 'Rebounds Per Game',
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'LeBron James'}),
            'team': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'LAL'}),
            'position': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'SF'}),
            'points_per_game': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'assists_per_game': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'rebounds_per_game': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
        }
