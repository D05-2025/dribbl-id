from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from django.contrib import messages
from django.http import HttpResponseBadRequest
from .models import Match, PlayerBoxScore
from .forms import MatchForm, MatchScoreForm, PlayerBoxScoreForm
from django.http import JsonResponse, HttpResponseBadRequest
from django.template.loader import render_to_string
from django.urls import reverse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import User
from django.contrib.auth.decorators import user_passes_test
from django.core.serializers import serialize
import json
from django.http import HttpResponse
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom

from .forms import MatchForm
from .models import Match

def match_schedule(request):
    q = (request.GET.get("q") or "").strip()
    qs = (
        Match.objects
        .select_related("home_team", "away_team", "season")
        .order_by("tipoff_at")
    )
    if q:
        qs = qs.filter(
            Q(home_team__name__icontains=q) |
            Q(away_team__name__icontains=q) |
            Q(home_team__short_name__icontains=q) |
            Q(away_team__short_name__icontains=q) |
            Q(venue__icontains=q)
        )

    context = {"matches": qs, "q": q}
    return render(request, "matches/match_schedule.html", context)

def match_results(request):
    q = (request.GET.get("q") or "").strip()
    qs = (
        Match.objects
        .select_related("home_team", "away_team", "season")
        .filter(status="finished")
        .order_by("-tipoff_at")
    )
    if q:
        qs = qs.filter(
            Q(home_team__name__icontains=q) |
            Q(away_team__name__icontains=q) |
            Q(home_team__short_name__icontains=q) |
            Q(away_team__short_name__icontains=q) |
            Q(venue__icontains=q)
        )

    context = {"matches": qs, "q": q}
    return render(request, "matches/match_results.html", context)

def match_detail(request, pk):
    m = get_object_or_404(
        Match.objects
        .select_related("home_team", "away_team", "season"),
        pk=pk
    )

    context = {
        "match": m,
    }
    return render(request, "matches/match_detail.html", context)

@login_required
def match_create(request):
    title = "Buat Pertandingan"
    if request.method == "POST":
        form = MatchForm(request.POST)
        if form.is_valid():
            obj = form.save()
            messages.success(request, "Match berhasil dibuat!")
            return redirect("matches:detail", pk=obj.pk)
        messages.error(request, "Gagal membuat match. Periksa input Anda.")
    else:
        form = MatchForm()

    return render(request, "matches/match_form.html", {"form": form, "title": title})


@login_required
def match_delete(request, pk):
    m = get_object_or_404(Match, pk=pk)
    if request.method == "POST":
        m.delete()
        messages.success(request, "Match berhasil dihapus!")
        return redirect("matches:schedule")
    return render(request, "matches/match_confirm_delete.html", {"match": m})

@login_required
def match_edit(request, pk):
    m = get_object_or_404(Match, pk=pk)
    if request.method == "GET":
        if _is_ajax(request):
            form = MatchForm(instance=m)
            html_form = render_to_string(
                "matches/_match_form.html",
                {"form": form},
                request=request,
            )
            return JsonResponse({"ok": True, "html_form": html_form})
        form = MatchForm(instance=m)
        return render(request, "matches/match_form.html", {"form": form})

    # POST
    form = MatchForm(request.POST, instance=m)
    if form.is_valid():
        obj = form.save()
        if _is_ajax(request):
            return JsonResponse({
                "ok": True,
                "message": "Match berhasil diperbarui!",
                "redirect": reverse("matches:detail", args=[obj.pk]),
            })
        messages.success(request, "Match berhasil diperbarui!")
        return redirect("matches:detail", pk=obj.pk)

    # invalid
    if _is_ajax(request):
        html_form = render_to_string(
            "matches/_match_form.html",
            {"form": form},
            request=request,
        )
        return JsonResponse({"ok": False, "html_form": html_form}, status=400)

    messages.error(request, "Gagal menyimpan perubahan. Periksa input Anda.")
    return render(request, "matches/match_form.html", {"form": form})

@login_required
def match_update_score(request, pk):
    m = get_object_or_404(Match, pk=pk)
    title = "Update Skor Per-Kuarter"
    if request.method == "POST":
        form = MatchScoreForm(request.POST, instance=m)
        if form.is_valid():
            form.save()
            # Recalculate total skor & flag OT
            m.recalc_totals_from_periods(save=True)
            messages.info(request, "Skor per-kuarter diperbarui dan direkalkulasi.")
            return redirect("matches:detail", pk=m.pk)
        messages.error(request, "Gagal menyimpan skor. Periksa input Anda.")
    else:
        form = MatchScoreForm(instance=m)

    return render(request, "matches/match_score_form.html", {"form": form, "match": m, "title": title})


@login_required
def boxscore_add(request, pk):
    m = get_object_or_404(Match, pk=pk)
    title = "Tambah Box Score"
    if request.method == "POST":
        form = PlayerBoxScoreForm(request.POST, match=m)
        if form.is_valid():
            box = form.save(commit=False)
            box.match = m
            # safety: team harus salah satu dari home/away
            if box.team_id not in (m.home_team_id, m.away_team_id):
                messages.error(request, "Team boxscore harus home atau away pada match ini.")
                return redirect("matches:detail", pk=m.pk)
            box.save()
            messages.success(request, "Box score ditambahkan.")
            return redirect("matches:detail", pk=m.pk)
        messages.error(request, "Gagal menyimpan box score. Periksa input Anda.")
    else:
        form = PlayerBoxScoreForm(match=m)

    return render(request, "matches/boxscore_form.html", {"form": form, "match": m, "title": title})


@login_required
def boxscore_edit(request, pk, box_id):
    m = get_object_or_404(Match, pk=pk)
    box = get_object_or_404(PlayerBoxScore, pk=box_id, match=m)
    title = "Edit Box Score"
    if request.method == "POST":
        form = PlayerBoxScoreForm(request.POST, instance=box, match=m)
        if form.is_valid():
            b = form.save(commit=False)
            if b.team_id not in (m.home_team_id, m.away_team_id):
                messages.error(request, "Team boxscore harus home atau away pada match ini.")
                return redirect("matches:detail", pk=m.pk)
            b.save()
            messages.success(request, "Box score diperbarui.")
            return redirect("matches:detail", pk=m.pk)
        messages.error(request, "Gagal menyimpan perubahan. Periksa input Anda.")
    else:
        form = PlayerBoxScoreForm(instance=box, match=m)

    return render(request, "matches/boxscore_form.html", {"form": form, "match": m, "title": title})

def _is_ajax(request):
    return request.headers.get("X-Requested-With") == "XMLHttpRequest"

@login_required
@require_http_methods(["GET", "POST"])
def match_create(request):
    """
    Single endpoint: kalau request AJAX -> balikin JSON,
    kalau biasa -> render form seperti normal.
    """
    if request.method == "GET":
        form = MatchForm()
        if _is_ajax(request):
            html_form = render_to_string(
                "matches/_match_form.html",
                {"form": form},
                request=request,
            )
            return JsonResponse({"ok": True, "html_form": html_form})
        return render(request, "matches/match_form.html", {"form": form})


def matches_json(request):
    matches = Match.objects.select_related("home_team", "away_team", "season").all()
    data = []
    for match in matches:
        data.append({
            "uuid": str(match.uuid),
            "home_team": match.home_team.name,
            "away_team": match.away_team.name,
            "tipoff_at": match.tipoff_at.isoformat(),
            "venue": match.venue,
            "status": match.status,
            "home_score": match.home_score,
            "away_score": match.away_score,
        })
    return JsonResponse({"matches": data})


def matches_xml(request):
    matches = Match.objects.select_related("home_team", "away_team", "season").all()
    root = Element("matches")
    for match in matches:
        match_elem = SubElement(root, "match")
        SubElement(match_elem, "uuid").text = str(match.uuid)
        SubElement(match_elem, "home_team").text = match.home_team.name
        SubElement(match_elem, "away_team").text = match.away_team.name
        SubElement(match_elem, "tipoff_at").text = match.tipoff_at.isoformat()
        SubElement(match_elem, "venue").text = match.venue or ""
        SubElement(match_elem, "status").text = match.status
        SubElement(match_elem, "home_score").text = str(match.home_score)
        SubElement(match_elem, "away_score").text = str(match.away_score)

    xml_str = tostring(root, encoding='unicode')
    pretty_xml = minidom.parseString(xml_str).toprettyxml(indent="  ")
    return HttpResponse(pretty_xml, content_type='application/xml')

    # POST
    form = MatchForm(request.POST)
    if form.is_valid():
        match = form.save()
        if _is_ajax(request):
            row_html = render_to_string(
                "matches/_match_row.html",
                {"m": match},
                request=request,
            )
            return JsonResponse({
                "ok": True,
                "message": "Match berhasil dibuat.",
                "row_html": row_html,
                "redirect": reverse("matches:detail", args=[match.pk]),
            })
        return redirect("matches:detail", pk=match.pk)

    # invalid
    if _is_ajax(request):
        html_form = render_to_string(
            "matches/_match_form.html",
            {"form": form},
            request=request,
        )
        return JsonResponse({"ok": False, "html_form": html_form}, status=400)

    return render(request, "matches/match_form.html", {"form": form})