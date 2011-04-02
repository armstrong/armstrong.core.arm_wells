import random

from .arm_wells_support.models import Story
from ._utils import (add_n_random_stories_to_well, generate_random_story,
        generate_random_well, TestCase)


class MergedNodesAndQuerySetTest(TestCase):
    def test_node_models_are_first(self):
        number_of_stories = random.randint(1, 5)
        for i in range(number_of_stories):
            generate_random_story()

        well = generate_random_well()
        number_in_well = random.randint(1, 5)
        add_n_random_stories_to_well(number_in_well, well)

        queryset_backed_well = well.merge_with(Story.objects.all())
        node_models = [a.content_object for a in well.nodes.all()]
        for obj in queryset_backed_well[0:number_in_well]:
            self.assertTrue(obj in node_models)
