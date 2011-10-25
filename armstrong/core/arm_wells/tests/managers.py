import datetime

from ._utils import TestCase

from ..models import Well
from ..models import WellType


class WellManagerTestCase(TestCase):
    def test_get_current_returns_most_current_well(self):
        now = datetime.datetime.now()
        future_time = now + datetime.timedelta(minutes=10)
        past_time = now - datetime.timedelta(minutes=10)

        type = WellType.objects.create(title="well-title", slug="well-title")
        future = Well.objects.create(type=type, pub_date=future_time)
        past = Well.objects.create(type=type, pub_date=past_time)
        present = Well.objects.create(type=type)

        self.assertEqual(present, Well.objects.get_current("well-title"))

    def test_get_current_does_not_return_expired_well(self):
        now = datetime.datetime.now()
        ten_minutes_ago = now - datetime.timedelta(minutes=10)
        twenty_minutes_ago = now - datetime.timedelta(minutes=20)

        type = WellType.objects.create(title="well-title", slug="well-title")
        expired = Well.objects.create(type=type,
                                      pub_date=twenty_minutes_ago,
                                      expires=ten_minutes_ago)
        expected = Well.objects.create(type=type,
                                       pub_date=twenty_minutes_ago)

        self.assertEqual(expected, Well.objects.get_current("well-title"))

    def test_get_current_should_raise_DoesNotExist_on_no_valid(self):
        now = datetime.datetime.now()
        ten_minutes_ago = now - datetime.timedelta(minutes=10)
        twenty_minutes_ago = now - datetime.timedelta(minutes=20)

        type = WellType.objects.create(title="well-title", slug="well-title")
        expired = Well.objects.create(type=type,
                                      pub_date=twenty_minutes_ago,
                                      expires=ten_minutes_ago)

        self.assertRaises(Well.DoesNotExist, Well.objects.get_current,
                          "well-title")

    def test_get_current_should_only_return_active(self):
        type = WellType.objects.create(title="well-title", slug="well-title")
        inactive = Well.objects.create(type=type, active=False)

        self.assertRaises(Well.DoesNotExist, Well.objects.get_current,
                          "well-title")
