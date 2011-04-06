from ._utils import *

@task
def pep8():
    local('find ./armstrong -name "*.py" | xargs pep8', capture=False)


@task
def test():
    settings = {
        'INSTALLED_APPS': (
            'django.contrib.contenttypes',
            'armstrong.core.arm_wells',
            'armstrong.core.arm_wells.tests.arm_wells_support',
        ),
        'TEMPLATE_CONTEXT_PROCESSORS': (
            'django.core.context_processors.request',
        ),
        'ROOT_URLCONF': 'armstrong.core.arm_wells.tests.arm_wells_support.urls',
    }
    with html_coverage_report():
        run_tests(settings, 'arm_wells_support', 'arm_wells')
