from django.db import models
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType

class Well(models.Model):
    title = models.SlugField()

    def add(self, *args, **kwargs):
        pass

class Node(models.Model):
    well = models.ForeignKey(Well, related_name="nodes")
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')

