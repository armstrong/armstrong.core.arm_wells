from django.conf import settings
from django.contrib import admin
from django.contrib.contenttypes import generic
from reversion.admin import VersionAdmin

from . import models


class NodeAdmin(VersionAdmin):
    pass


class NodeGrappelli(VersionAdmin):
    related_lookup_fields = [
        ['content_type', 'object_id',]
    ]


class NodeInline(admin.TabularInline):
    model = models.Node
    extra = 1

    # This is for Grappelli
    sortable_field_name = "order"
    related_lookup_fields = {
        'generic': ['content_type', 'object_id',]
    }


class WellAdmin(VersionAdmin):
    list_display = ('type', 'pub_date', 'expires', 'active', )
    inlines = [
        NodeInline,
    ]


class WellTypeAdmin(VersionAdmin):
    pass


node_admin_class = NodeGrappelli if 'grappelli' in settings.INSTALLED_APPS \
        else NodeAdmin
admin.site.register(models.Node, node_admin_class)
admin.site.register(models.Well, WellAdmin)
admin.site.register(models.WellType, WellTypeAdmin)
