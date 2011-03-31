from django.core.exceptions import ImproperlyConfigured
from django.http import HttpRequest
import fudge

from ._utils import generate_random_well
from ._utils import TestCase

from ..views import SimpleWellView


def generate_view(cls):
    view = SimpleWellView()
    fake_request = fudge.Fake(HttpRequest)
    view.request = fake_request
    return view


def generate_render_context(well_title=None):
    if not well_title:
        well = generate_random_well()
        well_title = well.type.title

    return {
        "params": {
            "template_name": "index.html",
            "well_title": well_title,
        },
    }


class SimpleWellViewTest(TestCase):
    view_class = SimpleWellView

    def test_raises_exception_when_called_without_params(self):
        view = self.view_class()
        self.assertRaises(ImproperlyConfigured, view.render_to_response, {})

    def test_raises_exception_without_template_name_param(self):
        view = self.view_class()
        self.assertRaises(ImproperlyConfigured, view.render_to_response,
                {'params': {}})

    def test_does_not_raise_if_template_name_is_present(self):
        view = generate_view(self.view_class)
        view.template_name = "index.html"
        args = generate_render_context()
        del args['params']['template_name']
        view.render_to_response(args)

    def test_raises_exception_on_no_well_in_params(self):
        view = generate_view(self.view_class)
        args = generate_render_context()
        del args['params']['well_title']
        self.assertRaises(ImproperlyConfigured, view.render_to_response, args)

    def test_passes_a_well_to_the_render(self):
        well = generate_random_well()
        view = generate_view(self.view_class)
        args = generate_render_context(well_title=well.type.title)
        result = view.render_to_response(args)
        self.assertInContext('well', well, result)
