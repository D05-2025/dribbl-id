from django.db import models

class Event(models.Model):
    nama = models.CharField(max_length=100)
    waktu = models.DateTimeField()
    lokasi = models.CharField(max_length=200)
    deskripsi = models.TextField()

    def __str__(self):
        return self.nama
