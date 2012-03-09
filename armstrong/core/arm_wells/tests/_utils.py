import random

from armstrong.dev.tests.utils.base import ArmstrongTestCase
from .arm_wells_support.models import Story, StoryChild, Image
from ..models import WellType, Well, Node


class TestCase(ArmstrongTestCase):
    pass


def generate_random_image():
    title = "Random Image %d" % random.randint(1000000, 2000000)
    url = "http://example.com/%d" % random.randint(1000000, 2000000)
    return Image.objects.create(title=title, url=url)


def generate_random_story_child():
    title = "Random title %d" % random.randint(1000000, 2000000)
    body = "Some random text %d" % random.randint(1000000, 2000000)
    comment = "Some random comment %d" % random.randint(1000000, 2000000)
    return StoryChild.objects.create(title=title, body=body, comment=comment)


def generate_random_story():
    title = "Random title %d" % random.randint(1000000, 2000000)
    body = "Some random text %d" % random.randint(1000000, 2000000)
    return Story.objects.create(title=title, body=body)


def generate_random_well():
    return Well.objects.create(type=generate_random_welltype())


def add_n_random_objects_to_well(n, well, object_generator):
    for i in range(n):
        node = Node.objects.create(well=well,
                content_object=object_generator())
        well.nodes.add(node)


def add_n_random_images_to_well(n, well):
    add_n_random_objects_to_well(n, well, generate_random_image)


def add_n_random_stories_to_well(n, well):
    add_n_random_objects_to_well(n, well, generate_random_story)


def generate_random_welltype():
    r = random.randint(1000000, 2000000)
    title = "Random Well %d" % r
    slug = "random-well-%d" % r
    return WellType.objects.create(title=title, slug=slug)
