from ._utils import *

@task
def test():
    settings = {
        'INSTALLED_APPS': (
            'django.contrib.contenttypes',
            'armstrong.core.arm_well',
            'armstrong.core.arm_well.tests.arm_well_support',
        ),
        'ROOT_URLCONF': 'armstrong.core.arm_well.tests.arm_well_support.urls',
    }
    run_tests(settings, 'arm_well_support', 'arm_well')

