# matches/views.py
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.urls import reverse
from django.views.decorators.http import require_http_methods

from .forms import MatchForm, MatchScoreForm, PlayerBoxScoreForm
from .models import Match, PlayerBoxScore

from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom

import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Match
from django.utils.dateparse import parse_datetime


# ---- helpers ----------------------------------------------------------------
def _is_ajax(request):
    return request.headers.get("X-Requested-With") == "XMLHttpRequest"


# ---- public pages ------------------------------------------------------------
def match_schedule(request):
    q = (request.GET.get("q") or "").strip()
    qs = Match.objects.select_related("season").order_by("tipoff_at")
    if q:
        qs = qs.filter(
            Q(home_team__icontains=q)
            | Q(away_team__icontains=q)
            | Q(venue__icontains=q)
        )
    return render(request, "matches/match_schedule.html", {"matches": qs, "q": q})


def match_results(request):
    q = (request.GET.get("q") or "").strip()
    qs = (
        Match.objects.select_related("season")
        .filter(status="finished")
        .order_by("-tipoff_at")
    )
    if q:
        qs = qs.filter(
            Q(home_team__icontains=q)
            | Q(away_team__icontains=q)
            | Q(venue__icontains=q)
        )
    return render(request, "matches/match_results.html", {"matches": qs, "q": q})


def match_detail(request, pk):
    m = get_object_or_404(Match.objects.select_related("season"), pk=pk)
    return render(request, "matches/match_detail.html", {"match": m})


# ---- CRUD: Match -------------------------------------------------------------
@login_required
@require_http_methods(["GET", "POST"])
def match_create(request):
    """
    Single endpoint:
      - GET normal: render form page
      - GET AJAX:  return {"ok": True, "html_form": "..."}
      - POST normal: redirect ke detail
      - POST AJAX:  return {"ok": True, "message": "...", "row_html": "...", "redirect": "..."}
    """
    if request.method == "GET":
        form = MatchForm()
        if _is_ajax(request):
            html_form = render_to_string("matches/_match_form.html", {"form": form}, request=request)
            return JsonResponse({"ok": True, "html_form": html_form})
        return render(request, "matches/match_form.html", {"form": form, "title": "Buat Pertandingan"})

    # POST
    form = MatchForm(request.POST)
    if form.is_valid():
        match = form.save()
        if _is_ajax(request):
            row_html = render_to_string("matches/_match_row.html", {"m": match}, request=request)
            return JsonResponse({
                "ok": True,
                "message": "Match berhasil dibuat.",
                "row_html": row_html,
                "redirect": reverse("matches:detail", args=[match.pk]),
            })
        messages.success(request, "Match berhasil dibuat!")
        return redirect("matches:detail", pk=match.pk)

    # invalid
    if _is_ajax(request):
        html_form = render_to_string("matches/_match_form.html", {"form": form}, request=request)
        return JsonResponse({"ok": False, "html_form": html_form}, status=400)
    messages.error(request, "Gagal membuat match. Periksa input Anda.")
    return render(request, "matches/match_form.html", {"form": form, "title": "Buat Pertandingan"})


@login_required
@require_http_methods(["GET", "POST"])
def match_edit(request, pk):
    """
    Edit form:
      - GET normal: render page
      - GET AJAX:  return html_form
      - POST normal: redirect
      - POST AJAX:  return {"ok": True} atau {"ok": False, "html_form": "..."}
    """
    m = get_object_or_404(Match, pk=pk)

    if request.method == "GET":
        form = MatchForm(instance=m)
        if _is_ajax(request):
            html_form = render_to_string("matches/_match_form.html", {"form": form, "is_edit": True, "match_pk": pk}, request=request)
            return JsonResponse({"ok": True, "html_form": html_form})
        return render(request, "matches/match_form.html", {"form": form, "title": "Edit Pertandingan"})

    # POST
    form = MatchForm(request.POST, instance=m)
    if form.is_valid():
        form.save()
        if _is_ajax(request):
            return JsonResponse({"ok": True, "message": "Match berhasil diperbarui!"})
        messages.success(request, "Match berhasil diperbarui!")
        return redirect("matches:detail", pk=m.pk)

    # invalid
    if _is_ajax(request):
        html_form = render_to_string("matches/_match_form.html", {"form": form, "is_edit": True, "match_pk": pk}, request=request)
        return JsonResponse({"ok": False, "html_form": html_form}, status=400)
    messages.error(request, "Gagal menyimpan perubahan. Periksa input Anda.")
    return render(request, "matches/match_form.html", {"form": form, "title": "Edit Pertandingan"})


@login_required
@require_http_methods(["GET", "POST"])
def match_delete(request, pk):
    m = get_object_or_404(Match, pk=pk)
    if request.method == "POST":
        m.delete()
        messages.success(request, "Match berhasil dihapus!")
        return redirect("matches:schedule")
    return render(request, "matches/match_confirm_delete.html", {"match": m})


@login_required
@require_http_methods(["GET", "POST"])
def match_update_score(request, pk):
    m = get_object_or_404(Match, pk=pk)
    if request.method == "POST":
        form = MatchScoreForm(request.POST, instance=m)
        if form.is_valid():
            form.save()
            m.recalc_totals_from_periods(save=True)
            messages.info(request, "Skor per-kuarter diperbarui dan direkalkulasi.")
            return redirect("matches:detail", pk=m.pk)
        messages.error(request, "Gagal menyimpan skor. Periksa input Anda.")
    else:
        form = MatchScoreForm(instance=m)
    return render(request, "matches/match_score_form.html", {"form": form, "match": m, "title": "Update Skor Per-Kuarter"})


# ---- Boxscore ---------------------------------------------------------------
@login_required
@require_http_methods(["GET", "POST"])
def boxscore_add(request, pk):
    m = get_object_or_404(Match, pk=pk)
    if request.method == "POST":
        form = PlayerBoxScoreForm(request.POST, match=m)
        if form.is_valid():
            box = form.save(commit=False)
            box.match = m
            if box.team not in (m.home_team, m.away_team):
                messages.error(request, "Team boxscore harus home atau away pada match ini.")
                return redirect("matches:detail", pk=m.pk)
            box.save()
            messages.success(request, "Box score ditambahkan.")
            return redirect("matches:detail", pk=m.pk)
        messages.error(request, "Gagal menyimpan box score. Periksa input Anda.")
    else:
        form = PlayerBoxScoreForm(match=m)
    return render(request, "matches/boxscore_form.html", {"form": form, "match": m, "title": "Tambah Box Score"})


@login_required
@require_http_methods(["GET", "POST"])
def boxscore_edit(request, pk, box_id):
    m = get_object_or_404(Match, pk=pk)
    box = get_object_or_404(PlayerBoxScore, pk=box_id, match=m)
    if request.method == "POST":
        form = PlayerBoxScoreForm(request.POST, instance=box, match=m)
        if form.is_valid():
            b = form.save(commit=False)
            if b.team not in (m.home_team, m.away_team):
                messages.error(request, "Team boxscore harus home atau away pada match ini.")
                return redirect("matches:detail", pk=m.pk)
            b.save()
            messages.success(request, "Box score diperbarui.")
            return redirect("matches:detail", pk=m.pk)
        messages.error(request, "Gagal menyimpan perubahan. Periksa input Anda.")
    else:
        form = PlayerBoxScoreForm(instance=box, match=m)
    return render(request, "matches/boxscore_form.html", {"form": form, "match": m, "title": "Edit Box Score"})


# ---- Data endpoints (JSON/XML) ----------------------------------------------
# matches/views.py

def matches_json(request):
    matches = Match.objects.select_related("season").all()
    data = [{
        "uuid": str(m.uuid),
        "home_team": m.home_team,
        "away_team": m.away_team,
        "tipoff_at": m.tipoff_at.isoformat(),
        "venue": m.venue,
        "status": m.status,
        "home_score": m.home_score,
        "away_score": m.away_score,
        "match_thumbnail": m.image_url, 
        
    } for m in matches]
    return JsonResponse(data, safe=False)


def matches_xml(request):
    matches = Match.objects.select_related("season").all()
    root = Element("matches")
    for m in matches:
        e = SubElement(root, "match")
        SubElement(e, "uuid").text = str(m.uuid)
        SubElement(e, "home_team").text = m.home_team
        SubElement(e, "away_team").text = m.away_team
        SubElement(e, "tipoff_at").text = m.tipoff_at.isoformat()
        SubElement(e, "venue").text = m.venue or ""
        SubElement(e, "status").text = m.status
        SubElement(e, "home_score").text = str(m.home_score)
        SubElement(e, "away_score").text = str(m.away_score)

    xml_str = tostring(root, encoding="unicode")
    pretty_xml = minidom.parseString(xml_str).toprettyxml(indent="  ")
    return HttpResponse(pretty_xml, content_type="application/xml")

@csrf_exempt
def create_match_flutter(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # Pastikan format datetime sesuai (ISO 8601 biasanya dikirim flutter)
            # Contoh format: "2025-10-24T19:30:00"
            
            new_match = Match.objects.create(
                home_team=data["home_team"],
                away_team=data["away_team"],
                tipoff_at=parse_datetime(data["tipoff_at"]),
                venue=data["venue"],
                image_url=data["image_url"],
                status=data["status"], # scheduled, live, finished
                home_score=int(data.get("home_score", 0)),
                away_score=int(data.get("away_score", 0)),
            )
            
            new_match.save()
            return JsonResponse({"status": "success"}, status=200)
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)

    return JsonResponse({"status": "error", "message": "Invalid method"}, status=401)
