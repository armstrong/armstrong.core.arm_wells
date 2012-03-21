import datetime

from django.db import models
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType

from .managers import WellManager
from .querysets import MergeQuerySet, GenericForeignKeyQuerySet


class WellTypeBase(models.Model):
    """
    Abstract WellType

    Provides all the functionality of a WellType.
    Can be implemented as a non-abstract Model without modification.

    """
    title = models.CharField(max_length=100)
    slug = models.SlugField()

    class Meta:
        abstract = True

    def __unicode__(self):
        return self.title


class WellBase(models.Model):
    """
    Abstract Well

    Provides all the functionality of a Well but lacks the
    relationship to the actual WellType.

    Requirements:
      1. A ``type`` field with a ``ForeignKey`` to a non-abstract WellType Model.

        ex: ``type = models.ForeignKey(MyWellTypeModel)``

    """
    @property
    def type(self):
        raise NotImplementedError("The 'type' field must be implemented")

    pub_date = models.DateTimeField()
    expires = models.DateTimeField(null=True, blank=True)
    active = models.BooleanField(default=True)

    objects = WellManager()

    class Meta:
        abstract = True

    def __init__(self, *args, **kwargs):
        super(WellBase, self).__init__(*args, **kwargs)
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
        return super(WellBase, self).save(*args, **kwargs)

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


class NodeBase(models.Model):
    """
    Abstract Node

    Provides all the functionality of a Node but lacks the
    relationship to the actual Well.

    Requirements:
      1. A ``well`` field with a ``ForeignKey`` to a non-abstract Well Model.
      2. The ``well`` field must use "nodes" as the ``related_name``.

        ex: ``well = models.ForeignKey(MyWellModel, related_name="nodes")``

    """
    @property
    def well(self):
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


#
# Concrete implementations
#
class WellType(WellTypeBase):
    """
    Provides a concrete implementation of the ``WellTypeBase`` class.

    """
    pass


class Well(WellBase):
    """
    Provides a concrete implementation of the ``WellBase`` class.

    Adds the required relation of the Well to the WellType.

    """
    type = models.ForeignKey(WellType)


class Node(NodeBase):
    """
    Provides a concrete implementation of the ``NodeBase`` class.

    Adds the required relation of the Node to the Well.

    """
    well = models.ForeignKey(Well, related_name="nodes")
