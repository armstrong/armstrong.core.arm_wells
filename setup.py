from setuptools import setup

setup(
    name='armstrong.core.arm_wells',
    version='0.1',
    description='Provides the basic content well manipulation',
    author='Bay Citizen & Texas Tribune',
    author_email='info@armstrongcms.org',
    url='http://github.com/armstrongcms/armstrong.core.arm_wells/',
    packages=[
        'armstrong',
        'armstrong.core',
        'armstrong.core.arm_wells',
    ],

    install_requires=[
        'distribute',
    ],

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
)
