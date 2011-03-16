import datetime
from django.db import models


class WellManager(models.Manager):
    def get_current(self, title):
        now = datetime.datetime.now()
        return self.filter(title=title, pub_date__lte=now)[0]
