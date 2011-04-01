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
        # TODO: Fix this so its not crushing the database.
        #       This is just the first, simplest possible pass to get this
        #       working for the tests.
        raw_queryset = super(QuerySetBackedWellView, self).get_queryset()
        well_content, excluded_ids = [], []
        for a in self.get_well().nodes.all():
            well_content.append(a)
            excluded_ids.append(a.pk)
        other_content = [a for a in raw_queryset.exclude(pk__in=excluded_ids)]
        return well_content + other_content
