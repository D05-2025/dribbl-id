from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
from .models import CustomUser
import datetime
from django.http import HttpResponseRedirect
from django.urls import reverse

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

def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        role = request.POST.get('role', 'user')

        if not username or not password:
            messages.error(request, 'Username dan password wajib diisi.')
            return redirect('main:register')

        if CustomUser.objects.filter(username=username).exists():
            messages.error(request, 'Username sudah digunakan.')
            return redirect('main:register')

        user = CustomUser.objects.create(
            username=username,
            role=role
        )
        user.set_password(password)
        user.save()

        messages.success(request, 'Akun berhasil dibuat! Silakan login.')
        return redirect('main:login') 

    return render(request, 'register.html')

def login_user(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            user = CustomUser.objects.get(username=username)
            if user.check_password(password):
                request.session['user_id'] = str(user.id)
                request.session['username'] = user.username
                request.session['role'] = user.role
                
                user.save()
                
                response = HttpResponseRedirect(reverse("main:show_main"))
                response.set_cookie('last_login', str(datetime.datetime.now()))
                return response
            else:
                messages.error(request, 'Password salah.')
        except CustomUser.DoesNotExist:
            messages.error(request, 'Username tidak ditemukan.')

    return render(request, 'login.html')

def logout_user(request):
    request.session.flush()
    # PERBAIKAN: Redirect ke home page setelah logout
    response = HttpResponseRedirect(reverse('main:show_main'))
    response.delete_cookie('last_login')
    return response