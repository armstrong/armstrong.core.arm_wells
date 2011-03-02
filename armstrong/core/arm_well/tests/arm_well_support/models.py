from django.db import models

class Story(models.Model):
    title = models.CharField(max_length=100)
    body = models.TextField()

class Image(models.Model):
    title = models.CharField(max_length=100)
    url = models.URLField()

