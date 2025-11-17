from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponseForbidden
from .models import Event

def show_json(request):
    events = Event.objects.all()

    data = [
        {
            'id': e.id,
            'title': e.title,
            'description': e.description,
            'date': e.date.strftime('%Y-%m-%d'),
            'time': e.time,
            'image_url': e.image_url,
            'is_public': e.is_public,
            'location': e.location
        } for e in events
    ]
    return JsonResponse(data, safe=False)

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
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    if user_role != 'admin':
        return JsonResponse({'error': 'Forbidden'}, status=403)

    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        date = request.POST.get('date')
        is_public = request.POST.get('is_public') == 'on'
        image_url = request.POST.get('image_url')
        location = request.POST.get('location')
        time = request.POST.get('time')

        event = Event.objects.create(
            title=title,
            description=description,
            date=date,
            is_public=is_public,
            created_by_id=user_id,
            image_url=image_url,
            location=location,
            time=time
        )

        # Respon AJAX
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'message': 'Event berhasil dibuat!', 'event_id': event.id})
        
        return redirect('events:event_list')

    return render(request, 'create_event.html')


def edit_event(request, event_id):
    user_role = request.session.get('role')
    if user_role != 'admin':
        return JsonResponse({'error': 'Forbidden'}, status=403)

    event = get_object_or_404(Event, id=event_id)

    if request.method == 'POST':
        event.title = request.POST.get('title')
        event.description = request.POST.get('description')
        event.date = request.POST.get('date')
        event.is_public = request.POST.get('is_public') == 'on'
        event.image_url = request.POST.get('image_url')
        event.location = request.POST.get('location')
        event.time = request.POST.get('time')
        event.save()

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'message': 'Event berhasil diperbarui!'})
        
        return redirect('events:event_list')

    return render(request, 'edit_event.html', {'event': event})


def delete_event(request, event_id):
    user_id = request.session.get('user_id')
    user_role = request.session.get('role')

    if user_role != 'admin':
        return JsonResponse({'error': 'Forbidden'}, status=403)

    event = get_object_or_404(Event, id=event_id)
    event.delete()

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'message': 'Event berhasil dihapus!'})

    return redirect('events:event_list')
