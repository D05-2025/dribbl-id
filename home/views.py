from django.shortcuts import render

# Create your views here.
def show_main(request):
    context = {
        "title": "Main Page",
        "kelompok" : "D05"
    }
    return render(request, "main.html", context)

