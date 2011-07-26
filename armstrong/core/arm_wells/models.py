import datetime
from django.db import models
from django.db.models.query import QuerySet
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType

from .managers import WellManager
from .querysets import MergeQuerySet, GenericForeignKeyQuerySet


class WellType(models.Model):
    title = models.CharField(max_length=100)
    slug = models.SlugField()

    def __unicode__(self):
        return self.title


class Well(models.Model):
    type = models.ForeignKey(WellType)
    pub_date = models.DateTimeField()
    expires = models.DateTimeField(null=True, blank=True)
    active = models.BooleanField(default=True)

    objects = WellManager()

    def __init__(self, *args, **kwargs):
        super(Well, self).__init__(*args, **kwargs)
        self.queryset = None

    @property
    def title(self):
        return self.type.title

    def __unicode__(self):
        return "%s (%s - %s)" % (self.type, self.pub_date,
                                 self.expires or "Never")

    def save(self, *args, **kwargs):
        if not self.pub_date:
            self.pub_date = datetime.datetime.now()
        return super(Well, self).save(*args, **kwargs)

    @property
    def items(self):
        node_qs = GenericForeignKeyQuerySet(self.nodes.all().select_related())
        if self.queryset is None:
            return node_qs
        else:
            return MergeQuerySet(node_qs, self.queryset)

    def merge_with(self, queryset):
        self.queryset = queryset
        return self.items


class Node(models.Model):
    well = models.ForeignKey(Well, related_name="nodes")
    order = models.IntegerField(default=0)
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    class Meta:
        ordering = ["order"]

    def __unicode__(self):
        return u"%s (%d): %s" % (self.well.title, self.order,
                                self.content_object)
