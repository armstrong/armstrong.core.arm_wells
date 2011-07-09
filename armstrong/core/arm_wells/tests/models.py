import datetime
import fudge
import random

from .arm_wells_support.models import Story
from ._utils import add_n_random_stories_to_well
from ._utils import generate_random_story
from ._utils import generate_random_well
from ._utils import generate_random_welltype
from ._utils import TestCase

from ..models import Node
from ..models import Well
from ..models import WellType
from .. import models


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

    def test_render_loads_template_for_node(self):
        title = "some-random-well-%d" % random.randint(100, 200)
        type = WellType.objects.create(title=title, slug=title)
        well = Well.objects.create(type=type)
        story = generate_random_story()
        node = Node.objects.create(well=well, content_object=story)

        expected_path = "wells/%s/%s/%s.html" % (story._meta.app_label,
                story._meta.object_name.lower(), title)
        random_return = str(random.randint(1000, 2000))

        render_to_string = fudge.Fake(callable=True)
        context = {"well": well, "object": story, "parent": None}
        render_to_string.with_args(expected_path, dictionary=context) \
                .returns(random_return)

        with fudge.patched_context(models, "render_to_string",
                render_to_string):
            result = well.render()

            self.assertEqual(result, random_return,
                    msg="Returns what was expected")

    def test_passes_RequestContext_to_template_if_provided_to_render(self):
        title = "some-random-well-%d" % random.randint(100, 200)
        type = WellType.objects.create(title=title, slug=title)
        well = Well.objects.create(type=type)
        story = generate_random_story()
        node = Node.objects.create(well=well, content_object=story)

        expected_path = "wells/%s/%s/%s.html" % (story._meta.app_label,
                story._meta.object_name.lower(), title)
        random_return = str(random.randint(1000, 2000))

        # doesn't really matter what it is, just that its the result of
        # RequestContext being invoked
        mock_context_instance = random.randint(1000, 2000)
        request = fudge.Fake()
        RequestContext = fudge.Fake(callable=True)
        RequestContext.with_args(request).returns(mock_context_instance)

        render_to_string = fudge.Fake(callable=True)
        context = {"well": well, "object": story, "parent": None}
        render_to_string.with_args(expected_path, dictionary=context,
                context_instance=mock_context_instance).returns(random_return)

        with fudge.patched_context(models, "render_to_string",
                render_to_string):
            with fudge.patched_context(models, "RequestContext",
                    RequestContext):
                result = well.render(request)

                self.assertEqual(result, random_return,
                        msg="Returns what was expected")

    def test_render_loads_template_for_node_without_mocks(self):
        type = WellType.objects.create(title="Foobar", slug="foobar")
        well = Well.objects.create(type=type)
        story = generate_random_story()
        node = Node.objects.create(well=well, content_object=story)

        result = well.render().strip()
        expected = "\n".join(["Story Template",
            "Story: %s" % story.title,
            "Well: %s" % type.title,
            ])

        self.assertEqual(expected, result)

    def test_render_loads_template_with_request_for_nodes_without_mocks(self):
        type = WellType.objects.create(title="Foobar", slug="foobar")
        well = Well.objects.create(type=type)
        story = generate_random_story()
        node = Node.objects.create(well=well, content_object=story)

        result = well.render([123]).strip()
        expected = "\n".join(["Story Template",
            "Story: %s" % story.title,
            "Well: %s" % type.title,
            "Got Request!",
            ])

        self.assertEqual(expected, result)

    def test_calls_render_on_inner_well(self):
        """
        This fails if render() is not invoked because there is no "outer.html"
        template file.
        """
        outer_type = WellType.objects.create(title="outer", slug="outer")
        outer_well = Well.objects.create(type=outer_type)
        inner_type = WellType.objects.create(title="foobar", slug="foobar")
        inner_well = Well.objects.create(type=inner_type)
        well_node = Node.objects.create(well=outer_well, content_object=inner_well)
        story = generate_random_story()
        story_node = Node.objects.create(well=inner_well, content_object=story)

        result = outer_well.render().strip()
        expected = "\n".join(["Story Template",
            "Parent Well: %s" % outer_type.title,
            "Story: %s" % story.title,
            "Well: %s" % inner_type.title,
            ])

        self.assertEqual(expected, result)

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
        for story in well:
            i = i + 1
        self.assertEqual(i, number_in_well)

    def test_well_is_iterable_with_merged_queryset(self):
        number_of_stories = random.randint(1, 5)
        for i in range(number_of_stories):
            generate_random_story()

        well = generate_random_well()
        number_in_well = random.randint(1, 5)
        add_n_random_stories_to_well(number_in_well, well)
        i = 0
        for story in well:
            i = i + 1
        self.assertEqual(i, number_in_well)

    def test_well_supports_indexing(self):
        well = generate_random_well()
        number_in_well = random.randint(1, 5)
        add_n_random_stories_to_well(number_in_well, well)
        i = 0
        for node in well.nodes.all():
            self.assertEqual(node.content_object, well[i].content_object)
            i = i + 1

    def test_well_supports_indexing_with_merged_queryset(self):
        number_of_stories = random.randint(1, 5)
        for i in range(number_of_stories):
            generate_random_story()

        well = generate_random_well()
        well
        number_in_well = random.randint(1, 5)
        add_n_random_stories_to_well(number_in_well, well)
        i = 0
        for node in well.nodes.all():
            self.assertEqual(node.content_object, well[i].content_object)
            i = i + 1


class NodeTestCase(TestCase):
    def test_string_representation(self):
        story = generate_random_story()
        well = generate_random_well()
        order = random.randint(100, 200)
        node = Node.objects.create(well=well, content_object=story,
                                   order=order)

        expected = "%s (%d): %s" % (well.title, order, story.title)
        self.assertEqual(expected, str(node))
