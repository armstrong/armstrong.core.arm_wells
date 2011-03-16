import datetime

from ._utils import TestCase

from ..models import Well


class WellManagerTestCase(TestCase):
    def test_get_current_returns_most_current_well(self):
        now = datetime.datetime.now()
        future_time = now + datetime.timedelta(minutes=10)
        past_time = now - datetime.timedelta(minutes=10)

        future = Well.objects.create(title="well-title", pub_date=future_time)
        present = Well.objects.create(title="well-title")
        past = Well.objects.create(title="well-title", pub_date=past_time)

        self.assertEqual(present, Well.objects.get_current("well-title"))
