#!/usr/bin/env python

# A set of benchmarks, generally used to test out different implementation
# choices against each other.

# This should be run using pytest, see end of file
from __future__ import absolute_import, print_function, unicode_literals

import os
import subprocess
import sys

import pytest

from django_ftl import activate
from django_ftl.bundles import Bundle

this_file = os.path.abspath(__file__)


# For testing changes, can use multiple runs and compare mean or OPS figures on
# subsequent runs, or test at the same time by creating multiple `Bundle`
# implementations and add them to `params` below.

@pytest.fixture(params=[Bundle])
def bundle(request):
    return request.param(['benchmarks/benchmarks.ftl'], default_locale='en')


def test_simple_string_default_locale_present(bundle, benchmark):
    activate('en')
    result = benchmark(lambda: bundle.format('simple-string'))
    assert result == "Hello I am a simple string"


def test_simple_string_other_locale_present(bundle, benchmark):
    activate('tr')
    result = benchmark(lambda: bundle.format('simple-string'))
    assert result == "Merhaba ben basit bir metinim"


def test_simple_string_present_in_fallback(bundle, benchmark):
    activate('tr')
    result = benchmark(lambda: bundle.format('simple-string-present-in-fallback'))
    assert result == "Hello I am a simple string present in fallback"


if __name__ == '__main__':
    # You can execute this file directly, and optionally add more py.test args
    # to the command line (e.g. -k for keyword matching certain tests).
    subprocess.check_call(["pytest", "--benchmark-warmup=on", "--benchmark-sort=name", this_file] + sys.argv[1:])
