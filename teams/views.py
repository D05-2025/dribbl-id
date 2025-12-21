from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.urls import reverse
# Import slugify to create IDs
from django.template.defaultfilters import truncatewords, slugify
from django.views.decorators.http import require_POST, require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
# Import Q object for searching
from django.db.models import Q

from .models import Team
from .forms import TeamForm
from functools import wraps

import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Team
from datetime import datetime

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

@csrf_exempt
def create_team_flutter(request):
    if request.method == "POST":
        data = json.loads(request.body)

        Team.objects.create(
            name=data["name"],
            city=data["city"],
            logo_url=data["logo_url"]
        )

        return JsonResponse({"status": "success"})
    
    return JsonResponse({"status": "error"}, status=400)

def show_json(request):
    teams = Team.objects.all()

    data = [
        {
            'name': t.name,
            'logo': t.logo,
            'region': t.region,
            'founded': t.founded.strftime('%Y-%m-%d'),
            'description': t.description
        } for t in teams
    ]
    return JsonResponse(data, safe=False)

# Helper decorator for admin-only AJAX views
def admin_required_ajax(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({"status": "error", "message": "Authentication required"}, status=401)
        if request.user.role != 'admin':
            return JsonResponse({"status": "error", "message": "Admin access required"}, status=403)
        return view_func(request, *args, **kwargs)
    return _wrapped_view

@login_required
def show_teams(request):
    """
    Displays the list of all teams and includes the form for adding a new team.
    Now includes server-side filtering based on GET parameters.
    """
    # --- NEW: Get filter parameters from URL ---
    search_query = request.GET.get('search', '')
    region_filter = request.GET.get('region', '')
    
    # Start with all teams
    teams = Team.objects.all()
    
    # --- NEW: Apply search filter ---
    if search_query:
        teams = teams.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    # --- NEW: Apply region filter ---
    if region_filter:
        teams = teams.filter(region=region_filter)
        
    form = TeamForm()
    context = {
        'teams': teams,
        'form': form,
        # --- NEW: Pass filter values back to template ---
        'search_query': search_query,
        'selected_region': region_filter,
    }
    return render(request, 'team_list.html', context)

@csrf_exempt
@require_POST
@admin_required_ajax # Use helper decorator
def add_team(request):
    """
    Handles the AJAX POST request to add a new team.
    """
    form = TeamForm(request.POST)
    if form.is_valid():
        team = form.save()
        
        # --- FIX: Send all data required by the JavaScript ---
        team_data = {
            'name': team.name,
            'slug_name': slugify(team.name), # For the card ID
            'logo': team.logo,
            'region': team.region, # For the filter
            'description': truncatewords(team.description, 20),
            'url': reverse('teams:team_detail', args=[team.name]),
            # Add URLs for the new card's admin buttons
            'get_url': reverse('teams:get_team_data', args=[team.name]),
            'edit_url': reverse('teams:edit_team', args=[team.name]),
            'delete_url': reverse('teams:delete_team', args=[team.name]),
        }
        return JsonResponse({'status': 'success', 'team': team_data})
    else:
        # Send back form validation errors
        return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)

@admin_required_ajax # Protect this view
def get_team(request, team_name):
    """
    (NEW) Returns a JSON object with a single team's data for populating the edit form.
    """
    team = get_object_or_404(Team, pk=team_name)
    data = {
        'name': team.name,
        'logo': team.logo,
        'region': team.region,
        'founded': team.founded.strftime('%Y-%m-%d'), # Format for <input type="date">
        'description': team.description,
    }
    return JsonResponse({'status': 'success', 'team': data})

@csrf_exempt
@require_POST
@admin_required_ajax # Protect this view
def edit_team(request, team_name):
    """
    (NEW) Handles the AJAX POST request to update an existing team.
    """
    team = get_object_or_404(Team, pk=team_name)
    form = TeamForm(request.POST, instance=team)
    if form.is_valid():
        updated_team = form.save()
        # --- FIX: Send data needed to update the card ---
        team_data = {
            'name': updated_team.name,
            'logo': updated_team.logo,
            'region': updated_team.region, # For the filter
            'description': truncatewords(updated_team.description, 20),
            'url': reverse('teams:team_detail', args=[updated_team.name])
        }
        return JsonResponse({'status': 'success', 'team': team_data})
    else:
        return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)

@csrf_exempt
@require_http_methods(["DELETE"]) # Only allow DELETE method
@admin_required_ajax # Protect this view
def delete_team(request, team_name):
    """
    (NEW) Handles the AJAX DELETE request to remove a team.
    """
    try:
        team = get_object_or_404(Team, pk=team_name)
        team.delete()
        return JsonResponse({'status': 'success', 'message': 'Team deleted successfully'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

def team_detail(request, team_name):
    """
    Displays the detailed page for a single team.
    """
    team = get_object_or_404(Team, pk=team_name)
    context = {
        'team': team
    }
    return render(request, 'team_detail.html', context)


