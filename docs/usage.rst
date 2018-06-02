=====
Usage
=====


Using Fluent in a Django project requires understanding a number of concepts and
APIs, in addition to understanding the `Fluent syntax
<http://projectfluent.org/fluent/guide/>`_. This guide outlines the main things
you need.

TODO locale/language terminology


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
visit. It might have an English ``myapp/main.ftl`` file that looks like this:

.. literalinclude:: ../tests/locales/en/tests/docs.ftl
   :language: ftl

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
convention you should create a ``ftl_bundles.py`` file inside your Python
``myapp`` package, i.e. a ``myapp.ftl_bundles`` module.

Our ``ftl_bundles.py`` file will look like this:

.. code-block:: python

   from django_ftl.bundles import Bundle

   main = Bundle(['myapp/main.ftl'])

``Bundle`` takes a single required positional argument
which is a list of FTL files. See :class:`~django_ftl.bundles.Bundle` API docs
for other arguments.

Activating a locale/language
----------------------------

The most direct way to activate a specific language/locale is use
:func:`django_ftl.activate_locale`:

.. code-block:: python

   from django_ftl import activate_locale

   activate_locale("en-US")

The argument can be any BCP 47 locale tag, or a "language priority list"
(a prioritised, comma separated list of locale tags). For example::

  "en-US, en, fr"

It is recommended that the value passed in should be validated by your own code.
Normally it will come from a list of options that you have given to a user (see
:ref:`setting-user-language` below).

As soon as you activate a language, all ``Bundle`` objects will switch to using
that language. (Before activating, they will use your ``LANGUAGE_CODE`` setting
as a default, and this is also used as a fallback in the case of missing FTL
files or messages).

Using middleware
~~~~~~~~~~~~~~~~

``django-ftl`` comes with a few middleware that may help you automatically
activate a locale for every request. If you were using Django's built-in i18n
solution previously, or are still using it for some parts of your app, you may
also be using `django.middleware.locale.LocaleMiddleware
<https://docs.djangoproject.com/en/stable/ref/middleware/#django.middleware.locale.LocaleMiddleware>`_.

The way you choose to activate a given language will depend on your exact setup.

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
(which has been set by ``django.middleware.locale.LocaleMiddleware``) and
activates that language.

Instead of these two, you could also use
``"django_ftl.middleware.activate_from_request_session"`` by adding it to your
``MIDDLEWARE`` (somewhere after the session middleware). This middleware looks
for a language set in ``request.session``, as set by the ``set_language`` view
that Django provides.


Outside of the request-response cycle
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For code running outside of the request-response cycle (e.g. cron jobs or
asynchronous tasks), you will not be able to use middleware, and will need some
other way to determine the language to use. This might involve:

* a field on a model (e.g. ``User`` class) to store the locale preference.
* for asynchronous tasks such as Celery, you could pass the locale as an
  argument. For Celery, signals such as `task-prerun
  <http://docs.celeryproject.org/en/latest/userguide/signals.html#task-prerun>`_
  might be useful.

Once you have determined the locale to use, use
:func:`django_ftl.activate_locale` to activate it.

Using bundles from Python
-------------------------

After you have activated a locale, to obtain a translation you call the
``Bundle`` :meth:`~django_ftl.bundles.Bundle.format` method, passing in a
message ID and an optional dictionary of arguments:

.. code-block:: python

   >>> from myapp.ftl_bundles import main as ftl_bundle
   >>> ftl_bundle.format('events-title')
   'MyApp Events!'

   >>> ftl_bundle.format('events-greeting', {'username': 'boaty mcboatface'})
   'Hello, ⁨\u2068boaty mcboatface\u2069⁩'

TODO - explain unicode bidi chars

That's it for the basic case. See :meth:`~django_ftl.bundles.Bundle.format` for
further info about passing numbers and datetimes, and about how errors are
handled.

Lazy translations
~~~~~~~~~~~~~~~~~

Sometimes you need to translate a string lazily. This happens when you have a
string that is defined at module load time (see the Django `lazy translation
docs
<https://docs.djangoproject.com/en/stable/topics/i18n/translation/#lazy-translation`_
for more info). For this situation, you can use
:meth:`~django_ftl.bundles.Bundle.format_lazy` instead of ``format``. It takes
the same parameters, but doesn't generate the translation until the value is
used in a string context, such as in template rendering.

For example, the ``help_text`` of a model field should be done this way:

.. code-block:: python

   from django.db import models
   from myapp.ftl_bundles import main as ftl_bundle

   class MyThing(models.Model):
       name = models.CharField(help_text=ftl_bundle.format_lazy('mything-model-name-help-text'))

If you do not do this, then the ``help_text`` attribute will end up having
the text translated into the default language.

To prevent this from happening, you can also pass ``require_activate=True``
parameter to :meth:`~django_ftl.bundles.Bundle.__init__`. As long as you do not
put a ``activate_locale`` call at module level in your project, this will cause
the ``Bundle`` to raise an exception if attempt to use the ``format`` method at
module level.


Aliases
~~~~~~~

If you are using the ``format`` and ``format_lazy`` functions a lot, you can
save on typing by defining some appropriate aliases for your bundle methods at
the top of a module - for example:

.. code-block:: python

   from myapp.ftl_bundles import main as ftl_bundle

   ftl = ftl_bundle.format
   ftl_lazy = ftl_bundle.format_lazy


Then use ``ftl`` and ``ftl_lazy`` just as you would use ``ftl_bundle.format``
and ``ftl_bundle.format_lazy``.

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
<https://docs.djangoproject.com/en/stable/topics/i18n/translation/#the-set-language-redirect-view>`_.
(It is designed to work with Django's built-in i18n solution but works just as
well with django-ftl). It saves a user's language preference into the session
(or a cookie if you are not using sessions), which you can then use later in a
middleware or view, for example.
