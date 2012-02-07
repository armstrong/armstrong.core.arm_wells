from functools import wraps
from django.db.models.query import QuerySet
import itertools

def requires_prep(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if args[0].needs_prep:
            args[0]._prep()
        assert(not args[0].needs_prep)
        return func(*args, **kwargs)
    return wrapper


class FilterException(Exception):
    pass


class MergeQuerySet(object):
    """
    This class provides a queryset-like object that merges two querysets
    and de-duplicates
    """
    def __init__(self, queryset, queryset2):
        self.queryset = queryset
        self.queryset2 = queryset2
        self.needs_prep = True

    def _prep(self):
        exclude_ids = []
        query_model = self.queryset2.model
        for obj in self.queryset:
            if query_model == obj.__class__:
                exclude_ids.append(obj.id)
            elif query_model in obj.__class__._meta.parents:
                parent_field = obj.__class__._meta.parents[query_model]
                exclude_ids.append(parent_field.value_from_object(obj))
        self.queryset2 = self.queryset2.exclude(id__in=exclude_ids)
        self.needs_prep = False

    @requires_prep
    def __iter__(self):
        return itertools.chain(self.queryset, self.queryset2)

    @requires_prep
    def __len__(self):
        return len(self.queryset) + len(self.queryset2)

    @requires_prep
    def __getitem__(self, i):
        if type(i) is slice:
            start, stop, step = i.indices(len(self))
            if step != 1:
                raise TypeError('MergeQuerySet only supports simple slices')
            return self.__getslice__(start, stop)
        elif type(i) is not int:
            raise TypeError
        if i < len(self.queryset):
            return self.queryset[i]
        elif i < len(self):
            return self.queryset2[i - len(self.queryset)]
        else:
            raise IndexError("list index out of range")

    def filter(self, *args, **kwargs):
        if not self.needs_prep:
            raise FilterException("Filter called after queryset already merged")
        return MergeQuerySet(self.queryset.filter(*args, **kwargs),
                self.queryset2.filter(*args, **kwargs))

    @requires_prep
    def count(self):
        return self.queryset.count() + self.queryset2.count()

    @requires_prep
    def __getslice__(self, i, j):
        qs_len = len(self.queryset)
        if j <= qs_len:
            return self.queryset[i:j]
        end = j - qs_len
        if i >= qs_len:
            start = i - qs_len
            return self.queryset2[start:end]
        return list(itertools.chain(self.queryset[i:], self.queryset2[0:end]))

    def __getattr__(self, key):
        try:
            return getattr(super(MergeQuerySet, self), key)
        except AttributeError:
            if key != 'queryset' and hasattr(QuerySet, key):
                raise NotImplementedError()
            raise
    

class GenericForeignKeyQuerySet(object):
    def __init__(self, queryset, gfk='content_object'):
        self.queryset = queryset
        model = self.queryset.model
        for field in model._meta.virtual_fields:
            if field.name == gfk:
                self.ct_field = field.ct_field
                self.fk_field = field.fk_field
                break
        else:
            raise ValueError("No GenericForeignKey named %s on the %s model" \
                    % (gfk, model))
        self.needs_prep = True

    def _prep(self):
        managers = {}
        ordering = {}
        for i, obj in enumerate(self.queryset):
            obj_ct = getattr(obj, self.ct_field)
            obj_fk = getattr(obj, self.fk_field)
            model_class = obj_ct.model_class()
            key = "%s.%s" % (model_class.__module__, obj_ct.model)
            if not key in managers:
                managers[key] = {
                        "name": obj_ct.model,
                        # _default_manager is undocumented. If django ever
                        # changes/documents a way to get the default
                        # manager, this will need to change too
                        "manager": model_class._default_manager,
                        "object_ids": [],
                }
            node_key = "%s.%i" % (obj_ct.model, obj_fk)
            ordering.setdefault(node_key, []).append(i)
            managers[key]["object_ids"].append(obj_fk)

        self.content = [None] * len(self.queryset)
        for model_data in managers.values():
            node_content = model_data["manager"].filter(
                    pk__in=model_data["object_ids"])
            for obj in node_content:
                node_key = "%s.%i" % (model_data['name'], obj.pk)
                for idx in ordering[node_key]:
                    self.content[idx] = obj
        self.needs_prep = False

    @requires_prep
    def __iter__(self):
        return self.content.__iter__()

    @requires_prep
    def __len__(self):
        return len(self.content)

    def count(self):
        return self.__len__()

    @requires_prep
    def __getitem__(self, i):
        return self.content.__getitem__(i)

    def filter(self, *args, **kwargs):
        if kwargs:
            raise FilterException("GenericForeignKeyQuerySets cannot be filtered")
        return self

    def __getattr__(self, key):
        try:
            return getattr(super(GenericForeignKeyQuerySet, self), key)
        except AttributeError:
            if key != 'queryset' and hasattr(QuerySet, key):
                raise NotImplementedError()
            raise
