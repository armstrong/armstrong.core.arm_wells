from django.test import TestCase

from .arm_well_support.models import Story

def generate_random_story():
    return Story.objects.create(title="foobar", body="Some random text")
