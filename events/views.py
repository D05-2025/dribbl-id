from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponseForbidden
from .models import Event
from django.views.decorators.csrf import csrf_exempt
from django.utils.html import strip_tags
import json
from django.http import JsonResponse

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

@csrf_exempt
def create_events_flutter(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"status": "error", "message": "Invalid JSON format"}, status=400)

        title = strip_tags(data.get("title", ""))
        description = strip_tags(data.get("description", ""))
        date_str = data.get("date", None)
        thumbnail = data.get("image_url", "")
        is_public = data.get("is_public", True)
        location = strip_tags(data.get("location", ""))
        time_str = data.get("time", None)

        user = request.user
        
        new_events = Event(
            title=title,
            description=description,
            date=date_str,
            is_public=is_public,
            created_by_id=user.id,
            image_url=thumbnail,
            location=location,
            time=time_str
        )
        new_events.save()
        
        return JsonResponse({"status": "success"}, status=201)
    else:
        return JsonResponse({"status": "error", "message": "Method not allowed"}, status=405)
    
@csrf_exempt
def delete_event_flutter(request):
    if request.method == 'POST':
        event_id = request.POST.get("id")

        if not event_id:
            return JsonResponse({"status": "error", "message": "Event ID required"}, status=400)

        try:
            event = Event.objects.get(pk=event_id)
        except Event.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Event not found"}, status=404)

        event.delete()
        return JsonResponse({"status": "success"}, status=200)

    return JsonResponse({"status": "error", "message": "Method not allowed"}, status=405)

@csrf_exempt
def edit_event_flutter(request):
    if request.method != "POST":
        return JsonResponse({"status": "error", "message": "Invalid method"}, status=400)

    try:
        data = json.loads(request.body)

        event_id = data.get("id")
        if event_id is None:
            return JsonResponse({"status": "error", "message": "Missing event ID"}, status=400)

        try:
            event = Event.objects.get(id=event_id)
        except Event.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Event not found"}, status=404)

        # Update fields
        event.title = data.get("title", event.title)
        event.description = data.get("description", event.description)
        event.location = data.get("location", event.location)
        event.date = data.get("date", event.date)
        event.time = data.get("time", event.time)
        event.image_url = data.get("image_url", event.image_url)
        event.is_public = data.get("is_public", event.is_public)

        event.save()

        return JsonResponse({"status": "success", "message": "Event updated successfully"})

    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)
    
@csrf_exempt
def update_events_flutter(request):
    if request.method == "POST":
        data = json.loads(request.body)
        event_id = data.get("id")

        try:
            event = Event.objects.get(id=event_id, created_by=request.user)
        except Event.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Not found"}, status=404)

        event.title = data.get("title", event.title)
        event.description = data.get("description", event.description)
        event.location = data.get("location", event.location)
        event.time = data.get("time", event.time)
        event.date = data.get("date", event.date)
        event.image_url = data.get("image_url", event.image_url)
        event.is_public = data.get("is_public", event.is_public)

        event.save()
        return JsonResponse({"status": "success"}, status=200)

    return JsonResponse({"status": "error", "message": "Method not allowed"}, status=405)
