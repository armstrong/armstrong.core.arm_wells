from django.core.exceptions import ImproperlyConfigured
from django.views.generic.base import TemplateView
from django.views.generic.list import MultipleObjectMixin
from django.utils.translation import ugettext as _

from .models import Well


class SimpleWellView(TemplateView):
    allow_empty = False
    well_title = None

    def __init__(self, *args, **kwargs):
        super(SimpleWellView, self).__init__(*args, **kwargs)
        if not self.well_title:
            raise ImproperlyConfigured(
                    _(u"Expects a `well_title` to be provided"))

    def get_well(self):
        try:
            return Well.objects.get_current(title=self.well_title)
        except Well.DoesNotExist:
            if self.allow_empty:
                return None
            raise

    def get_context_data(self, **kwargs):
        context = super(SimpleWellView, self).get_context_data(**kwargs)
        context["well"] = self.get_well()
        return context


class QuerySetBackedWellView(SimpleWellView, MultipleObjectMixin):
    def get_queryset(self):
        well = self.get_well()
        return (well.items if well is not None
                else super(QuerySetBackedWellView, self).get_queryset())

    def get_well(self):
        well = super(QuerySetBackedWellView, self).get_well()
        if well:
            well.merge_with(super(QuerySetBackedWellView, self).get_queryset())
        return well

    def get_context_data(self, **kwargs):
        queryset = self.get_queryset()
        # manually build context because in Django 1.4, `TemplateView` does not
        # build it properly (bug #16074, see:
        # https://code.djangoproject.com/ticket/16074). This function can be
        # simplified once Django 1.4 support is dropped.
        context = SimpleWellView.get_context_data(self,
            object_list=queryset,
            **kwargs
        )
        context.update(MultipleObjectMixin.get_context_data(self,
            object_list=queryset,
            **kwargs
        ))
        return context
