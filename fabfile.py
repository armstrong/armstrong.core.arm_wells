from armstrong.dev.tasks import *

settings = {
    'DEBUG': True,
    'INSTALLED_APPS': (
        'django.contrib.contenttypes',
        'armstrong.core.arm_wells',
        'south',
    ),
    'TEMPLATE_CONTEXT_PROCESSORS': (
        'django.core.context_processors.request',
    ),
}

main_app = "arm_wells"
full_name = "armstrong.core.arm_wells"
tested_apps = (main_app,)
pip_install_first = True
