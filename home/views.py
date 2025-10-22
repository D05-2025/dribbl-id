from django.shortcuts import render

def show_main(request):
    """
    View untuk menampilkan homepage dengan efek ketik
    """
    context = {
        'title': 'DRIBBL.ID',
        'welcome_text': 'Welcome to DRIBBL.ID',
        'subtitle': 'The biggest Indonesian basketball community',
    }
    return render(request, 'main.html', context)