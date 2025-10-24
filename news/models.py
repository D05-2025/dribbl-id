from django.db import models
import uuid

class News(models.Model):
    CATEGORY_CHOICES = [
        ('nba', 'NBA'),
        ('ibl', 'IBL'),
        ('fiba', 'FIBA'),
        ('transfer', 'Transfers & Trades'),
        ('highlight', 'Game Highlights'),
        ('analysis', 'Team & Player Analysis'),
    ]
    
    user = models.ForeignKey('main.CustomUser', on_delete=models.CASCADE, null=True, blank=True)
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    content = models.TextField()
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    published_at = models.DateTimeField(auto_now_add=True)
    thumbnail = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.title