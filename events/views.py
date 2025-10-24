from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponseForbidden
from django.conf import settings
from .models import Event
from datetime import datetime
import os
import pandas as pd


def event_list(request):
    user_id = request.session.get('user_id')
    user_role = request.session.get('role')

    if not user_id:
        return redirect('/login')

    if user_role == 'admin':
        events = Event.objects.all()
    else:
        events = Event.objects.filter(is_public=True)

    # Kalau request pakai AJAX, kirim data JSON
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        events_data = [
            {
                'id': e.id,
                'title': e.title,
                'description': e.description,
                'date': e.date.strftime('%Y-%m-%d'),
                'time': e.time.strftime('%H:%M') if e.time else '',
                'image_url': e.image_url,
                'is_public': e.is_public,
                'location': e.location
            } for e in events
        ]
        return JsonResponse({'events': events_data})
    
    return render(request, 'event_list.html', {'events': events})


def create_event(request):
    user_id = request.session.get('user_id')
    user_role = request.session.get('role')

    if not user_id:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'error': 'Unauthorized'}, status=403)
        return redirect('login')
    
    if user_role != 'admin':
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'error': 'Forbidden'}, status=403)
        return HttpResponseForbidden("Kamu tidak punya akses untuk membuat event.")

    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        date = request.POST.get('date')
        time = request.POST.get('time') or None
        location = request.POST.get('location') or None
        image_url = request.POST.get('image_url') or None
        is_public = request.POST.get('is_public') == 'on'

        event = Event.objects.create(
            title=title,
            description=description,
            date=date,
            time=time,
            location=location,
            image_url=image_url,
            is_public=is_public,
            created_by_id=user_id
        )

        # Respon AJAX
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'message': 'Event berhasil dibuat!', 'event_id': event.id})
        
        return redirect('events:event_list')

    return render(request, 'create_event.html')


def edit_event(request, event_id):
    user_id = request.session.get('user_id')
    user_role = request.session.get('role')

    if not user_id:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'error': 'Unauthorized'}, status=403)
        return redirect('authentication:login')

    if user_role != 'admin':
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'error': 'Forbidden'}, status=403)
        return HttpResponseForbidden("Kamu tidak punya akses untuk mengedit event.")

    event = get_object_or_404(Event, id=event_id)

    if request.method == 'POST':
        event.title = request.POST.get('title')
        event.description = request.POST.get('description')
        event.date = request.POST.get('date')
        event.time = request.POST.get('time') or None
        event.location = request.POST.get('location') or None
        event.image_url = request.POST.get('image_url') or None
        event.is_public = request.POST.get('is_public') == 'on'
        event.save()

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'message': 'Event berhasil diperbarui!'})
        
        return redirect('events:event_list')

    return render(request, 'edit_event.html', {'event': event})


def delete_event(request, event_id):
    user_id = request.session.get('user_id')
    user_role = request.session.get('role')

    if not user_id:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'error': 'Unauthorized'}, status=403)
        return redirect('authentication:login')

    if user_role != 'admin':
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'error': 'Forbidden'}, status=403)
        return HttpResponseForbidden("Kamu tidak punya akses untuk menghapus event.")

    event = get_object_or_404(Event, id=event_id)
    event.delete()

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'message': 'Event berhasil dihapus!'})

    return redirect('events:event_list')

def load_events_dataset(request):
    user_id = request.session.get('user_id')
    user_role = request.session.get('role')

    # Cek login dan role admin
    if not user_id:
        return JsonResponse({'status': 'error', 'message': 'Kamu belum login.'}, status=403)
    if user_role != 'admin':
        return JsonResponse({'status': 'error', 'message': 'Hanya admin yang bisa memuat dataset.'}, status=403)

    # Path CSV
    csv_path = os.path.join(settings.BASE_DIR, 'data', 'events', 'events_data.csv')

    # Cek file
    if not os.path.exists(csv_path):
        return JsonResponse({
            'status': 'error',
            'message': f'File CSV tidak ditemukan di: {csv_path}'
        }, status=404)

    # Load CSV
    df = pd.read_csv(csv_path)
    count = 0

    for row in df.itertuples(index=False):
        event, created = Event.objects.get_or_create(
            title=row.title,
            defaults={
                'description': row.description,
                'date': row.date,
                'time': row.time,
                'location': row.location,
                'image_url': row.image_url,
                'is_public': str(row.is_public).strip().upper() == 'TRUE'
            }
        )
        if created:
            count += 1

    return JsonResponse({
        'status': 'success',
        'message': f'Berhasil memuat {count} event baru dari CSV.',
        'total_events': Event.objects.count()
    })
