from django.core.paginator import Paginator
import random

from .arm_wells_support.models import *
from ._utils import (add_n_random_stories_to_well, add_n_random_images_to_well,
        generate_random_image, generate_random_story, generate_random_well,
        TestCase)

from ..querysets import (GenericForeignKeyQuerySet, MergeQuerySet,
        FilterException)
from ..models import Node


class GenericForeignKeyQuerySetTestCase(TestCase):
    def setUp(self):
        super(GenericForeignKeyQuerySetTestCase, self).setUp()

        self.well = generate_random_well()
        self.number_in_well = random.randint(1, 5)
        add_n_random_stories_to_well(self.number_in_well, self.well)

        self.number_of_extra_stories = random.randint(1, 5)
        self.extra_stories = []
        for i in range(self.number_of_extra_stories):
            self.extra_stories.append(generate_random_story())

    def test_raises_NotImplementedError_on_exclude(self):
        with self.assertRaises(NotImplementedError):
            gfk_qs = GenericForeignKeyQuerySet(self.well.nodes.all()\
                    .select_related())
            gfk_qs.exclude()

    def test_raises_NotImplementedError_on_misc_functions(self):
        funcs_to_test = ['aggregate', 'get', 'create', 'get_or_create',
                'latest', 'in_bulk', 'update', 'exists', 'values',
                'values_list', 'dates', 'none', 'complex_filter',
                'select_related', 'dup_select_related', 'annotate', 'order_by',
                'distinct', 'extra', 'reverse', 'defer', 'only', 'using',
                'ordered', ]
        gfk_qs = GenericForeignKeyQuerySet(self.well.nodes.all()\
                .select_related())
        for func in funcs_to_test:
            with self.assertRaises(NotImplementedError):
                getattr(gfk_qs, func)()

    def test_raises_AttributeError_on_unknown_attribute(self):
        """Necessary because of the NotImplementedError code"""
        gfk_qs = GenericForeignKeyQuerySet(self.well.nodes.all()\
                .select_related())
        with self.assertRaises(AttributeError):
            getattr(gfk_qs, "unknown_and_unknowable")


    def test_gathers_all_nodes_of_one_type_with_two_queries(self):
        gfk_qs = GenericForeignKeyQuerySet(self.well.nodes.all()\
                .select_related())
        with self.assertNumQueries(2):
            node_models = gfk_qs[0:self.number_in_well]

    def test_gathers_all_nodes_of_two_types_with_three_queries(self):
        add_n_random_images_to_well(self.number_in_well, self.well)
        gfk_qs = GenericForeignKeyQuerySet(self.well.nodes.all()\
                .select_related())
        with self.assertNumQueries(3):
            node_models = gfk_qs[0:self.number_in_well * 2]

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
            models = queryset[0:3]
        self.assertEqual(models[0], content[0])
        self.assertEqual(models[1], content[1])
        self.assertEqual(models[2], content[2])

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

    def test_non_standard_node(self):
        num_nodes = random.randint(3,5)
        for i in range(num_nodes):
            OddNode.objects.create(baz=generate_random_story())
        gfk_qs = GenericForeignKeyQuerySet(
                    OddNode.objects.all().select_related(),
                    gfk='baz'
                )
        with self.assertNumQueries(2):
            for obj in gfk_qs:
                self.assertEqual(obj.__class__, Story)

    def test_non_standard_node_failure(self):
        num_nodes = random.randint(3,5)
        for i in range(num_nodes):
            OddNode.objects.create(baz=generate_random_story())
        with self.assertRaises(ValueError):
            gfk_qs = GenericForeignKeyQuerySet(
                        OddNode.objects.all().select_related(),
                        gfk='bad_field_name'
                    )

    def test_works_with_duplicate_nodes(self):
        well = generate_random_well()
        story = generate_random_story()
        for i in range(3):
            Node.objects.create(content_object=story, order=i, well=well)
        for i in range(3):
            self.assertEqual(well.items[i], story)

    def test_count(self):
        well = generate_random_well()
        content = [generate_random_story(), generate_random_image(),
                generate_random_story()]
        for i, obj in enumerate(content):
            Node.objects.create(content_object=obj, order=i, well=well)

        queryset = well.items
        self.assertEqual(3, queryset.count())

    def test_empty_filter(self):
        well = generate_random_well()
        content = [generate_random_story(), generate_random_image(),
                generate_random_story()]
        for i, obj in enumerate(content):
            Node.objects.create(content_object=obj, order=i, well=well)

        queryset = well.items
        self.assertEqual(3, len(queryset.filter()))

    def test_non_empty_filter(self):
        well = generate_random_well()
        content = [generate_random_story(), generate_random_image(),
                generate_random_story()]
        for i, obj in enumerate(content):
            Node.objects.create(content_object=obj, order=i, well=well)

        queryset = well.items
        with self.assertRaises(FilterException):
            self.assertEqual(3, len(queryset.filter(title__in=['foo','bar'])))

class MergeQuerySetTestCase(TestCase):
    def setUp(self):
        super(MergeQuerySetTestCase, self).setUp()

        self.number_in_a = random.randint(1, 5)
        for i in range(self.number_in_a):
            generate_random_story()
        self.qs_a = Story.objects.all()

        self.number_in_b = random.randint(1, 5)
        for i in range(self.number_in_b):
            generate_random_image()
        self.qs_b = Image.objects.all()

    def test_raises_NotImplementedError_on_exclude(self):
        with self.assertRaises(NotImplementedError):
            merge_qs = MergeQuerySet(self.qs_a, self.qs_b)
            merge_qs.exclude()

    def test_raises_NotImplementedError_on_misc_functions(self):
        funcs_to_test = ['aggregate', 'get', 'create', 'get_or_create',
                'latest', 'in_bulk', 'update', 'exists', 'values',
                'values_list', 'dates', 'none', 'complex_filter',
                'select_related', 'dup_select_related', 'annotate', 'order_by',
                'distinct', 'extra', 'reverse', 'defer', 'only', 'using',
                'ordered', ]
        merge_qs = MergeQuerySet(self.qs_a, self.qs_b)
        for func in funcs_to_test:
            with self.assertRaises(NotImplementedError):
                getattr(merge_qs, func)()

    def test_raises_AttributeError_on_unknown_attribute(self):
        """Necessary because of the NotImplementedError code"""
        merge_qs = MergeQuerySet(self.qs_a, self.qs_b)
        with self.assertRaises(AttributeError):
            getattr(merge_qs, "unknown_and_unknowable")

    def test_count_returns_total_of_combined_queryset_and_queryset2(self):
        merge_qs = MergeQuerySet(self.qs_a.all(), self.qs_b.all())
        expected = self.number_in_b + self.number_in_a
        self.assertEqual(expected, merge_qs.count())

    def test_count_and_len_are_identical_with_small_queryset(self):
        # This might not always be the case.  __len__() and count() are
        # semantically different in QuerySet.
        merge_qs = MergeQuerySet(self.qs_a.all(), self.qs_b.all())
        self.assertEqual(merge_qs.count(),
                len(merge_qs))

    def test_count_does_not_call_length_on_queryset2(self):
        merge_qs = MergeQuerySet(self.qs_a.all(), self.qs_b.all())
        merge_qs.count()
        with self.assertNumQueries(1):
            len(merge_qs)

    def test_story_models_are_first(self):
        merge_qs = MergeQuerySet(self.qs_a.all(), self.qs_b.all())
        qs_a_copy = self.qs_a.all()
        for obj in merge_qs[0:self.number_in_a]:
            self.assertTrue(obj in qs_a_copy)

    def test_fills_in_with_queryset_after_nodes_are_exhausted(self):
        merge_qs = MergeQuerySet(self.qs_a.all(), self.qs_b.all())
        qs_a_copy = self.qs_a.all()

        start = self.number_in_a + 1
        back_filled_models = merge_qs[start:]
        for back_filled in back_filled_models:
            self.assertTrue(isinstance(back_filled, Image), msg="sanity check")
            self.assertFalse(back_filled in qs_a_copy)

    def test_deduplicates_across_inheritance(self):
        merge_qs = MergeQuerySet(self.qs_a.all(), Content.objects.all())
        objs = list(merge_qs)
        for i, obj in enumerate(objs):
            self.assertFalse(obj in merge_qs[i+1:])

    def test_empty_filter(self):
        merge_qs = MergeQuerySet(self.qs_a.all(), self.qs_b.all())
        filtered = merge_qs.filter()
        self.assertEqual(len(filtered), len(self.qs_a) + len(self.qs_b))

    def test_non_empty_filter(self):
        merge_qs = MergeQuerySet(self.qs_a.all(), self.qs_b.all())
        filtered = merge_qs.filter(id__lte=2)
        self.assertEqual(len(filtered), 2)

    def test_is_slicable(self):
        merge_qs = MergeQuerySet(self.qs_a.all(), self.qs_b.all())
        sliced = merge_qs[0:self.number_in_a + 2]
        try:
            obj = sliced[1]
        except TypeError:
            self.fail("Threw a TypeError")
