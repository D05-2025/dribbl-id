from django.db import models

class Player(models.Model):
    name = models.CharField(max_length=100)
    position = models.CharField(max_length=10)
    team = models.CharField(max_length=50)
    points_per_game = models.FloatField()
    assists_per_game = models.FloatField()
    rebounds_per_game = models.FloatField()

    def __str__(self):
        return self.name
