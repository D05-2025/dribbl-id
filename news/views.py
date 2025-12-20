import datetime
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.core import serializers
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils.html import strip_tags
from news.models import News
from news.forms import NewsForm
from django.contrib.auth.decorators import login_required
from main.decorators import login_required_custom
import json
import requests

from django.db.models import Q

def proxy_image(request):
    image_url = request.GET.get('url')
    if not image_url:
        return HttpResponse('No URL provided', status=400)
    
    try:
        response = requests.get(image_url, timeout=10)
        response.raise_for_status()
        
        return HttpResponse(
            response.content,
            content_type=response.headers.get('Content-Type', 'image/jpeg')
        )
    except requests.RequestException as e:
        return HttpResponse(f'Error fetching image: {str(e)}', status=500)

@csrf_exempt
def add_news_flutter(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            title = strip_tags(data.get("title", "").strip())
            content = strip_tags(data.get("content", "").strip())
            category = data.get("category", "").strip()
            thumbnail = data.get("thumbnail", "").strip() or None

            new_news = News(
                title=title, 
                content=content,
                category=category,
                thumbnail=thumbnail,
                user=request.user if request.user.is_authenticated else None
            )
            new_news.save()

            return JsonResponse({"status": "success"}, status=200)
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=400)
    return JsonResponse({"status": "error", "message": "Invalid method"}, status=405)


@login_required
def show_news_page(request):
    category_filter = request.GET.get('category', '')
    sort_by = request.GET.get('sort', 'newest')
    search_query = request.GET.get('search', '')
    
    news_list = News.objects.all()
    
    if category_filter:
        news_list = news_list.filter(category=category_filter)
    
    if search_query:
        news_list = news_list.filter(
            Q(title__icontains=search_query) | 
            Q(content__icontains=search_query)
        )
    
    if sort_by == 'oldest':
        news_list = news_list.order_by('published_at')
    elif sort_by == 'title_asc':
        news_list = news_list.order_by('title')
    elif sort_by == 'title_desc':
        news_list = news_list.order_by('-title')
    else:  
        news_list = news_list.order_by('-published_at')
    
    categories = News.CATEGORY_CHOICES
    
    context = {
        'news_list': news_list,
        'categories': categories,
        'selected_category': category_filter,
        'selected_sort': sort_by,
        'search_query': search_query,
        'user': request.user
    }
    return render(request, 'news_page.html', context)

def show_news_detail(request, news_id):
    news = get_object_or_404(News, id=news_id)
    context = {
        'news': news,
    }
    return render(request, 'news_detail.html', context)

@csrf_exempt
@require_POST
def add_news_entry_ajax(request):
    try:
        if not request.user.is_authenticated:
            return JsonResponse({
                "status": "error",
                "message": "User not authenticated"
            }, status=401)

        if request.user.role != 'admin':
            return JsonResponse({
                "status": "error",
                "message": "Only admin users can create news"
            }, status=403)

        title = strip_tags(request.POST.get("title", "").strip())
        content = strip_tags(request.POST.get("content", "").strip())
        category = request.POST.get("category", "").strip()
        thumbnail = request.POST.get("thumbnail", "").strip() or None

        if not title:
            return JsonResponse({
                "status": "error", 
                "message": "Title is required"
            }, status=400)
        
        if not content:
            return JsonResponse({
                "status": "error",
                "message": "Content is required" 
            }, status=400)
            
        if not category:
            return JsonResponse({
                "status": "error",
                "message": "Category is required"
            }, status=400)

        new_news = News(
            title=title, 
            content=content,
            category=category,
            thumbnail=thumbnail,
            user=request.user
        )
        new_news.save()

        return JsonResponse({
            "status": "success",
            "message": "News created successfully",
            "news_id": str(new_news.id)
        }, status=201)

    except Exception as e:
        print(f"Error in add_news_entry_ajax: {str(e)}")
        return JsonResponse({
            "status": "error",
            "message": f"Server error: {str(e)}"
        }, status=500)

@csrf_exempt
def edit_news_entry_ajax(request, id):
    if not request.user.is_authenticated:
        return JsonResponse({"status": "error"}, status=401)

    if request.user.role != 'admin':
        return JsonResponse({"status": "error"}, status=403)

    if request.method == "POST":
        data = json.loads(request.body)

        news = get_object_or_404(News, pk=id)

        news.title = strip_tags(data.get("title", ""))
        news.content = strip_tags(data.get("content", ""))
        news.category = data.get("category")
        news.thumbnail = data.get("thumbnail")
        news.save()

        return JsonResponse({"status": "success"})


@csrf_exempt
@require_POST 
def delete_news(request, id):
    if not request.user.is_authenticated:
        return JsonResponse({"status": "error", "message": "User not authenticated"}, status=401)

    if request.user.role != 'admin':
        return JsonResponse({"status": "error", "message": "Only admin can delete news"}, status=403)

    try:
        news = get_object_or_404(News, pk=id)
        news.delete()
        return JsonResponse({"status": "success", "message": "News deleted successfully"})
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)

def show_xml(request):
    news = News.objects.all()
    xml_data = serializers.serialize("xml", news)
    return HttpResponse(xml_data, content_type="application/xml")

def show_xml_by_id(request, id):
    try:
        news = get_object_or_404(News, id=id)
        xml_data = serializers.serialize("xml", [news])
        return HttpResponse(xml_data, content_type="application/xml")
    except News.DoesNotExist:
        return HttpResponse(status=404)
    
def show_json(request):
    news_list = News.objects.all()
    data = [
        {
            'id': str(news.id),
            'user_id': str(news.user.id) if news.user else None,
            'title': news.title,
            'content': news.content,
            'category': news.category,
            'thumbnail': news.thumbnail,
            'created_at': news.published_at.isoformat(), 
        }
        for news in news_list
    ]
    return JsonResponse(data, safe=False)

def get_news_json(request, id):
    try:
        news = get_object_or_404(News, pk=id)
        news_data = {
            'id': str(news.id),
            'title': news.title,
            'content': news.content,
            'category': news.category,
            'thumbnail': news.thumbnail or '',  
            'user_id': str(news.user.id) if news.user else None
        }
        return JsonResponse(news_data)
    except Exception as e:
        print(f"Error in get_news_json: {str(e)}")
        return JsonResponse({"status": "error", "message": str(e)}, status=500)

def show_json_by_id(request, news_id):
    try:
        news = News.objects.select_related('user').get(pk=news_id)
        data = {
            'id': str(news.id),
            'title': news.title,
            'content': news.content,
            'category': news.category,
            'thumbnail': news.thumbnail,
            'created_at': news.published_at.isoformat() if news.published_at else None,
        }
        return JsonResponse(data)
    except News.DoesNotExist:
        return JsonResponse({'detail': 'Not found'}, status=404)


