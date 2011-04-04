class MergedNodesAndQuerySet(object):
    def __init__(self, well, queryset):
        self.well = well
        self.queryset = queryset

    def combined(self):
        total, exclude_ids = [], []
        for a in self.well.nodes.all():
            total.append(a.content_object)
            exclude_ids.append(a.pk)
        queryset = self.queryset.exclude(pk__in=exclude_ids)
        total += [a for a in queryset]
        return total

    def __getslice__(self, i, j):
        return self.combined()[i:j]

    def __len__(self):
        return len(self.combined())
