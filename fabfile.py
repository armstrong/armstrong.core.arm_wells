from armstrong.dev.tasks import *

settings = {
    'DEBUG': True,
    'INSTALLED_APPS': (
        'django.contrib.admin',
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.sites',
        'django.contrib.staticfiles',
        'armstrong.core.arm_access',
        'armstrong.core.arm_sections',
        'armstrong.core.arm_wells',
        'armstrong.core.arm_wells.tests.arm_wells_support',
        'armstrong.apps.articles',
        'armstrong.apps.content',
        'south',
    ),
    'STATIC_URL': '/static/',
    'DATABASE': {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': './testing.db',
        },
    },
    'TEMPLATE_CONTEXT_PROCESSORS': (
        'django.core.context_processors.request',
        'django.contrib.auth.context_processors.auth',
    ),
    'ROOT_URLCONF': 'armstrong.core.arm_wells.tests.arm_wells_support.urls',
    'SITE_ID': 1,
}

main_app = "arm_wells"
full_name = "armstrong.core.arm_wells"
tested_apps = (main_app, 'arm_wells_support')
pip_install_first = True
