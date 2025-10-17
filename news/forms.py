from django.forms import ModelForm
from news.models import News
from django.utils.html import strip_tags

class NewsForm(ModelForm):
    class Meta:
        model = News
        fields = ['title', 'content', 'category', 'thumbnail']

    def clean_content(self):
        content = self.cleaned_data.get('content', '')
        return strip_tags(content)
    
    def clean_title(self):
        title = self.cleaned_data["title"]
        return strip_tags(title)