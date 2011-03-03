import random

from django.test import TestCase

from .models import Story


class StoryTestCase(TestCase):
    def test_uses_title_when_converted_to_string(self):
        title = "Some Random Title %d" % random.randint(100, 200)
        story = Story(title=title)

        self.assertEqual(title, str(story))
