from django.core.exceptions import ImproperlyConfigured
from django.db.models.query import QuerySet
from django.http import HttpRequest
from django.test.client import RequestFactory
import fudge

from ._utils import generate_random_well
from ._utils import TestCase

from ..views import SimpleWellView
from ..views import QuerySetBackedWellView


class WellViewTestCase(TestCase):
    def setUp(self):
        super(WellViewTestCase, self).setUp()
        self.well = generate_random_well()

class SimpleWellViewTest(WellViewTestCase):
    view_class = SimpleWellView

    def default_kwargs(self):
        return {
            "template_name": "index.html",
            "well_title": self.well.type.title,
        }

    def test_raises_exception_without_template_name_param(self):
        kwargs = self.default_kwargs()
        del kwargs["template_name"]
        view = self.view_class.as_view(**kwargs)
        with self.assertRaises(ImproperlyConfigured) as context_manager:
            response = view(self.factory.get("/"))

        self.assertEqual(
            "TemplateResponseMixin requires either a definition of "
            "'template_name' or an implementation of "
            "'get_template_names()'",
            context_manager.exception.message)

    def test_does_not_raise_if_template_name_is_present(self):
        view = self.view_class.as_view(**self.default_kwargs())
        view(self.factory.get("/"))

    def test_raises_exception_on_no_well_in_params(self):
        kwargs = self.default_kwargs()
        del kwargs["well_title"]
        view = self.view_class.as_view(**kwargs)
        self.assertRaises(ImproperlyConfigured, view, self.factory.get("/"))

    def test_passes_a_well_to_the_render(self):
        view = self.view_class.as_view(**self.default_kwargs())
        result = view(self.factory.get("/"))
        self.assertInContext('well', self.well, result)


class QuerySetBackedWellViewTest(SimpleWellViewTest):
    view_class = QuerySetBackedWellView

    def default_kwargs(self):
        kwargs = super(QuerySetBackedWellViewTest, self).default_kwargs()
        kwargs['queryset'] = fudge.Fake(QuerySet)
        return kwargs

    def test_raises_exception_if_no_queryset_provided(self):
        kwargs = self.default_kwargs()
        del kwargs["queryset"]
        view = self.view_class.as_view(**kwargs)
        self.assertRaises(ImproperlyConfigured, view, self.factory.get("/"))
