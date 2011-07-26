from django.core.exceptions import ImproperlyConfigured
from django.views.generic import TemplateView
from django.views.generic.list import MultipleObjectMixin
from django.utils.translation import ugettext as _

from .models import Well


class SimpleWellView(TemplateView):
    well_title = None

    def __init__(self, *args, **kwargs):
        super(SimpleWellView, self).__init__(*args, **kwargs)
        if not self.well_title:
            raise ImproperlyConfigured(
                    _(u"Expects a `well_title` to be provided"))

    def get_well(self):
        return Well.objects.get_current(title=self.well_title)

    def get_context_data(self, **kwargs):
        context = super(SimpleWellView, self).get_context_data(**kwargs)
        context["well"] = self.get_well()
        return context


class QuerySetBackedWellView(SimpleWellView, MultipleObjectMixin):
    def get_queryset(self):
        return self.get_well().items

    def get_well(self):
        well = super(QuerySetBackedWellView, self).get_well()
        well.merge_with(super(QuerySetBackedWellView, self).get_queryset())
        return well

