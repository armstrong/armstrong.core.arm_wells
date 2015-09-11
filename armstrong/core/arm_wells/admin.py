from django.contrib import admin
from django.utils.safestring import mark_safe
from reversion.admin import VersionAdmin

from . import models


class NodeAdmin(VersionAdmin):
    pass


class NodeInline(admin.TabularInline):
    model = models.Node


class WellAdmin(VersionAdmin):
    list_display = ('type', 'pub_date', 'expires', 'active', )
    inlines = [
        NodeInline,
    ]
    save_as = True


class WellTypeAdmin(VersionAdmin):
    pass


admin.site.register(models.Node, NodeAdmin)
admin.site.register(models.Well, WellAdmin)
admin.site.register(models.WellType, WellTypeAdmin)
