import datetime
from django.db import models
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType

from .managers import WellManager


class Well(models.Model):
    title = models.SlugField()
    pub_date = models.DateTimeField()

    objects = WellManager()

    def __unicode__(self):
        return "%s (%s)" % (self.title, self.pub_date)

    def save(self, *args, **kwargs):
        if not self.pub_date:
            self.pub_date = datetime.datetime.now()
        return super(Well, self).save(*args, **kwargs)


class Node(models.Model):
    well = models.ForeignKey(Well, related_name="nodes")
    order = models.IntegerField(default=0)
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    class Meta:
        ordering = ["order"]

    def __unicode__(self):
        return "%s (%d): %s" % (self.well.title, self.order,
                                self.content_object)
