import datetime
from django.db import models
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.template import RequestContext
from django.template.loader import render_to_string
from django.template import TemplateDoesNotExist
from django.utils.safestring import mark_safe

from .managers import WellManager

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
        self.well_content = []
        self.exclude_ids = []

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
        self.queryset = queryset
        self.well_content = []
        self.exclude_ids = []
        return self

    def render(self, request=None, parent=None):
        if parent is None:
            parent = self
        kwargs = {'parent': parent,
                  'request': request}
        return mark_safe(''.join(n.render(**kwargs) for n in self))

    def initialize(self):
        if self.well_content:
            return

        def process_well(well, managers, ordering):
            for node in well.nodes.all().select_related():
                i = len(ordering)
                model_class = node.content_type.model_class()
                if model_class == Well:
                    managers, ordering = process_well(node.content_object,
                            managers, ordering)
                    continue
                key = "%s.%s" % (model_class.__module__, node.content_type.model)
                if not key in managers:
                    managers[key] = {
                            "name": node.content_type.model,
                            "manager": model_class.objects,
                            "object_ids": [],
                    }
                node_key = "%s.%i" % (node.content_type.model, node.object_id)
                ordering[node_key] = i, well
                managers[key]["object_ids"].append(node.object_id)
                if self.queryset is not None and self.queryset.model is model_class:
                    self.exclude_ids.append(node.object_id)
            return managers, ordering

        # well_managers {'module.model':name, manager, ids}
        self.exclude_ids = []
        well_managers, ordering = process_well(self, {}, {})
        self.well_content = [i for i in range(len(ordering))]

        # at this point we know all the queries we need to run to fetch all
        # content
        for model_data in well_managers.values():
            node_content = model_data["manager"].filter(
                    pk__in=model_data["object_ids"])
            for content in node_content:
                node_key = "%s.%i" % (model_data['name'], content.id)
                idx, well = ordering[node_key]
                self.well_content[idx] = content, well

        if self.queryset is not None:
            self.queryset = self.queryset.exclude(pk__in=self.exclude_ids)



    def __iter__(self):
        self.initialize()
        for content, well in self.well_content:
            yield NodeWrapper(well=well, content_object=content)
        if self.queryset is not None:
            for item in self.queryset:
                yield NodeWrapper(well=self, content_item=item)

    def __getslice__(self, i, j):
        self.initialize()
        total_in_well = len(self.well_content)
        if j <= total_in_well:
            return [NodeWrapper(*args) for args in self.well_content[i:j]]
        end = j - total_in_well
        if i >= total_in_well:
            start = i - total_in_well
            return [NodeWrapper(content, self) for content in self.queryset[start:end]]
        end = j - total_in_well
        return itertools.chain(
                (NodeWrapper(*args) for args in self.well_content[i:]),
                (NodeWrapper(content, self) for content in self.queryset[0:end]))

    def __getitem__(self, i):
        if type(i) != type(1):
            raise TypeError
        self.initialize()
        con_length = len(self.well_content)
        if i < con_length:
            return NodeWrapper(*(self.well_content[i]))
        elif self.queryset:
            return NodeWrapper(self.queryset[i-con_length], self)
        else:
            raise IndexError

    def count(self):
        return self.__len__()

    def __len__(self):
        self.initialize()
        return len(self.well_content) + \
                self.queryset.count()

    def __nonzero__(self):
        return True

    def __getattr__(self, key):
        try:
            return getattr(super(Well, self), key)
        except AttributeError:
            if key != 'queryset' and self.queryset is not None and hasattr(self.queryset, key):
                raise NotImplementedError()
            raise


class NodeRenderMixin(object):
    def render(self, request=None, parent=None):
        render_args = {
                'dictionary':{
                    "well": self.well,
                    "object": self.content_object,
                    "parent": parent,
                },
            }
        if parent == self.well:
            render_args['dictionary']['parent'] = None
        if request:
            render_args['context_instance'] = RequestContext(request)
        return render_to_string("wells/%s/%s/%s.html" % (
                                self.content_object._meta.app_label,
                                self.content_object._meta.object_name.lower(),
                                self.well.type.slug), **render_args)

class Node(NodeRenderMixin, models.Model):
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

class NodeWrapper(NodeRenderMixin):
    def __init__(self, content_object, well):
        self.well = well
        self.content_object = content_object

    def __unicode__(self):
        return "%s: %s" % (self.well.title, self.content_object)

