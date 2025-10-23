from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
from .models import CustomUser
import datetime
from django.http import HttpResponseRedirect
from django.urls import reverse

def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        role = request.POST.get('role', 'user')

        if not username or not password:
            messages.error(request, 'Username dan password wajib diisi.')
            return redirect('register')

        if CustomUser.objects.filter(username=username).exists():
            messages.error(request, 'Username sudah digunakan.')
            return redirect('register')

        user = CustomUser.objects.create(
            username=username,
            role=role
        )
        user.set_password(password)
        user.save()

        messages.success(request, 'Akun berhasil dibuat! Silakan login.')
        return redirect('login') 

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
                
                # Update last_login
                user.save()  # AbstractBaseUser handle last_login automatically
                
                response = HttpResponseRedirect(reverse("home:show_main"))
                response.set_cookie('last_login', str(datetime.datetime.now()))
                return response
            else:
                messages.error(request, 'Password salah.')
        except CustomUser.DoesNotExist:
            messages.error(request, 'Username tidak ditemukan.')

    return render(request, 'login.html')

def logout_user(request):
    # Hapus session
    request.session.flush()
    response = HttpResponseRedirect(reverse('login'))
    response.delete_cookie('last_login')
    return response