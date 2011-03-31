import random

from django.test import TestCase as DjangoTestCase
from django.test.client import RequestFactory

from .arm_wells_support.models import Story
from ..models import Well
from ..models import WellType


def generate_random_story():
    title = "Random title %d" % random.randint(100, 200)
    body = "Some random text %d" % random.randint(100, 200)
    return Story.objects.create(title=title, body=body)


def generate_random_well():
    return Well.objects.create(type=generate_random_welltype())


def generate_random_welltype():
    r = random.randint(100, 200)
    title = "Random Well %d" % r
    slug = "random-well-%d" % r
    return WellType.objects.create(title=title, slug=slug)


class TestCase(DjangoTestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def assertInContext(self, var_name, other, template_or_context):
        # TODO: support passing in a straight "context" (i.e., dict)
        context = template_or_context.context_data
        self.assertTrue(var_name in context,
                msg="`%s` not in provided context" % var_name)
        self.assertEqual(context[var_name], other)
