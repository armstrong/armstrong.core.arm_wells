import random

from .arm_wells_support.models import Story
from ._utils import (add_n_random_stories_to_well, generate_random_story,
        generate_random_well, TestCase)


class MergedNodesAndQuerySetTest(TestCase):
    def setUp(self):
        super(MergedNodesAndQuerySetTest, self).setUp()
        self.well = generate_random_well()
        self.number_in_well = random.randint(1, 5)
        add_n_random_stories_to_well(self.number_in_well, self.well)

        self.number_of_extra_stories = random.randint(1, 5)
        self.extra_stories = []
        for i in range(self.number_of_extra_stories):
            self.extra_stories.append(generate_random_story())

    def test_node_models_are_first(self):
        queryset_backed_well = self.well.merge_with(Story.objects.all())

        node_models = [a.content_object for a in self.well.nodes.all()]
        for obj in queryset_backed_well[0:self.number_in_well]:
            self.assertTrue(obj in node_models)

    def test_fills_in_with_queryset_after_nodes_are_exhausted(self):
        node_models = [a.content_object for a in self.well.nodes.all()]

        queryset_backed_well = self.well.merge_with(Story.objects.all())
        back_filled_models = queryset_backed_well[self.number_in_well+1:]
        for back_filled in back_filled_models:
            self.assertTrue(isinstance(back_filled, Story), msg="sanity check")
            self.assertFalse(back_filled in node_models)

    def test_gathers_all_nodes_with_N_plus_1_queries(self):
        queryset_backed_well = self.well.merge_with(Story.objects.all())
        with self.assertNumQueries(self.number_in_well + 1):
            node_models = queryset_backed_well[0:self.number_in_well]
