#!/bin/sh

set -x

# Basic tests
pre-commit run check-manifest --all-files
pre-commit run isort --all-files
pre-commit run flake8 --all-files
pytest || exit 1

umask 000
rm -rf build dist
git ls-tree --full-tree --name-only -r HEAD | xargs chmod ugo+r
find . -type d | xargs chmod ugo+rx

./setup.py sdist bdist_wheel || exit 1

VERSION=$(./setup.py --version) || exit 1

twine upload dist/django-ftl-$VERSION.tar.gz dist/django_ftl-$VERSION-py3-none-any.whl || exit 1
