from armstrong.dev.tasks import *

settings = {
    'DEBUG': True,
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

main_app = "arm_wells"
full_name = "armstrong.core.arm_wells"
tested_apps = (main_app, 'arm_wells_support')
pip_install_first = True
