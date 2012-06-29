import datetime

from ._utils import TestCase

from ..models import Well
from ..models import WellType


class WellManagerTestCase(TestCase):
    def test_get_current_returns_using_title_kwarg(self):
        title_type = WellType.objects.create(title="well-title", slug="none")
        slug_type = WellType.objects.create(title="none", slug="well-title")
        title = Well.objects.create(type=title_type)
        slug = Well.objects.create(type=slug_type)

        self.assertEqual(title, Well.objects.get_current(title="well-title"))

    def test_get_current_returns_using_slug_kwarg(self):
        title_type = WellType.objects.create(title="well-slug", slug="none")
        slug_type = WellType.objects.create(title="none", slug="well-slug")
        title = Well.objects.create(type=title_type)
        slug = Well.objects.create(type=slug_type)

        self.assertEqual(slug, Well.objects.get_current(slug="well-slug"))

    def test_get_current_should_default_to_title(self):
        title_type = WellType.objects.create(title="well-title", slug="none")
        slug_type = WellType.objects.create(title="none", slug="well-title")
        title = Well.objects.create(type=title_type)
        slug = Well.objects.create(type=slug_type)

        self.assertEqual(title, Well.objects.get_current("well-title"))

    def test_get_current_should_use_title_before_slug(self):
        title_type = WellType.objects.create(title="well-title", slug="none")
        slug_type = WellType.objects.create(title="none", slug="well-slug")
        title = Well.objects.create(type=title_type)
        slug = Well.objects.create(type=slug_type)

        self.assertEqual(
            title,
            Well.objects.get_current(title="well-title", slug="well-slug")
        )

    def test_get_current_should_use_title_arg_before_slug_arg(self):
        title_type = WellType.objects.create(title="well-title", slug="none")
        slug_type = WellType.objects.create(title="none", slug="well-slug")
        title = Well.objects.create(type=title_type)
        slug = Well.objects.create(type=slug_type)

        self.assertEqual(
            title,
            Well.objects.get_current("well-title", "well-slug")
        )

    def test_get_current_should_use_arg_before_slug(self):
        title_type = WellType.objects.create(title="well-title", slug="none")
        slug_type = WellType.objects.create(title="none", slug="well-slug")
        title = Well.objects.create(type=title_type)
        slug = Well.objects.create(type=slug_type)

        self.assertEqual(
            title,
            Well.objects.get_current("well-title", slug="well-slug")
        )

    def test_get_current_should_raise_DoesNotExist_on_no_params(self):
        type = WellType.objects.create(title="well-title", slug="well-slug")
        well = Well.objects.create(type=type)

        self.assertRaises(Well.DoesNotExist, Well.objects.get_current)

    def test_get_current_should_raise_DoesNotExist_on_nonexistent_arg(self):
        type = WellType.objects.create(title="none", slug="exists")
        well = Well.objects.create(type=type)

        self.assertRaises(Well.DoesNotExist, Well.objects.get_current,
                          "exists")

    def test_get_current_should_raise_DoesNotExist_on_nonexistent_title(self):
        type = WellType.objects.create(title="none", slug="exists")
        well = Well.objects.create(type=type)

        self.assertRaises(Well.DoesNotExist, Well.objects.get_current,
                          title="exists")

    def test_get_current_should_raise_DoesNotExist_on_nonexistent_slug(self):
        type = WellType.objects.create(title="exists", slug="none")
        well = Well.objects.create(type=type)

        self.assertRaises(Well.DoesNotExist, Well.objects.get_current,
                          slug="exists")

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
