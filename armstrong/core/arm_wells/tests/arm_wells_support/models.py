from django.db import models
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType

from ...models import WellType
from ...mixins import WellMixin, WellNodeMixin, WellTypeMixin


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


class MissingFieldWell(WellMixin):
    # missing the `type` field
    pass


class MissingFieldWellNode(WellNodeMixin):
    # missing the `well` field
    pass


class NewWell(WellMixin):
    type = models.ForeignKey(WellType)


class NewNode(WellNodeMixin):
    well = models.ForeignKey(NewWell, related_name="nodes")


class WrongRelationWell(WellMixin):
    type = models.ForeignKey(WellType)


class WrongRelationNode(WellNodeMixin):
    well = models.ForeignKey(WrongRelationWell, related_name="foo")


class DifferentWellType(WellTypeMixin):
    pass


class DifferentWell(WellMixin):
    type = models.ForeignKey(DifferentWellType)
