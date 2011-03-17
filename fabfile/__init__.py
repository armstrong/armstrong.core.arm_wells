from ._utils import *

@task
def pep8():
    local('find ./armstrong -name "*.py" | xargs pep8', capture=False)

@task
def test():
    settings = {
        'INSTALLED_APPS': (
            'django.contrib.contenttypes',
            'armstrong.core.arm_well',
            'armstrong.core.arm_well.tests.arm_well_support',
        ),
        'TEMPLATE_CONTEXT_PROCESSORS': (
            'django.core.context_processors.request',
        ),
        'ROOT_URLCONF': 'armstrong.core.arm_well.tests.arm_well_support.urls',
    }
    run_tests(settings, 'arm_well_support', 'arm_well')

