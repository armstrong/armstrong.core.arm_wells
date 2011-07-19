from functools import wraps
import itertools

def requires_prep(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if args[0].needs_prep:
            args[0]._prep()
        assert(not args[0].needs_prep)
        return func(*args, **kwargs)
    return wrapper


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
        if type(i) is not int:
            raise TypeError
        if i < len(self.queryset):
            return self.queryset[i]
        elif i < len(self):
            return self.queryset2[i - len(self.queryset)]
        else:
            raise IndexError("list index out of range")

    @requires_prep
    def count(self):
        return self.__len__()

    @requires_prep
    def __getslice__(self, i, j):
        qs_len = len(self.queryset)
        if j <= qs_len:
            return self.queryset[i:j]
        end = j - qs_len
        if i >= qs_len:
            start = i - qs_len
            return self.queryset2[start:end]
        return itertools.chain(self.queryset[i:], self.queryset2[0:end])


class GenericForeignKeyQuerySet(object):
    def __init__(self, queryset):
        self.queryset = queryset
        self.needs_prep = True

    def _prep(self):
        managers = {}
        ordering = {}
        for i, obj in enumerate(self.queryset):
            model_class = obj.content_type.model_class()
            key = "%s.%s" % (model_class.__module__, obj.content_type.model)
            if not key in managers:
                managers[key] = {
                        "name": obj.content_type.model,
                        # _default_manager is undocumented. If django ever
                        # changes/documents a way to get the default
                        # manager, this will need to change too
                        "manager": model_class._default_manager,
                        "object_ids": [],
                }
            node_key = "%s.%i" % (obj.content_type.model, obj.object_id)
            ordering[node_key] = i
            managers[key]["object_ids"].append(obj.object_id)

        self.content = [None] * len(ordering)
        for model_data in managers.values():
            node_content = model_data["manager"].filter(
                    pk__in=model_data["object_ids"])
            for obj in node_content:
                node_key = "%s.%i" % (model_data['name'], obj.pk)
                idx = ordering[node_key]
                self.content[idx] = obj
        self.needs_prep = False

    @requires_prep
    def __iter__(self):
        return self.content.__iter__()

    @requires_prep
    def __len__(self):
        return len(self.content)

    @requires_prep
    def __getitem__(self, i):
        return self.content.__getitem__(i)

