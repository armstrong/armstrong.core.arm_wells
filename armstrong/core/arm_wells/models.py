import datetime
from django.db import models
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.template import RequestContext
from django.template.loader import render_to_string
from django.template import TemplateDoesNotExist

from .managers import WellManager
from .query import MergedNodesAndQuerySet


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

    def merge_with(self, queryset):
        # TODO: Fix this so its not crushing the database.
        #       This is just the first, simplest possible pass to get this
        #       working for the tests.
        return MergedNodesAndQuerySet(self, queryset)

    def render(self, request=None):
        ret = []
        kwargs = {}
        if request:
            kwargs['context_instance'] = RequestContext(request)

        for node in self.nodes.all():
            kwargs["dictionary"] = {
                    "well": self,
                    "object": node.content_object,
            }
            content = node.content_object

            if hasattr(content, "render"):
                ret.append(content.render(request))
            else:
                ret.append(render_to_string("wells/%s/%s/%s.html" % (
                    content._meta.app_label,
                    content._meta.object_name.lower(),
                    self.type.slug), **kwargs))
        return ''.join(ret)


class Node(models.Model):
    well = models.ForeignKey(Well, related_name="nodes")
    order = models.IntegerField(default=0)
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    class Meta:
        ordering = ["order"]

    def __unicode__(self):
        return "%s (%d): %s" % (self.well.type.title, self.order,
                                self.content_object)
