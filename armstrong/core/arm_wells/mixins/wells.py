import datetime
from django.db import models
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType

from ..managers import WellManager
from ..querysets import MergeQuerySet, GenericForeignKeyQuerySet


class WellTypeMixin(models.Model):
    title = models.CharField(max_length=100)
    slug = models.SlugField()

    class Meta:
        abstract = True

    def __unicode__(self):
        return self.title


class WellMixin(models.Model):
    @property
    def type(self):
        # ex: type = models.ForeignKey(MyWellTypeModel)
        raise NotImplementedError("The 'type' field must be implemented")

    pub_date = models.DateTimeField()
    expires = models.DateTimeField(null=True, blank=True)
    active = models.BooleanField(default=True)

    objects = WellManager()

    class Meta:
        abstract = True

    def __init__(self, *args, **kwargs):
        super(WellMixin, self).__init__(*args, **kwargs)
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
        return super(WellMixin, self).save(*args, **kwargs)

    @property
    def items(self):
        node_qs = GenericForeignKeyQuerySet(self.nodes.all())
        if self.queryset is None:
            return node_qs
        else:
            return MergeQuerySet(node_qs, self.queryset)

    def merge_with(self, queryset):
        self.queryset = queryset
        return self.items


class WellNodeMixin(models.Model):
    @property
    def well(self):
        # ex: well = models.ForeignKey(MyWellModel, related_name="nodes")
        raise NotImplementedError("The 'well' field must be implemented")

    order = models.IntegerField(default=0)
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    class Meta:
        abstract = True
        ordering = ["order"]

    def __unicode__(self):
        return u"%s (%d): %s" % (self.well.title, self.order,
                                 self.content_object)