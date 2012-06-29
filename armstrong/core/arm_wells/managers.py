import datetime
from django.db import models


class WellManager(models.Manager):
    def get_current(self, title=None, slug=None):
        now = datetime.datetime.now()
        filter_params = dict(pub_date__lte=now, active=True)

        if (title):
            filter_params['type__title'] = title
        elif (slug):
            filter_params['type__slug'] = slug
        else:
            raise self.model.DoesNotExist()

        return (self.filter(**filter_params)
                    .exclude(expires__lte=now, expires__isnull=False)
                    .latest('pub_date'))
