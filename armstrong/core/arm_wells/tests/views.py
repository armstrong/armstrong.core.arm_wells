from django.core.exceptions import ImproperlyConfigured
from django.http import HttpRequest
import fudge

from ._utils import TestCase

from ..views import SimpleWellView


def generate_view(cls):
    view = SimpleWellView()
    fake_request = fudge.Fake(HttpRequest)
    view.request = fake_request
    return view


def generate_render_context():
    return {
        "params": {
            "template_name": "index.html",
            "well": "front-page",
        },
    }


class SimpleWellViewTest(TestCase):
    def test_raises_exception_when_called_without_params(self):
        view = SimpleWellView()
        self.assertRaises(ImproperlyConfigured, view.render_to_response, {})

    def test_raises_exception_without_template_name_param(self):
        view = SimpleWellView()
        self.assertRaises(ImproperlyConfigured, view.render_to_response,
                {'params': {}})

    def test_does_not_raise_if_template_name_is_present(self):
        view = generate_view(SimpleWellView)
        view.template_name = "index.html"
        args = generate_render_context()
        del args['params']['template_name']
        view.render_to_response(args)

    def test_raises_exception_on_no_well_in_params(self):
        view = generate_view(SimpleWellView)
        args = generate_render_context()
        del args['params']['well']
        self.assertRaises(ImproperlyConfigured, view.render_to_response, args)
