from django.db import models
from authentication.models import CustomUser

class Event(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    date = models.DateTimeField()
    is_public = models.BooleanField(default=True)
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    image_url = models.URLField(null=True, blank=True)  # pakai URL gambar
    location = models.CharField(max_length=255, null=True, blank=True)
    time = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return self.title
