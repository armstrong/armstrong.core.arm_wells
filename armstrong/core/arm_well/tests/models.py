import datetime
import fudge
import random

from ._utils import generate_random_story
from ._utils import generate_random_well
from ._utils import TestCase

from ..models import Node
from ..models import Well
from .. import models


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

    def test_outputs_title_and_pub_date_when_cast_to_string(self):
        title = "some-random-title-%d" % random.randint(10, 100)
        date = datetime.datetime.now()

        well = Well.objects.create(title=title, pub_date=date)
        self.assertEqual("%s (%s - Never)" % (title, date), str(well))

    def test_outputs_expires_if_present(self):
        title = "some-random-title-%d" % random.randint(10, 100)
        date = datetime.datetime.now()

        well = Well.objects.create(title=title, pub_date=date, expires=date)
        self.assertEqual("%s (%s - %s)" % (title, date, date), str(well))

    def test_render_loads_template_for_node(self):
        title = "some-random-well-%d" % random.randint(100, 200)
        well = Well.objects.create(title=title)
        story = generate_random_story()
        node = Node.objects.create(well=well, content_object=story)

        expected_path = "wells/%s/%s/%s.html" % (story._meta.app_label,
                story._meta.object_name.lower(), title)
        random_return = str(random.randint(1000, 2000))

        render_to_string = fudge.Fake(callable=True)
        render_to_string.with_args(expected_path).returns(random_return)

        with fudge.patched_context(models, "render_to_string",
                render_to_string):
            result = well.render()

            self.assertEqual(result, random_return,
                    msg="Returns what was expected")

    def test_passes_RequestContext_to_template_if_provided_to_render(self):
        title = "some-random-well-%d" % random.randint(100, 200)
        well = Well.objects.create(title=title)
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
        render_to_string.with_args(expected_path,
                context_instance=mock_context_instance).returns(random_return)

        with fudge.patched_context(models, "render_to_string",
                render_to_string):
            with fudge.patched_context(models, "RequestContext",
                    RequestContext):
                result = well.render(request)

                self.assertEqual(result, random_return,
                        msg="Returns what was expected")


class NodeTestCase(TestCase):
    def test_string_representation(self):
        story = generate_random_story()
        well = generate_random_well()
        order = random.randint(100, 200)
        node = Node.objects.create(well=well, content_object=story,
                                   order=order)

        expected = "%s (%d): %s" % (well.title, order, story.title)
        self.assertEqual(expected, str(node))
