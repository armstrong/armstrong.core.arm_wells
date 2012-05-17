import datetime
from django.db import models


class WellManager(models.Manager):
    def get_current(self, title):
        now = datetime.datetime.now()
        return self.filter(type__title=title, pub_date__lte=now,
                active=True).exclude(expires__lte=now,
                        expires__isnull=False).latest('pub_date')
