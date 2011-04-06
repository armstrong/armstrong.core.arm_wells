import itertools


class MergedNodesAndQuerySet(object):
    def __init__(self, well, queryset):
        self.well = well
        self.queryset = queryset
        self.well_content = []
        self.exclude_ids = []

    def initialize(self):
        if self.well_content:
            return

        well_managers = {}
        for node in self.well.nodes.all().select_related():
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
            return self.queryset.exclude(pk__in=self.exclude_ids)[start:end]
        return itertools.chain(self.well_content,
                self.queryset.exclude(pk__in=self.exclude_ids)[0:end])

    def count(self):
        return self.__len__()

    def __len__(self):
        self.initialize()
        return len(self.well_content) + \
                self.queryset.exclude(pk__in=self.exclude_ids).count()

    def __getattr__(self, key):
        if hasattr(self.queryset, key):
            raise NotImplementedError()
        raise AttributeError("%s not an attribute on %s" % (key,
            self.__class__.__name__))
