import random

from django.test import TestCase

from .arm_well_support.models import Story
from ..models import Well


def generate_random_story():
    title = "Random title %d" % random.randint(100, 200)
    body = "Some random text %d" % random.randint(100, 200)
    return Story.objects.create(title=title, body=body)


def generate_random_well():
    title = "Random Well %d" % random.randint(100, 200)
    return Well.objects.create(title=title)
