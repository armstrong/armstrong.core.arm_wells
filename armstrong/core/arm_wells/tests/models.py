import datetime
import fudge
from fudge.inspector import arg
import random

from .arm_wells_support.models import Story
from ._utils import add_n_random_stories_to_well
from ._utils import generate_random_story
from ._utils import generate_random_image
from ._utils import generate_random_story_child
from ._utils import generate_random_well
from ._utils import generate_random_welltype
from ._utils import TestCase

from ..models import Node
from ..models import Well
from ..models import WellType
from .. import models

from django.template.context import Context


class WellTestCase(TestCase):
    def test_has_as_many_nodes_as_are_added(self):
        well = generate_random_well()
        self.assertEqual(0, well.nodes.count(), msg="Sanity check")

        r = random.randint(1, 10)
        for i in range(r):
            Node.objects.create(well=well,
                                content_object=generate_random_story())

        self.assertEqual(r, well.nodes.count())

    def test_nodes_are_sorted_by_order(self):
        well = generate_random_well()
        second = Node.objects.create(well=well,
                                     content_object=generate_random_story(),
                                     order=100)
        first = Node.objects.create(well=well,
                                    content_object=generate_random_story(),
                                    order=10)

        self.assertEqual(first, well.nodes.all()[0])
        self.assertEqual(second, well.nodes.all()[1])

    def test_outputs_title_and_pub_date_when_cast_to_string(self):
        title = "some-random-title-%d" % random.randint(10, 100)
        date = datetime.datetime.now()

        type = WellType.objects.create(title=title, slug=title)
        well = Well.objects.create(type=type, pub_date=date)
        self.assertEqual("%s (%s - Never)" % (title, date), str(well))

    def test_outputs_expires_if_present(self):
        title = "some-random-title-%d" % random.randint(10, 100)
        date = datetime.datetime.now()

        type = WellType.objects.create(title=title, slug=title)
        well = Well.objects.create(type=type, pub_date=date, expires=date)
        self.assertEqual("%s (%s - %s)" % (title, date, date), str(well))

    def test_combines_a_well_with_another_queryset(self):
        number_of_stories = random.randint(1, 5)
        for i in range(number_of_stories):
            generate_random_story()

        well = generate_random_well()
        number_in_well = random.randint(1, 5)
        add_n_random_stories_to_well(number_in_well, well)

        queryset_backed_well = well.merge_with(Story.objects.all())
        self.assertEqual(number_in_well + number_of_stories,
                len(queryset_backed_well))

    def test_title_is_the_same_as_welltype_title(self):
        well_type = generate_random_welltype()
        well = Well.objects.create(type=well_type)
        self.assertEqual(well_type.title, well.title)

    def test_well_is_iterable(self):
        well = generate_random_well()
        number_in_well = random.randint(1, 5)
        add_n_random_stories_to_well(number_in_well, well)
        i = 0
        for story in well.items:
            i = i + 1
        self.assertEqual(i, number_in_well)

    def test_well_is_iterable_with_merged_queryset(self):
        number_of_stories = random.randint(1, 5)
        for i in range(number_of_stories):
            generate_random_story()

        well = generate_random_well()
        number_in_well = random.randint(1, 5)
        add_n_random_stories_to_well(number_in_well, well)

        well.merge_with(Story.objects.all())
        i = 0
        for story in well.items:
            i = i + 1
        self.assertEqual(i, number_in_well + number_of_stories)

    def test_well_supports_indexing(self):
        well = generate_random_well()
        number_in_well = random.randint(1, 5)
        add_n_random_stories_to_well(number_in_well, well)
        i = 0
        for node in well.nodes.all():
            self.assertEqual(node.content_object, well.items[i])
            i = i + 1
        self.assertRaises(IndexError, lambda:well.items[i])

    def test_well_supports_indexing_with_merged_queryset(self):
        number_of_stories = random.randint(1, 5)
        for i in range(number_of_stories):
            generate_random_story()

        well = generate_random_well()
        number_in_well = random.randint(1, 5)
        add_n_random_stories_to_well(number_in_well, well)
        qs = Story.objects.all()
        well.merge_with(qs)
        i = 0
        # querysets are filtered to prevent duplicate objects, so we need to
        # keep track of the objects we've already seen
        used_objects = {}
        for node in well.nodes.all():
            self.assertEqual(node.content_object, well.items[i])
            used_objects[node.content_object.id] = 1
            i = i + 1
        for story in qs:
            if story.id in used_objects:
                continue
            self.assertEqual(story, well.items[i])
            i = i + 1
        self.assertRaises(IndexError, lambda:well.items[i])


class NodeTestCase(TestCase):
    def test_string_representation(self):
        story = generate_random_story()
        well = generate_random_well()
        order = random.randint(100, 200)
        node = Node.objects.create(well=well, content_object=story,
                                   order=order)

        expected = "%s (%d): %s" % (well.title, order, story.title)
        self.assertEqual(expected, str(node))
