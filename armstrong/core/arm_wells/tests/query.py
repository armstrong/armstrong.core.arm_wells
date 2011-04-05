from django.core.paginator import Paginator
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
        self.assertEqual(len(self.queryset_backed_well),
                self.queryset_backed_well.count())

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

    def test_gathers_all_nodes_with_N_plus_1_queries(self):
        with self.assertNumQueries(self.number_in_well + 1):
            node_models = self.queryset_backed_well[0:self.number_in_well]

    def test_gathers_nodes_plus_backfill_in_N_plus_2_queries(self):
        with self.assertNumQueries(self.number_in_well + 2):
            node_models = self.queryset_backed_well \
                    [0:self.number_in_well + self.number_of_extra_stories]

    def test_works_with_simple_pagination(self):
        paged = Paginator(self.queryset_backed_well, self.number_in_well)
        page_one = paged.page(1)
        node_models = [a.content_object for a in self.well.nodes.all()]
        for model in node_models:
            self.assertTrue(model in page_one.object_list)

        paged = Paginator(self.queryset_backed_well, \
                self.number_in_well + self.number_of_extra_stories)
        page_one = paged.page(1)
        for model in node_models:
            self.assertTrue(model in page_one.object_list)
        for story in self.extra_stories:
            self.assertTrue(story in page_one.object_list)

    def test_pagination_works_when_split_across_well_and_queryset(self):
        paged = Paginator(self.queryset_backed_well, self.number_in_well + 1)
        page_one = paged.page(1)
        node_models = [a.content_object for a in self.well.nodes.all()]
        self.assertFalse(page_one.object_list[-1] in node_models)
