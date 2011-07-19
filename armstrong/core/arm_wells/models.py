import datetime
from django.db import models
from django.db.models.query import QuerySet
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.template import RequestContext
from django.template.base import Context
from django.template.loader import select_template
from django.template import TemplateDoesNotExist
from django.utils.safestring import mark_safe

from .managers import WellManager
from .querysets import MergeQuerySet, GenericForeignKeyQuerySet

import itertools


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
    def content_items(self):
        node_qs = GenericForeignKeyQuerySet(self.nodes.all().select_related())
        if self.queryset is None:
            return node_qs
        else:
            return MergeQuerySet(node_qs, self.queryset)

    @property
    def items(self):
        return NodeWrapperQuerySet(self.content_items, self)

    def merge_with(self, queryset):
        self.queryset = queryset
        return self.items

    def render(self, request=None, parent=None, context=None):
        if parent is None:
            parent = self
        if context is None:
            if request is not None:
                context = RequestContext(request)
            else:
                context = Context()
        kwargs = {'parent': parent,
                  'context': context}
        return mark_safe(''.join(n.render(**kwargs) for n in self.items))


class NodeRenderMixin(object):
    def _template_iter(self):
        for klass in self.content_object.__class__.mro():
            if hasattr(klass, '_meta'):
                yield "wells/%s/%s/%s.html" % (
                        klass._meta.app_label,
                        klass._meta.object_name.lower(),
                        self.well.type.slug)
        yield "wells/default/%s.html" % self.well.type.slug

    def template(self):
        return select_template(self._template_iter())

    def render(self, context=None, parent=None):
        if hasattr(self.content_object, 'render'):
            return self.content_object.render(parent=parent, context=context)
        template = self.template()
        dictionary = {
                    "well": self.well,
                    "object": self.content_object,
                    "parent": parent,
                }
        if parent == self.well:
            dictionary['parent'] = None
        if context is None:
            context = Context()
        context.update(dictionary)
        result = template.render(context)
        context.pop()
        return result

class Node(NodeRenderMixin, models.Model):
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

class NodeWrapper(NodeRenderMixin):
    def __init__(self, content_object, well):
        self.well = well
        self.content_object = content_object

    def __unicode__(self):
        return u"%s: %s" % (self.well.title, self.content_object)

    def __str__(self):
        return self.__unicode__()


class NodeWrapperQuerySet(object):
    def __init__(self, queryset, well):
        self.queryset = queryset
        self.well = well

    def __iter__(self):
        return itertools.imap(lambda x: NodeWrapper(x, self.well),
                self.queryset)

    def __len__(self):
        return len(self.queryset)

    def __getslice__(self, i, j):
        return [NodeWrapper(x, self.well) for x in self.queryset[i:j]]

    def __getitem__(self, i):
        return NodeWrapper(self.queryset[i], self.well)

    def count(self):
        return len(self)

    def __getattr__(self, key):
        try:
            return getattr(super(NodeWrapperQuerySet, self), key)
        except AttributeError:
            if key != 'queryset' and hasattr(QuerySet, key):
                raise NotImplementedError()
            raise
