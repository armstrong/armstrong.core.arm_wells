from django.conf import settings
from django.contrib import admin
from django.contrib.contenttypes import generic
from reversion.admin import VersionAdmin

from armstrong.hatband.options import BackboneInline
from armstrong.hatband.forms import OrderableGenericKeyLookupForm

from . import models


class NodeAdmin(VersionAdmin):
    pass


class NodeInlineAdminForm(OrderableGenericKeyLookupForm):
    class Media:
        js = (
                'hatband/js/jquery-ui-1.8.16.min.js',
                'arm_wells/js/well-node-inline.js',
              )
        css = {'all': ('arm_wells/css/well-node-inline.css',
                       'hatband/css/jquery/ui-lightness/jquery-ui-1.8.16.custom.css',)}


class NodeInline(BackboneInline):
    template = 'arm_wells/admin/well-node-inline.html'
    form = NodeInlineAdminForm
    model = models.Node

    # This is for Grappelli
    sortable_field_name = "order"
    related_lookup_fields = {
        'generic': ['content_type', 'object_id', ]
    }


class WellAdmin(VersionAdmin):
    list_display = ('type', 'pub_date', 'expires', 'active', )
    inlines = [
        NodeInline,
    ]


class WellTypeAdmin(VersionAdmin):
    pass


admin.site.register(models.Node, NodeAdmin)
admin.site.register(models.Well, WellAdmin)
admin.site.register(models.WellType, WellTypeAdmin)
