from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from .models import Player
from .forms import PlayerForm

def player_list(request):
    players = Player.objects.all()
    return render(request, 'players/players_list.html', {'players': players})

@login_required
def add_player(request):
    if request.user.role != 'admin':
        return HttpResponseForbidden("Hanya admin yang dapat menambah data pemain.")
    if request.method == 'POST':
        form = PlayerForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('players:player_list')  
    else:
        form = PlayerForm()
    return render(request, 'players/player_form.html', {'form': form, 'title': 'Add Player'})

@login_required
def edit_player(request, player_id):
    if request.user.role != 'admin':
        return HttpResponseForbidden("Hanya admin yang dapat mengedit data pemain.")
    player = get_object_or_404(Player, pk=player_id)
    if request.method == 'POST':
        form = PlayerForm(request.POST, instance=player)
        if form.is_valid():
            form.save()
            return redirect('players:player_list')  
    else:
        form = PlayerForm(instance=player)
    return render(request, 'players/player_form.html', {'form': form, 'title': 'Edit Player'})

@login_required
def delete_player(request, player_id):
    if request.user.role != 'admin':
        return HttpResponseForbidden("Hanya admin yang dapat menghapus data pemain.")
    player = get_object_or_404(Player, pk=player_id)
    if request.method == 'POST':
        player.delete()
        return redirect('players:player_list')  
    return render(request, 'players/player_delete.html', {'player': player})
