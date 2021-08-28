=============================
django-ftl
=============================

.. image:: https://badge.fury.io/py/django-ftl.svg
    :target: https://badge.fury.io/py/django-ftl

.. image:: https://readthedocs.org/projects/django-ftl/badge/?version=latest&style=flat
   :target: https://django-ftl.readthedocs.io

.. image:: https://github.com/django-ftl/django-ftl/workflows/Python%20package/badge.svg
   :target: https://github.com/django-ftl/django-ftl/actions?query=workflow%3A%22Python+package%22+branch%3Amaster

django-ftl is a Django package for using for `Fluent <https://projectfluent.org/>`_, a
localization system for today's world. (It would have been called django-fluent but that was
already `taken <https://django-fluent.org/>`_).

This package builds upon `fluent-compiler
<https://github.com/django-ftl/fluent-compiler>`_ and provides:

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

The library is now pretty stable, with a full test suite, no major missing
features and no major breaking changes planned.

It has seen real-world usage in:

* `Firefox Relay <https://relay.firefox.com/>`_ - see `fx-private-relay GitHub
  project <https://github.com/mozilla/fx-private-relay>`_.
* `Learn Scripture <https://learnscripture.net/>`_ - the original project it was
  created for, see the `GitLab learnscripture.net project
  <https://gitlab.com/learnscripture/learnscripture.net>`_.
* Probably a fair number of other projects, but I don’t know about them…


Credits
-------

Tools used in rendering this package:

*  Cookiecutter_
*  `cookiecutter-djangopackage`_

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`cookiecutter-djangopackage`: https://github.com/pydanny/cookiecutter-djangopackage
