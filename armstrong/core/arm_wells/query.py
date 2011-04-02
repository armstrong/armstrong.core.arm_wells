class MergedNodesAndQuerySet(object):
    def __init__(self, well, queryset):
        self.well = well
        self.queryset = queryset

    def __len__(self):
        well_nodes = self.well.nodes.all()
        exclude_ids = [a.pk for a in well_nodes]
        total = self.queryset.exclude(pk__in=exclude_ids).count()
        return well_nodes.count() + total
