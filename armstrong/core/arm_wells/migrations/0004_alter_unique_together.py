# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('arm_wells', '0003_cp_summaries_to_wells'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='well',
            unique_together=set([('type', 'pub_date')]),
        ),
    ]

