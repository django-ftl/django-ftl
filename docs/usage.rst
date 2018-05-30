=====
Usage
=====


Using Fluent in a Django project requires understanding a number of things, in
addition to understanding the `Fluent syntax
<http://projectfluent.org/fluent/guide/>`_. This guide outlines the main steps.


FTL files and layout
--------------------

Fluent translations are placed in Fluent Translation List files, with suffix
``.ftl``. For them to be found by django-ftl, you need to use the following
conventions, which align with the convention used across tools that use Fluent.

For the sake of this tutorial, we will assume you are writing a Django app
(reusable or non-reusable) called ``myapp`` - that is, it forms a Python
top-level module/package called ``myapp``. You will need to replace ``myapp``
with the actual name of your app.

You will need your directory layout to include the following::

   myapp/
     __init__.py
     ftl_bundles.py
     locales/
       en/
         myapp/
             main.ftl
       de
         myapp/
             main.ftl

That is:

* Within your ``myapp`` package directory, create a ``locales`` directory. In a
  typical Django app, this ``locales`` directory exists at the same level as
  your app-specific ``templates``, ``templatetags``, ``static`` etc.
  directories.

* For each locale you support, within that folder create a directory with the
  locale name. The example above shows English and German. Locale names should
  be in `BCP 47 format <https://tools.ietf.org/html/bcp47>`_.

  It is recommended that you use the capitalisation convention recommended by
  BCP47, which is:

  * Lower case for the language code
  * Title case for script code
  * Upper case for region code

  e.g. en, en-GB, en-US, de-DE, zh-Hans-CN

  django-ftl does not enforce this convention - it will find locale files if
  different capitalisation is used. However, if multiple directories exist for
  the same locale, differing only by case (e.g. ``EN-US`` and ``en-US``), and
  their contents are not the same, then your FTL files will likely not be found
  correctly.

  Finally, django-ftl will also find the FTL files if you name the directories
  in Unix convention with underscores e.g. ``en_GB``, although for the sake of
  consistency this is also not recommended.

* Within each specific locale directory, create another directory with the name
  of your app. This is necessary to give a separate namespace for your FTL
  files, so that they don't clash with the FTL files that might be provided by
  other Django apps. By doing it this way, you can reference FTL
  files from other apps in your app — this is very similar to how templates
  and static files work in Django

* Within that ``myapp`` directory, you can add any number of further
  sub-directories, and can split your FTL files up into as many files as you
  want. For the remainder of this guide we will assume a single
  ``myapp/main.ftl`` file.


The contents of these files must be valid Fluent syntax. For the sake of this
guide, we will assume ``myapp`` has an 'events' page which greets the user, and
informs them how many new events have happened on the site since their last
visit. It might have an English ``myapp/main.ftl`` file that looks like this::

  events-title = MyApp Events!

  events-greeting = Hello, { $username }

  events-new-events-info = { $count ->
      [0]     There have been no new events since your last event.
      [1]     There has been one new event since your last visit.
     *[other] There have been { $count } new events since your last visit.
   }

In this ``.ftl`` file, ``events-title``, ``events-greeting`` and
``events-new-events-info`` are Fluent message IDs. Note that we have used
``events-`` as a adhoc namespace for this 'events' page, to avoid name clashes
with other messages from our app. It's recommended to use a prefix like this for
different pages or components in your app.


Bundles
-------

To use ``.ftl`` files with django-ftl, you must first define a Bundle. They
define a collection of ``.ftl`` files that you want to use, and are responsible
for finding and loading these files. The definition of a Bundle can go anywhere
in your project, but by convention we should create a ``ftl_bundles.py`` inside
your Python ``myapp`` package, i.e. a ``myapp.ftl_bundles`` module.

Our ``ftl_bundles.py`` will look like this:

.. code-block:: python

   from django_ftl.bundles import Bundle

   main = Bundle(['myapp/main.ftl'])

:class:`~django_ftl.bundles.Bundle` takes a single positional argument which is
a list of FTL files. See API docs for other arguments.


Activating a language
---------------------

TODO

Using bundles from Python
-------------------------

TODO



Using bundles from Django templates
-----------------------------------

To use django-ftl template tags in a project, ``django_ftl`` must be added to
your ``INSTALLED_APPS`` like this:

.. code-block:: python

    INSTALLED_APPS = (
        ...
        'django_ftl.apps.DjangoFtlConfig',
        ...
    )
