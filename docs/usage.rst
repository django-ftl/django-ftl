=====
Usage
=====


Using Fluent in a Django project requires understanding a number of concepts and
APIs, in addition to understanding the `Fluent syntax
<http://projectfluent.org/fluent/guide/>`_. This guide outlines the main things
you need.


FTL files and layout
--------------------

Fluent translations are placed in Fluent Translation List files, with suffix
``.ftl``. For them to be found by django-ftl, you need to use the following
conventions, which align with the conventions used across other tools that use
Fluent (such as Pontoon).

For the sake of this tutorial, we will assume you are writing a Django app
(reusable or non-reusable) called ``myapp`` - that is, it forms a Python
top-level module/package called ``myapp``. You will need to replace ``myapp``
with the actual name of your app.

You will need your directory layout to match the following example::

   myapp/
     __init__.py
     ftl_bundles.py
     locales/
       en/
         myapp/
             main.ftl
       de/
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

* It is recommended that you follow the capitalisation convention in BCP47,
  which is:

  * Lower case for the language code
  * Title case for script code
  * Upper case for region code

  e.g. en, en-GB, en-US, de-DE, zh-Hans-CN

  django-ftl does not enforce this convention - it will find locale files if
  different capitalisation is used. However, if multiple directories exist for
  the same locale, differing only by case (e.g. ``EN-US`` and ``en-US``), and
  their contents are not the same, then your FTL files will probably not be
  found correctly.

  Finally, django-ftl will also find the FTL files if you name the directories
  in Unix convention with underscores e.g. ``en_GB``, although for the sake of
  consistency and other tools this is also not recommended.

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

To use ``.ftl`` files with django-ftl, you must first define a
:class:`~django_ftl.bundles.Bundle`. They represent a collection of ``.ftl``
files that you want to use, and are responsible for finding and loading these
files. The definition of a ``Bundle`` can go anywhere in your project, but by
convention you should create a ``ftl_bundles.py`` inside your Python ``myapp``
package, i.e. a ``myapp.ftl_bundles`` module.

Our ``ftl_bundles.py`` will look like this:

.. code-block:: python

   from django_ftl.bundles import Bundle

   main = Bundle(['myapp/main.ftl'])

:class:`~django_ftl.bundles.Bundle` takes a single required positional argument
which is a list of FTL files. See API docs for other arguments.


Activating a language
---------------------

The most direct way to activate a specific language/locale is use
:func:`django_ftl.activate_locale`:

.. code-block:: python

   from django_ftl import activate_locale

   activate_language("en-US")

The argument can be any BCP 47 locale tag, or a "language priority list"
(a prioritised, comma separated list of locale tags). For example::

  "en-US, en, fr"

It is recommended that the value passed in should be validated by your own code.
Normally it will come from a list of options that you have given to a user (see
:ref:`setting-user-language` below).

As soon as you activate a language, all ``Bundle`` objects will switch to using
that language. (Before activating, by default they will use your
``LANGUAGE_CODE`` setting as a default, and this is also used as a fallback in
the case of missing FTL files or messages).

Using middleware
~~~~~~~~~~~~~~~~

``django-ftl`` comes with a few middleware that may help you automatically
activate a locale for every request. If you were using Django's built-in i18n
solution previously, or are still using it for some parts of your app, you may
also be using `django.middleware.locale.LocaleMiddleware
<https://docs.djangoproject.com/en/2.0/ref/middleware/#django.middleware.locale.LocaleMiddleware>`_.

The way you choose to activate a given language will therefore depend on your
exact setup.

If you are already using ``django.middleware.locale.LocaleMiddleware``, and want
to continue using it, the easiest solution is to add
``"django_ftl.middleware.activate_from_request_language_code"`` after it in your
``MIDDLEWARE`` setting:

.. code-block:: python

   MIDDLEWARE = [
         ...
         "django.middleware.locale.LocaleMiddleware",
         "django_ftl.middleware.activate_from_request_language_code"
         ...
   ]

This is a very simple middleware that simply looks at ``request.LANGUAGE_CODE``
(which has been set by ``ango.middleware.locale.LocaleMiddleware``) and
activates that language.

Instead of these two, you could also use
``"django_ftl.middleware.activate_from_request_session"`` by adding it to your
``MIDDLEWARE``, after the session middleware. This middleware looks for a
language set in ``request.session``, as set by the ``set_language`` view that
Django provides.


Outside of the request-response cycle
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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

TODO - the rest


.. _setting-user-language:

Setting the user language preference
------------------------------------

How you want to set and store the user's language preference will depend on your
application. For example, you can set it in a cookie, in the session, or store
it as a user preference.

Django has a built-in ``set_language`` view that you can use with django-ftl -
see the `set_language docs
<https://docs.djangoproject.com/en/2.0/topics/i18n/translation/#the-set-language-redirect-view>`_.
This saves language preference in the session (or a cookie if you are not using
the session), which you can then use later in a middleware, for example. This is
designed to work with Django's built-in i18n solution but works just as well
with django-ftl.
