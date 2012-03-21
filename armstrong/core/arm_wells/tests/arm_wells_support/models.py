from django.db import models
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType

from ...models import WellBase, NodeBase, WellTypeBase, WellType


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


class MissingFieldWell(WellBase):
    # missing the `type` field
    pass


class MissingFieldWellNode(NodeBase):
    # missing the `well` field
    pass


class NewWell(WellBase):
    type = models.ForeignKey(WellType)


class NewNode(NodeBase):
    well = models.ForeignKey(NewWell, related_name="nodes")


class WrongRelationWell(WellBase):
    type = models.ForeignKey(WellType)


class WrongRelationNode(NodeBase):
    well = models.ForeignKey(WrongRelationWell, related_name="foo")


class DifferentWellType(WellTypeBase):
    pass


class DifferentWell(WellBase):
    type = models.ForeignKey(DifferentWellType)
