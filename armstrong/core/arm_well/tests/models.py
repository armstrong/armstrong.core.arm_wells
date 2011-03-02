import random

from ._utils import generate_random_story
from ._utils import TestCase

from ..models import Node
from ..models import Well


class WellTestCase(TestCase):
    def test_has_many_nodes_as_are_added(self):
        well = Well.objects.create(title="foo")
        self.assertEqual(0, well.nodes.count(), msg="Sanity check")

        r = random.randint(1, 10)
        for i in range(r):
            Node.objects.create(well=well,
                                content_object=generate_random_story())

        self.assertEqual(r, well.nodes.count())

