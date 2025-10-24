from django.db import models
from django.utils import timezone
from authentication.models import CustomUser

class Event(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    date = models.DateField()
    time = models.TimeField(null=True, blank=True)
    location = models.CharField(max_length=255, null=True, blank=True)
    image_url = models.URLField(null=True, blank=True)
    is_public = models.BooleanField(default=True)
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date', '-created_at']
        verbose_name = 'Event'
        verbose_name_plural = 'Events'

    def __str__(self):
        return self.title