from django.db import models
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType

from ...models import BaseWell, BaseWellNode, BaseWellType, WellType


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


class MissingFieldWell(BaseWell):
    # missing the `type` field
    pass


class MissingFieldWellNode(BaseWellNode):
    # missing the `well` field
    pass


class NewWell(BaseWell):
    type = models.ForeignKey(WellType)


class NewNode(BaseWellNode):
    well = models.ForeignKey(NewWell, related_name="nodes")


class WrongRelationWell(BaseWell):
    type = models.ForeignKey(WellType)


class WrongRelationNode(BaseWellNode):
    well = models.ForeignKey(WrongRelationWell, related_name="foo")


class DifferentWellType(BaseWellType):
    pass


class DifferentWell(BaseWell):
    type = models.ForeignKey(DifferentWellType)
