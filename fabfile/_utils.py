from contextlib import contextmanager
try:
    import coverage
except ImportError:
    coverage = False
import glob
from os.path import basename, dirname


from fabric.api import *
from fabric.decorators import task

import os, sys
sys.path.insert(0, os.path.join(os.path.realpath('.'), '..'))

try:
    from d51.django.virtualenv.test_runner import run_tests
except ImportError, e:
    import sys
    sys.stderr.write("This project requires d51.django.virtualenv.test_runner\n")
    sys.exit(-1)

@contextmanager
def html_coverage_report(directory="./coverage"):
    # This relies on this being run from within a directory named the same as
    # the repository on GitHub.  It's fragile, but for our purposes, it works.
    if coverage:
        module_name = basename(dirname(dirname(__file__)))
        files_to_cover = glob.glob("./%s/*.py" % module_name.replace('.', '/'))
        cov = coverage.coverage(branch=True, include=files_to_cover)
        cov.start()
    yield

    if coverage:
        cov.stop()
        cov.html_report(directory=directory)
    else:
        print "Install coverage.py to measure test coverage"
