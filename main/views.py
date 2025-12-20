from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
from .models import CustomUser
import datetime, requests
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse

#buat 

def proxy_image(request):
    image_url = request.GET.get('url')
    if not image_url:
        return HttpResponse('No URL provided', status=400)
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
            'Referer': 'https://www.google.com/',
        }

        response = requests.get(image_url, headers=headers, timeout=10)
        response.raise_for_status()
        
        return HttpResponse(
            response.content,
            content_type=response.headers.get('Content-Type', 'image/jpeg')
        )
    except requests.RequestException as e:
        return HttpResponse(f'Error fetching image: {str(e)}', status=500)

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

        user = CustomUser.objects.create(username=username, role=role)
        user.set_password(password) 
        user.save()

        messages.success(request, 'Akun berhasil dibuat! Silakan login.')
        return redirect('main:login') 

    return render(request, 'register.html')

def login_user(request):
    if request.method == 'POST':
        username = request.POST.get('username') or ''
        password = request.POST.get('password') or ''

        try:
            user = CustomUser.objects.get(username=username)
            if user.check_password(password):
                # Simpan session minimal
                request.session['user_id'] = str(user.id)
                request.session['username'] = user.username
                request.session['role'] = user.role
                
                user.save()
                
                response = HttpResponseRedirect(reverse("main:show_main"))
                response.set_cookie('last_login', str(datetime.datetime.now()))
                messages.success(request, f'Selamat datang, {user.username}!')
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
    messages.info(request, 'Anda telah logout.')
    return response