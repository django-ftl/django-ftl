=============================
django-ftl
=============================

.. image:: https://badge.fury.io/py/django-ftl.svg
    :target: https://badge.fury.io/py/django-ftl

.. image:: https://readthedocs.org/projects/django-ftl/badge/?version=latest&style=flat
   :target: https://django-ftl.readthedocs.io

.. image:: https://travis-ci.org/django-ftl/django-ftl.svg?branch=master
    :target: https://travis-ci.org/django-ftl/django-ftl

.. image:: https://codecov.io/gh/django-ftl/django-ftl/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/django-ftl/django-ftl

django-ftl is a Django package for using for `Fluent <https://projectfluent.org/>`_, a
localization system for today's world.

This package builds upon the `Python implementation of Fluent
<https://github.com/projectfluent/python-fluent>`_ and provides:

* A structure for setting up and managing your ``.ftl`` files.
* Methods for switching/setting the current language.
* Integration into Django templates.


Why would I use this?
---------------------

The defacto standard in Django world is GNU Gettext. See this `Fluent vs gettext
<https://github.com/projectfluent/fluent/wiki/Fluent-vs-gettext>`_ page for a
comparison. In brief, here are some advantages:

* Fluent makes concerns like plural rules the job of the translator.

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
        'there is %(count)d object.',
        'there are %(count)d objects.',
    count) % {
        'count': count,
    }

Finally, this still doesn't work very well, because often you want to special
case zero anyway - "there are no objects" (or "your inbox is empty" etc.)
instead of "there are 0 objects".

In Fluent, plural rules are one example of a more generic mechanism for
selecting variants, and the translator is in control. The equivalent with
fluent/django-ftl, with special handling of the zero case included, looks like
this in an English ``.ftl`` file:

::

  there-are-some-objects = { $count ->
      [0]     There are no objects.
      [1]     There is one object.
      [other] There are { $count } objects.
   }

The Python code referencing this will only need to use the ID
(``there-are-some-objects``) and pass the ``$count`` argument.

Another problem that comes up is gender - for example, in French adjectives must
agree in gender with the person being described. This can be solved in Fluent by
passing the gender of the person as an argument, and allowing the translator to
use the variant mechanism to write the correct language. This contrasts with GNU
Gettext where the developer would have to create separate message strings for
each case, because the message format is not powerful enough to allow the
translator to add variant selection. Also, these different message strings will
be identical in languages which don't have that feature — in other words, the
grammatical features of all languages end up either having a disproportionate
effect on the source code and on other translators, or being neglected entirely.


Documentation
-------------

The documentation for how to use django-ftl is in the docs/folder and online at
https://django-ftl.readthedocs.io.

Status
------

This package should be considered a beta. While it has a good feature set, test
suite and docs, it has not been used a huge amount in production. In addition,
it currently relies on `our fork <https://github.com/django-ftl/python-fluent>`_
of `python-fluent <https://github.com/projectfluent/python-fluent>`_, which has
the following significant features/changes not yet merged to the official
version:

* Refined error handling for functions (see `PR
  <https://github.com/projectfluent/python-fluent/pull/92>`_).

* Compiler implementation (see `compiler branch
  <https://github.com/django-ftl/python-fluent/tree/compiler_implementation>`_).
  This is an additional and much faster implementation of ``FluentBundle`` that
  compiles FTL messages to Python `AST
  <https://docs.python.org/3/library/ast.html>`_, running the result through
  `compile
  <https://docs.python.org/3/library/functions.html?highlight=compile#compile>`_
  and `exec
  <https://docs.python.org/3/library/functions.html?highlight=compile#exec>`_.

  Use of ``exec`` for high performance Python code is an established technique
  used by other projects (e.g. `Jinja2 <http://jinja.pocoo.org/>`_ and `Mako
  <https://www.makotemplates.org/>`_), and we only use exec on data derived from
  FTL files, which will normally be created by translators and not potential
  attackers. Nevertheless there are understandably some security concerns. Using
  AST objects rather than strings for creating Python code dynamically makes our
  use of ``exec`` intrinsically safer than some of these other projects, and we
  also use some `defence-in-depth techniques
  <https://github.com/django-ftl/python-fluent/blob/compiler_implementation/fluent.runtime/fluent/runtime/codegen.py>`_.

  When using the compiler as opposed to the resolver, the additional up-front
  processing of the FTL messages could incur a noticeable startup cost
  (typically of the order of .5ms per message). For long running Django
  processes this is usually a very good trade-off given the performance
  benefits.

* 'Escaper' functionality (see `escapers branch
  <https://github.com/django-ftl/python-fluent/tree/implement_escapers>`_). This
  allows us to `handle embedded HTML correctly
  <https://django-ftl.readthedocs.io/en/latest/usage.html#html-escaping>`_. The
  mechanism for doing this has been implemented as part of python-fluent in a
  generic way, and then used in django-ftl to handle HTML escaping in templates
  with a minimum of work.

Credits
-------

Tools used in rendering this package:

*  Cookiecutter_
*  `cookiecutter-djangopackage`_

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`cookiecutter-djangopackage`: https://github.com/pydanny/cookiecutter-djangopackage
