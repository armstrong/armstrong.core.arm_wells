from django.core.paginator import Paginator
import random

from .arm_wells_support.models import Image, Story
from ._utils import (add_n_random_stories_to_well, add_n_random_images_to_well,
        generate_random_image, generate_random_story, generate_random_well,
        TestCase)

from ..models import Node


class SimpleMergedNodesAndQuerySetTests(TestCase):
    """Tests that don't require all of the setup and such"""

    def test_merge_when_sliced_across_the_well_content_with_slice_object(self):
        well = generate_random_well()
        stories = [generate_random_story() for i in range(2)]
        add_n_random_stories_to_well(2, well)

        queryset = well.merge_with(Story.objects.all())
        sliced = [a for a in queryset[slice(1,3)]]
        self.assertEqual(2, len(sliced))

    def test_merges_correctly_when_sliced_across_the_well_content(self):
        well = generate_random_well()
        stories = [generate_random_story() for i in range(2)]
        add_n_random_stories_to_well(2, well)

        queryset = well.merge_with(Story.objects.all())
        sliced = [a for a in queryset[1:3]]
        self.assertEqual(2, len(sliced))


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
        self.queryset_backed_well = self.well.merge_with(Story.objects.all())

    def test_works_with_simple_pagination(self):
        paged = Paginator(self.queryset_backed_well, self.number_in_well)
        page_one = paged.page(1)
        node_models = [a.content_object for a in self.well.nodes.all()]
        page_one_objects = [n for n in page_one.object_list]
        for model in node_models:
            self.assertTrue(model in page_one_objects)

    def test_works_when_all_results_are_on_one_page(self):
        paged = Paginator(self.queryset_backed_well, \
                self.number_in_well + self.number_of_extra_stories)
        page_one = paged.page(1)
        node_models = [a.content_object for a in self.well.nodes.all()]
        object_list = [a for a in page_one.object_list]
        for model in node_models:
            self.assertTrue(model in object_list)
        for story in self.extra_stories:
            self.assertTrue(story in object_list)

    def test_pagination_works_when_split_across_well_and_queryset(self):
        paged = Paginator(self.queryset_backed_well, self.number_in_well + 1)
        page_one = paged.page(1)
        node_models = [a.content_object for a in self.well.nodes.all()]
        object_list = [a for a in page_one.object_list]
        self.assertFalse(object_list[-1] in node_models)
