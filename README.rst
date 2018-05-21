=============================
django-ftl
=============================

.. image:: https://badge.fury.io/py/django-ftl.svg
    :target: https://badge.fury.io/py/django-ftl

.. image:: https://travis-ci.org/django-ftl/django-ftl.svg?branch=master
    :target: https://travis-ci.org/django-ftl/django-ftl

.. image:: https://codecov.io/gh/django-ftl/django-ftl/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/django-ftl/django-ftl

Django bindings for `Fluent <https://projectfluent.org/>`_, a localization
system for today's world.

This package builds upon the `Python implementation of Fluent
<https://github.com/projectfluent/python-fluent>`_ and provides:

* A more opinionated way to set up and managed your ``.ftl`` files
* Integration into Django templates


CURRENT STATUS: Minimal functionality implemented (bundles and template tags),
but no docs yet.


Why would I use this?
---------------------

The defacto standard in Django world is GNU Gettext. See this `Fluent vs gettext
<https://github.com/projectfluent/fluent/wiki/Fluent-vs-gettext>`_ page for a
comparison. In brief, here are some advantages:

* Fluent makes concerns like plural rules the job of the translator

* Fluent gives translators the power to obey language specific rules
  (gender, case, plurals) that the developer may not be aware of,
  and shouldn't have to build into the software.

* Fluent integrates number and date formatting, and gives both developer and
  translators control over these, instead of these having to be handled
  separately, and only controlled by the developer.

To give an example, in GNU Gettext there is support for plural rules. However,
this is the only language specific feature Gettext supports, and it is kind of
bolted on afterwards. The developer also has to partially hard code the English
rules (that is, the fact that there are two variants in English), as per the
`Django docs
<https://docs.djangoproject.com/en/dev/topics/i18n/translation/#pluralization>`_:


.. code-block:: python

   msg = ngettext(
        'there is %(count)d object',
        'there are %(count)d objects',
    count) % {
        'count': count,
    }

Finally, this still doesn't work very well, because often you want to special
case zero anyway - "there are no objects" (or "your inbox is empty" etc.)
instead of "there are 0 objects".

In Fluent, plural rules are one example of a more generic mechanism for
selecting variants, and the translator is in control. The equivalent with
fluent/django-ftl, with special handling of the zero case included, looks like
this:


English ``.ftl`` file::

  there-are-some-objects = { $count ->
      [0]     There are no objects
      [1]     There is one object
      [other] There are { $count } objects
   }


Python code:

.. code-block:: python

   msg = messageContext.format('there-are-some-objects', {'count': count})

Or Django template code:

.. code-block:: html+django

   {% ftl 'server' 'there-are-some-objects' count=count %}



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

Install our fork of the python-fluent repo -
https://github.com/django-ftl/python-fluent/tree/implement_format - and the
``implement_format`` branch::

    pip install git+ssh://git@github.com/django-ftl/python-fluent.git@implement_format

Features
--------

* TODO - none yet


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
