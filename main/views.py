from django.shortcuts import render, redirect, get_object_or_404
from .models import Event

# tampil daftar acara (user)
def event_list(request):
    events = Event.objects.all().order_by('waktu')
    return render(request, 'events_list.html', {'events': events})

# detail acara
def event_detail(request, id):
    event = get_object_or_404(Event, id=id)
    return render(request, 'event_detail.html', {'event': event})

# CRUD (admin)
def event_create(request):
    if request.method == 'POST':
        nama = request.POST['nama']
        waktu = request.POST['waktu']
        lokasi = request.POST['lokasi']
        deskripsi = request.POST['deskripsi']
        Event.objects.create(nama=nama, waktu=waktu, lokasi=lokasi, deskripsi=deskripsi)
        return redirect('event_list')
    return render(request, 'event_form.html')

def event_update(request, id):
    event = get_object_or_404(Event, id=id)
    if request.method == 'POST':
        event.nama = request.POST['nama']
        event.waktu = request.POST['waktu']
        event.lokasi = request.POST['lokasi']
        event.deskripsi = request.POST['deskripsi']
        event.save()
        return redirect('event_list')
    return render(request, 'event_form.html', {'event': event})

def event_delete(request, id):
    event = get_object_or_404(Event, id=id)
    event.delete()
    return redirect('event_list')
