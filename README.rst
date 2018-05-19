=============================
django-ftl
=============================

.. image:: https://badge.fury.io/py/django-ftl.svg
    :target: https://badge.fury.io/py/django-ftl

.. image:: https://travis-ci.org/django-ftl/django-ftl.svg?branch=master
    :target: https://travis-ci.org/django-ftl/django-ftl

.. image:: https://codecov.io/gh/django-ftl/django-ftl/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/django-ftl/django-ftl

Django bindings for 'fluent', the localization system for today's world.

Documentation
-------------

The full documentation is at https://django-ftl.readthedocs.io.

Quickstart
----------

Install django-ftl::

    pip install django-ftl

Add it to your ``INSTALLED_APPS``:

.. code-block:: python

    INSTALLED_APPS = (
        ...
        'django_ftl.apps.DjangoFtlConfig',
        ...
    )

Features
--------

* TODO

Running Tests
-------------

Does the code actually work?

::

    source <YOURVIRTUALENV>/bin/activate
    (myenv) $ pip install tox
    (myenv) $ tox


Credits
-------

Tools used in rendering this package:

*  Cookiecutter_
*  `cookiecutter-djangopackage`_

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`cookiecutter-djangopackage`: https://github.com/pydanny/cookiecutter-djangopackage
