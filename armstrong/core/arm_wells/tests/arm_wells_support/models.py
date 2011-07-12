from django.db import models


class Story(models.Model):
    title = models.CharField(max_length=100)
    body = models.TextField()

    def __unicode__(self):
        return self.title


class StoryChild(Story):
    comment = models.CharField(max_length=100)


class Image(models.Model):
    title = models.CharField(max_length=100)
    url = models.URLField()
