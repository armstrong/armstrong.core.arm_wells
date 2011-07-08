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
        ret = []
        kwargs = {}
        if request:
            kwargs['context_instance'] = RequestContext(request)

        for node in self.nodes.all():
            kwargs["dictionary"] = {
                    "well": self,
                    "object": node.content_object,
                    "parent": parent,
            }
            content = node.content_object

            if hasattr(content, "render"):
                ret.append(content.render(request, parent=self))
            else:
                ret.append(render_to_string("wells/%s/%s/%s.html" % (
                    content._meta.app_label,
                    content._meta.object_name.lower(),
                    self.type.slug), **kwargs))
        return mark_safe(''.join(ret))

    def initialize(self):
        if self.well_content:
            return

        well_managers = {}
        for node in self.nodes.all().select_related():
            model_class = node.content_type.model_class()
            key = "%s.%s" % (model_class.__module__, node.content_type.model)
            if not key in well_managers:
                well_managers[key] = {
                        "name": node.content_type.model,
                        "manager": model_class.objects,
                        "object_ids": [],
                }
            self.well_content.append((node.content_type.model, node.object_id))
            well_managers[key]["object_ids"].append(node.object_id)
            if self.queryset.model is model_class:
                self.exclude_ids.append(node.object_id)
        self.queryset = self.queryset.exclude(pk__in=self.exclude_ids)

        for model_data in well_managers.values():
            node_content = model_data["manager"].filter(
                    pk__in=model_data["object_ids"])
            for content in node_content:
                idx = self.well_content.index((model_data["name"], content.pk))
                self.well_content[idx] = content

    def __getslice__(self, i, j):
        self.initialize()
        total_in_well = len(self.well_content)
        if j <= total_in_well:
            return self.well_content[i:j]
        end = j - total_in_well
        if i >= total_in_well:
            start = i - total_in_well
            return self.queryset[start:end]
        return itertools.chain(self.well_content[i:],
                self.queryset[0:end])

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


