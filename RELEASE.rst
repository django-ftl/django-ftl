Release process
===============

* Tests, including flake8, isort and check-manifest

* Update HISTORY.rst, removing "(in development)"

* Update the version number, removing the ``-dev1`` part

  * setup.py
  * src/django_ftl/__init__.py
  * docs/conf.py

* Commit

* Ensure correct file permissions::

    git ls-tree --full-tree --name-only -r HEAD | xargs chmod ugo+r

* Make sure all is committed

* Release to PyPI::

    ./release.sh

* Tag the release e.g.::

    git tag v0.1.0

* Update the version numbers again, moving to the next release, and adding "-dev1"

* Add new section to HISTORY.rst

* ``git push --tags``
