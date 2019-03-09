#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function  # noqa: FI14

import os
import re
import subprocess
import sys

from setuptools import find_packages, setup
from setuptools.command.test import test as TestCommand

tests_requires = [
    'coverage==4.4.1',
    'mock>=1.0.1',
    'flake8>=2.1.0',
    'codecov>=2.0.0',
    'flake8-future-import>=0.4.5',
    'django-functest==1.0.4',
    'check-manifest',
]


class MyTestCommand(TestCommand):

    description = 'run linters, tests and create a coverage report'
    user_options = []

    def run_tests(self):
        self._run(['flake8', 'django_ftl', 'test'])
        self._run(['./runtests.py'])
        self._run(['check-manifest'])

    def _run(self, command):
        try:
            subprocess.check_call(command)
        except subprocess.CalledProcessError as error:
            print('Command "{0}" failed with exit code'.format(" ".join(command)), error.returncode)
            sys.exit(error.returncode)


def get_version(*file_paths):
    """Retrieves the version from django_ftl/__init__.py"""
    filename = os.path.join(os.path.dirname(__file__), *file_paths)
    version_file = open(filename).read()
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError('Unable to find version string.')


version = get_version("src", "django_ftl", "__init__.py")


if sys.argv[-1] == 'publish':
    try:
        import wheel
        print("Wheel version: ", wheel.__version__)
    except ImportError:
        print('Wheel library missing. Please run "pip install wheel"')
        sys.exit()
    os.system('python setup.py sdist upload')
    os.system('python setup.py bdist_wheel upload')
    sys.exit()

if sys.argv[-1] == 'tag':
    print("Tagging the version on git:")
    os.system("git tag -a %s -m 'version %s'" % (version, version))
    os.system("git push --tags")
    sys.exit()

readme = open('README.rst').read()
if hasattr(readme, 'decode'):
    readme = readme.decode('utf-8')
history = open('HISTORY.rst').read()
if hasattr(history, 'decode'):
    history = history.decode('utf-8')
history = history.replace(u'.. :changelog:', u'')

setup(
    name='django-ftl',
    version=version,
    description="""Django bindings for 'fluent', the localization system for today's world.""",
    long_description=readme + u'\n\n' + history,
    author='Luke Plant',
    author_email='L.Plant.98@cantab.net',
    url='https://github.com/django-ftl/django-ftl',
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
    install_requires=[
        'fluent.runtime',
        'Django>=1.11',
    ],
    tests_require=tests_requires,  # for 'setup.py test'
    extras_require={
        'develop': tests_requires,  # for 'pip install fluent.runtime[develop]'
    },
    license="MIT",
    zip_safe=False,
    keywords='django-ftl',
    cmdclass={'test': MyTestCommand},
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Framework :: Django :: 1.11',
        'Framework :: Django :: 2.0',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
)
