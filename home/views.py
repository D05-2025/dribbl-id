from django.shortcuts import render
from django.http import HttpResponse

def show_main(request):
    """
    View untuk menampilkan homepage dengan efek ketik
    """
    context = {
        'title': 'DRIBBL.ID',
        'welcome_text': 'Welcome to DRIBBL.ID',
        'subtitle': 'The biggest Indonesian basketball community',
    }
<<<<<<< HEAD
    return render(request, 'main.html', context)
=======
    return render(request, 'main.html', context)

>>>>>>> news
