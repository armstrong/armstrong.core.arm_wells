from django.db import models
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType

class Content(models.Model):
    title = models.CharField(max_length=100)
    def __unicode__(self):
        return self.title


class Story(Content):
    body = models.TextField()


class StoryChild(Story):
    comment = models.CharField(max_length=100)


class Image(Content):
    url = models.URLField()


class OddNode(models.Model):
    foo = models.ForeignKey(ContentType)
    bar = models.PositiveIntegerField()
    baz = generic.GenericForeignKey('foo', 'bar')
