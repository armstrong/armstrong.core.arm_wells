from django.core.paginator import Paginator
import random

from .arm_wells_support.models import Image, Story
from ._utils import (add_n_random_stories_to_well, add_n_random_images_to_well,
        generate_random_image, generate_random_story, generate_random_well,
        TestCase)

from ..models import Node


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

    def test_raises_NotImplementedError_on_filter(self):
        with self.assertRaises(NotImplementedError):
            self.queryset_backed_well.filter()

    def test_raises_NotImplementedError_on_exclude(self):
        with self.assertRaises(NotImplementedError):
            self.queryset_backed_well.exclude()

    def test_raises_NotImplementedError_on_misc_functions(self):
        funcs_to_test = ['aggregate', 'get', 'create', 'get_or_create',
                'latest', 'in_bulk', 'delete', 'update', 'exists', 'values',
                'values_list', 'dates', 'none', 'complex_filter',
                'select_related', 'dup_select_related', 'annotate', 'order_by',
                'distinct', 'extra', 'reverse', 'defer', 'only', 'using',
                'ordered', ]
        for func in funcs_to_test:
            with self.assertRaises(NotImplementedError):
                getattr(self.queryset_backed_well, func)()

    def test_raises_AttributeError_on_unknown_attribute(self):
        """Necessary because of the NotImplementedError code"""
        with self.assertRaises(AttributeError):
            getattr(self.queryset_backed_well, "unknown_and_unknowable")

    def test_count_returns_total_of_combined_queryset_and_well_nodes(self):
        expected = self.number_of_extra_stories + self.number_in_well
        self.assertEqual(expected, self.queryset_backed_well.count())

    def test_count_and_len_are_identical_with_small_queryset(self):
        # This might not always be the case.  __len__() and count() are
        # semantically different in QuerySet.
        try:
            self.assertEqual(len(self.queryset_backed_well), len(self.queryset_backed_well))
        except AssertionError, e:
            import ipdb;ipdb.set_trace()
            raise e

    def test_node_models_are_first(self):
        node_models = [a.content_object for a in self.well.nodes.all()]
        for obj in self.queryset_backed_well[0:self.number_in_well]:
            self.assertTrue(obj in node_models)

    def test_fills_in_with_queryset_after_nodes_are_exhausted(self):
        node_models = [a.content_object for a in self.well.nodes.all()]

        start = self.number_in_well + 1
        back_filled_models = self.queryset_backed_well[start:]
        for back_filled in back_filled_models:
            self.assertTrue(isinstance(back_filled, Story), msg="sanity check")
            self.assertFalse(back_filled in node_models)

    def test_gathers_all_nodes_of_one_type_with_two_queries(self):
        with self.assertNumQueries(2):
            node_models = self.queryset_backed_well[0:self.number_in_well]

    def test_gathers_all_nodes_of_two_types_with_three_queries(self):
        add_n_random_images_to_well(self.number_in_well, self.well)
        with self.assertNumQueries(3):
            node_models = self.queryset_backed_well[0:self.number_in_well * 2]

        number_of_images, number_of_stories = 0, 0
        for node_model in node_models:
            if node_model.__class__.__name__ == "Story":
                number_of_stories += 1
            if node_model.__class__.__name__ == "Image":
                number_of_images += 1
        self.assertEqual(self.number_in_well, number_of_stories)
        self.assertEqual(self.number_in_well, number_of_images)


    def test_perserves_order_across_types(self):
        well = generate_random_well()
        content = [generate_random_story(), generate_random_image(),
                generate_random_story()]

        Node.objects.create(content_object=content[0], order=0, well=well)
        Node.objects.create(content_object=content[1], order=1, well=well)
        Node.objects.create(content_object=content[2], order=2, well=well)

        queryset = well.merge_with(Story.objects.all())
        with self.assertNumQueries(3, msg="sanity check"):
            node_models = queryset[0:3]
        self.assertEqual(node_models[0], content[0])
        self.assertEqual(node_models[1], content[1])
        self.assertEqual(node_models[2], content[2])

    def test_does_not_ignore_same_ids_in_different_types(self):
        well = generate_random_well()
        story = generate_random_story()
        story.pk = 1
        story.save()

        image = generate_random_image()
        image.pk = 1
        image.save()

        Node.objects.create(content_object=story, well=well)
        queryset = well.merge_with(Image.objects.all())
        self.assertEqual(2, len(queryset))

    def test_gathers_nodes_of_one_type_plus_backfill_in_three_queries_total(self):
        with self.assertNumQueries(2,
                msg="only takes two queries to get the slice"):
            end = self.number_in_well + self.number_of_extra_stories
            node_models = self.queryset_backed_well[0:end]

        with self.assertNumQueries(1,
                msg="queryset is run only when actually iterated over"):
            [a for a in node_models]

    def test_works_with_simple_pagination(self):
        paged = Paginator(self.queryset_backed_well, self.number_in_well)
        page_one = paged.page(1)
        node_models = [a.content_object for a in self.well.nodes.all()]
        for model in node_models:
            self.assertTrue(model in page_one.object_list)

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
