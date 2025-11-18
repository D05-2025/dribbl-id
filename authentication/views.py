from django.contrib.auth import login as auth_login, logout as auth_logout
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from main.models import CustomUser 

import json

# Create your views here.
@csrf_exempt
def login(request):
    username = request.POST['username']
    password = request.POST['password']
    user = CustomUser.objects.get(username=username,password=password)
    if user is not None:
        if user.is_active:
            auth_login(request, user)
            # Login status successful.
            return JsonResponse({
                "username": user.username,
                "role": user.role,
                "status": True,
                "message": "Login successful!"
                # Add other data if you want to send data to Flutter.
            }, status=200)
        else:
            return JsonResponse({
                "status": False,
                "message": "Login failed, account is disabled."
            }, status=401)

    else:
        return JsonResponse({
            "status": False,
            "message": "Login failed, please check your username or password."
        }, status=401)
    
@csrf_exempt
def register(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        username = data['username']
        password = data['password']
        role = data['role']
        
        # Check if the username is already taken
        if CustomUser.objects.filter(username=username).exists():
            return JsonResponse({
                "status": False,
                "message": "Username already exists."
            }, status=400)
        
        # Create the new user
        user = CustomUser.objects.create(username=username, password=password, role=role)
        user.save()
        
        return JsonResponse({
            "username": user.username,
            "role": user.role, 
            "status": 'success',
            "message": "User created successfully!"
        }, status=200)
    
    else:
        return JsonResponse({
            "status": False,
            "message": "Invalid request method."
        }, status=400)

@csrf_exempt
def logout(request):
    username = request.user.username
    try:
        auth_logout(request)
        return JsonResponse({
            "username": username,
            "status": True,
            "message": "Logged out successfully!"
        }, status=200)
    except:
        return JsonResponse({
            "status": False,
            "message": "Logout failed."
        }, status=401)