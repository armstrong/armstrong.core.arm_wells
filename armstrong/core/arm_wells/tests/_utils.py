import random

from django.test import TestCase

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
