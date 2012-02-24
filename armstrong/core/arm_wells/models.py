from django.db import models

from .mixins import WellTypeMixin, WellMixin, WellNodeMixin


class WellType(WellTypeMixin):
    pass


class Well(WellMixin):
    type = models.ForeignKey(WellType)


class Node(WellNodeMixin):
    well = models.ForeignKey(Well, related_name="nodes")
