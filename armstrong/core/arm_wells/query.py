class MergedNodesAndQuerySet(object):
    def __init__(self, well, queryset):
        self.well = well
        self.queryset = queryset
        self.well_content = []

    def initialize(self):
        if self.well_content:
            return
        self.well_content = [a.content_object for a in self.well.nodes.all()]

    def combined(self):
        self.initialize()
        total = self.well_content
        exclude_ids = [a.pk for a in total]
        queryset = self.queryset.exclude(pk__in=exclude_ids)
        total += [a for a in queryset]
        return total

    def __getslice__(self, i, j):
        self.initialize()
        to_slice = self.well_content if j <= len(self.well_content) \
                else self.combined()
        return to_slice[i:j]

    def __len__(self):
        return len(self.combined())
