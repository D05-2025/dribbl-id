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
from django.views.decorators.csrf import csrf_exempt


@login_required()
def show_news(request,id):
    news = get_object_or_404(News, pk=id)
    context = {
        'news': news
    }
    return render(request, 'news.html', context)

def add_news_entry_ajax(request):
    title = strip_tags(request.POST.get("title")) 
    content = strip_tags(request.POST.get("content"))
    category = request.POST.get("category")
    thumbnail = request.POST.get("thumbnail")
    user = request.user

    new_news = News(
        title=title, 
        content=content,
        category=category,
        thumbnail=thumbnail,
        user=user
    )
    new_news.save()

    return HttpResponse(b"CREATED", status=201)

@csrf_exempt
def edit_news_entry_ajax(request, id):
    if request.method == "POST":
        news = get_object_or_404(News, pk=id)

        title = strip_tags(request.POST.get("title"))
        content = strip_tags(request.POST.get("content"))
        category = request.POST.get("category")
        thumbnail = request.POST.get("thumbnail")
        is_featured = request.POST.get("is_featured") == 'on'

        news.title = title
        news.content = content
        news.category = category
        news.thumbnail = thumbnail
        news.is_featured = is_featured

        news.save()

        return HttpResponse(b"UPDATED", status=200)
    else:
        return HttpResponse(b"INVALID_METHOD", status=405)

@csrf_exempt
@require_POST
def delete_news_ajax(request, id):
    news = get_object_or_404(News, pk=id)
    news.delete()
    return JsonResponse({"message": "News deleted successfully"})


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
            'title': news.title,
            'content': news.content,
            'category': news.category,
            'published_at': news.published_at,
            'thumbnail': news.thumbnail
        }
        for news in news_list
    ]
    return JsonResponse(data, safe=False)

def show_json_by_id(request, news_id):
    try:
        news = News.objects.select_related('user').get(pk=news_id)
        data = {
            'id': str(news.id),
            'title': news.title,
            'content': news.content,
            'category': news.category,
            'thumbnail': news.thumbnail,
            'created_at': news.created_at.isoformat() if news.created_at else None,
        }
        return JsonResponse(data)
    except News.DoesNotExist:
        return JsonResponse({'detail': 'Not found'}, status=404)


