from django.core.exceptions import ImproperlyConfigured
from django.db.models.query import QuerySet
from django.http import HttpRequest
from django.test.client import RequestFactory
import fudge
import random

from .arm_wells_support.models import Story
from ._utils import add_n_random_stories_to_well
from ._utils import generate_random_story
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
            "well_title": self.well.title,
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

    def setUp(self):
        super(QuerySetBackedWellViewTest, self).setUp()
        self.number_in_well = random.randint(1, 5)
        add_n_random_stories_to_well(self.number_in_well, self.well)

    def default_kwargs(self):
        queryset = Story.objects.all()
        kwargs = super(QuerySetBackedWellViewTest, self).default_kwargs()
        kwargs['queryset'] = queryset
        return kwargs

    def test_raises_exception_if_no_queryset_provided(self):
        kwargs = self.default_kwargs()
        del kwargs["queryset"]
        view = self.view_class(**kwargs)
        with self.assertRaises(ImproperlyConfigured) as context_manager:
            view.get_queryset()
        expected = u"'%s' must define 'queryset' or 'model'" % (
                self.view_class.__name__)
        self.assertEqual(expected, context_manager.exception.message)

    def test_get_queryset_returns_well_and_backed_queryset(self):
        number_of_stories = random.randint(1, 5)
        for i in range(number_of_stories):
            generate_random_story()

        view = self.view_class(**self.default_kwargs())

        queryset = view.get_queryset()
        expected = number_of_stories + self.number_in_well
        self.assertEqual(expected, len(queryset))
