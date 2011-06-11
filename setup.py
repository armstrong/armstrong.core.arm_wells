from distutils.core import setup
import os

PACKAGE_NAME = "armstrong.core.arm_wells"
VERSION = ("0", "1", "0", "1")
NAMESPACE_PACKAGES = []

# TODO: simplify this process
def generate_namespaces(package):
    new_package = ".".join(package.split(".")[0:-1])
    if new_package.count(".") > 0:
        generate_namespaces(new_package)
    NAMESPACE_PACKAGES.append(new_package)
generate_namespaces(PACKAGE_NAME)

if os.path.exists("MANIFEST"):
    os.unlink("MANIFEST")

# Borrowed and modified from django-registration
# Compile the list of packages available, because distutils doesn't have
# an easy way to do this.
packages, data_files = [], []
root_dir = os.path.dirname(__file__)
if root_dir:
    os.chdir(root_dir)


def build_package(dirpath, dirnames, filenames):
    # Ignore dirnames that start with '.'
    for i, dirname in enumerate(dirnames):
        if dirname.startswith('.'):
            del dirnames[i]
    if '__init__.py' in filenames and 'steps.py' not in filenames:
        pkg = dirpath.replace(os.path.sep, '.')
        if os.path.altsep:
            pkg = pkg.replace(os.path.altsep, '.')
        packages.append(pkg)
    elif filenames:
        # Strip off the length of the package name plus the trailing slash
        prefix = dirpath[len(PACKAGE_NAME) + 1:]
        for f in filenames:
            # Ignore all dot files and any compiled
            if f.startswith(".") or f.endswith(".pyc"):
                continue
            data_files.append(os.path.join(prefix, f))


[build_package(dirpath, dirnames, filenames) for dirpath, dirnames, filenames
        in os.walk(PACKAGE_NAME.replace(".", "/"))]

setup(
    name=PACKAGE_NAME,
    version=".".join(VERSION),
    description='Provides the basic content well manipulation',
    author='Bay Citizen & Texas Tribune',
    author_email='info@armstrongcms.org',
    url='http://github.com/armstrong/armstrong.core.arm_wells/',
    packages=packages,
    package_data={PACKAGE_NAME: data_files, },
    namespace_packages=NAMESPACE_PACKAGES,
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
