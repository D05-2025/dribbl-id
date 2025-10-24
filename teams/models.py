from django.db import models

# Create your models here.
class Team(models.Model):
    REGION = [
        ('us', 'United States'),
        ('eu', 'Europe'),
        ('as', 'Asia'),
        ('af', 'Africa'),
        ('sa', 'South America'),
        ('oc', 'Oceania'),
    ]

    name = models.CharField(primary_key=True, max_length=100)
    logo = models.URLField(blank=True, null=True)
    region = models.CharField(max_length=2, choices=REGION, default='us')
    founded = models.DateField()
    description = models.TextField()

    def __str__(self):
        return self.name