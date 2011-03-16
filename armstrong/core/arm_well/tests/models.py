import random

from ._utils import generate_random_story
from ._utils import generate_random_well
from ._utils import TestCase

from ..models import Node
from ..models import Well


class WellTestCase(TestCase):
    def test_has_as_many_nodes_as_are_added(self):
        well = Well.objects.create(title="foo")
        self.assertEqual(0, well.nodes.count(), msg="Sanity check")

        r = random.randint(1, 10)
        for i in range(r):
            Node.objects.create(well=well,
                                content_object=generate_random_story())

        self.assertEqual(r, well.nodes.count())

    def test_nodes_are_sorted_by_order(self):
        well = Well.objects.create(title="foo")
        second = Node.objects.create(well=well,
                                     content_object=generate_random_story(),
                                     order=100)
        first = Node.objects.create(well=well,
                                    content_object=generate_random_story(),
                                    order=10)

        self.assertEqual(first, well.nodes.all()[0])
        self.assertEqual(second, well.nodes.all()[1])


class NodeTestCase(TestCase):
    def test_string_representation(self):
        story = generate_random_story()
        well = generate_random_well()
        order = random.randint(100, 200)
        node = Node.objects.create(well=well, content_object=story,
                                   order=order)

        expected = "%s (%d): %s" % (well.title, order, story.title)
        self.assertEqual(expected, str(node))
