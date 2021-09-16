=====
Usage
=====


Using Fluent in a Django project requires understanding a number of concepts and
APIs, in addition to understanding the `Fluent syntax
<http://projectfluent.org/fluent/guide/>`_. This guide outlines the main things
you need.

Terminology
-----------

Internationalization and localization (i18n and l10n) tools usually distinguish
between ‘languages’ and ‘locales’. ‘Locale’ is a broader term than includes
other cultural/regional differences, such as how numbers and dates are
represented.

Since they go together, Fluent not only addresses language translation, it also
integrates locale support. If a message contains a number substitution, when
different locales are active the number formatting will match the language
automatically. For this reason the django-ftl docs generally do not make a big
distinction between these terms, but tend to use ‘locale’ (which includes
language).

Django's `i18n docs
<https://docs.djangoproject.com/en/stable/topics/i18n/#term-locale-name>`_
distinguish between ‘locale name’ (which look like ``it``, ``en_US`` etc) and
‘language code’ (which look like ``it``, ``en-us``). In reality there is a lot
of overlap between these. Most modern systems (e.g. `unicode CLDR
<http://cldr.unicode.org/>`_) use BCP 47 language tags, which are the same as
‘language codes’. They in fact represent locales as well as languages, and have
a mechanism for incorporating more specific locale information.

Fluent and django-ftl use BCP 47 language tags in all their APIs (more
information below).


FTL files and layout
--------------------

Fluent translations are placed in Fluent Translation List files, with the suffix
``.ftl``. For them to be found by django-ftl, you need to use the following
conventions, which align with the conventions used across other tools that use
Fluent (such as Pontoon).

For the sake of this guide, we will assume you are writing a Django app
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

* It is recommended that you follow the capitalization convention in BCP 47,
  which is:

  * Lower case for the language code
  * Title case for script code
  * Upper case for region code

  e.g. en, en-GB, en-US, de-DE, zh-Hans-CN

  django-ftl does not enforce this convention - it will find locale files if
  different capitalization is used. However, if multiple directories exist for
  the same locale, differing only by case (e.g. ``EN-US`` and ``en-US``), and
  their contents are not the same, then your FTL files will probably not be
  found correctly.

  Finally, django-ftl will also find the FTL files if you name the directories
  in Unix “locale name” convention with underscores e.g. ``en_GB``, although for
  the sake of consistency and other tools this is also not recommended.

* Within each specific locale directory, create another directory with the name
  of your app. This is necessary to give a separate namespace for your FTL
  files, so that they don't clash with the FTL files that might be provided by
  other Django apps. By doing it this way, you can reference FTL
  files from other apps in your app — this is very similar to how templates
  and static files work in Django.

* Within that ``myapp`` directory, you can add any number of further
  sub-directories, and can split your FTL files up into as many files as you
  want. For the remainder of this guide we will assume a single
  ``myapp/main.ftl`` file for each locale.


The contents of these files must be valid Fluent syntax. For the sake of this
guide, we will assume ``myapp`` has an 'events' page which greets the user, and
informs them how many new events have happened on the site since their last
visit. It might have an English ``myapp/main.ftl`` file that looks like this:

.. literalinclude:: ../tests/locales/en/tests/docs.ftl

In this ``.ftl`` file, ``events-title``, ``events-greeting`` and
``events-new-events-info`` are Fluent message IDs. Note that we have used
``events-`` as an adhoc namespace for this 'events' page, to avoid name clashes
with other messages from our app. It's recommended to use a prefix like this for
different pages or components in your app.


Bundles
-------

To use ``.ftl`` files with django-ftl, you must first define a
:class:`~django_ftl.bundles.Bundle`. They represent a collection of ``.ftl``
files that you want to use, and are responsible for finding and loading these
files. The definition of a ``Bundle`` can go anywhere in your project, but we
recommend the convention of creating a ``ftl_bundles.py`` file inside your
Python ``myapp`` package, i.e. a ``myapp.ftl_bundles`` module.

Our ``ftl_bundles.py`` file will look like this:

.. code-block:: python

   from django_ftl.bundles import Bundle

   main = Bundle(['myapp/main.ftl'])

``Bundle`` takes a single required positional argument
which is a list of FTL files. See :class:`~django_ftl.bundles.Bundle` API docs
for other arguments.

Activating a locale/language
----------------------------

The most direct way to activate a specific language/locale is to use
:func:`django_ftl.activate`:

.. code-block:: python

   from django_ftl import activate

   activate("en-US")

The argument can be any BCP 47 language tag, or a "language priority list"
(a prioritized, comma separated list of language tags). For example::

  "en-US, en, fr"

It is recommended that the value passed in should be validated by your own code.
Normally it will come from a list of options that you have given to a user (see
:ref:`setting-user-language` below).

As soon as you activate a language, all ``Bundle`` objects will switch to using
that language, for the current thread only. (Before activating, they will use
your ``LANGUAGE_CODE`` setting as a default if ``require_activate=False``, and
this is also used as a fallback in the case of missing FTL files or messages).

Please note that ``activate`` is stateful, meaning it is essentially a global
(thread local) variable that is preserved between requests. This introduces the
possibility that one user's request changes the behavior of subsequent requests
made by a completely different user. This problem can also affect test isolation
in automated tests. The best way to avoid these problems is to use
:func:`django_ftl.override` instead:


.. code-block:: python

   from django_ftl import override

   with override("en-US"):
       pass  # Code that uses this language

Alternatively, ensure that :func:`django_ftl.deactivate` is called at the end of a
request.

Using middleware
~~~~~~~~~~~~~~~~

The way you choose to activate a given language will depend on your exact setup.

``django-ftl`` comes with a few middleware that may help you automatically
activate a locale for every request.

If you were using Django's built-in i18n solution previously, or are still using
it for some parts of your app, you may also be using
`django.middleware.locale.LocaleMiddleware
<https://docs.djangoproject.com/en/stable/ref/middleware/#django.middleware.locale.LocaleMiddleware>`_.
If that is the case, and if you want to continue using ``LocaleMiddleware``, the
easiest solution is to add
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
activates that language for django-ftl.

Instead of these two, you could also use
``"django_ftl.middleware.activate_from_request_session"`` by adding it to your
``MIDDLEWARE`` (somewhere after the session middleware). This middleware looks
for a language set in ``request.session``, as set by the ``set_language`` view
that Django provides (see `set_language docs
<https://docs.djangoproject.com/en/stable/topics/i18n/translation/#set-language-redirect-view>`_),
and uses this value, falling back to ``settings.LANGUAGE_CODE`` if it is not
found. It also sets ``request.LANGUAGE_CODE`` to the same value, similar to how
``django.middleware.locale.LocaleMiddleware`` behaves.

Both of these provided middleware use ``override`` to set the locale, not
``activate``, as per the advice above, for better request and test isolation.

You are not limited to these middleware, or to using Django's ``set_language``
view — these are provided as shortcuts and examples. In some cases it will be
best to write your own, using the `middleware source code
<https://github.com/django-ftl/django-ftl/blob/master/src/django_ftl/middleware.py>`_
as a starting point.

Outside of the request-response cycle
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you need to generate localized text from code running outside of the
request-response cycle (e.g. cron jobs or asynchronous tasks), you will not be
able to use middleware, and will need some other way to determine the locale
to use. This might involve:

* a field on a model (e.g. ``User`` class) to store the locale preference.
* for asynchronous tasks such as Celery, you could pass the locale as an
  argument. For Celery, signals such as `task-prerun
  <http://docs.celeryproject.org/en/latest/userguide/signals.html#task-prerun>`_
  might be useful.

Once you have determined the locale you need, use :func:`django_ftl.activate` or
:func:`django_ftl.override` to activate it.

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
   'Hello, \u2068boaty mcboatface\u2069'

The ``\u2068`` and ``\u2069`` characters are `unicode bidi isolation characters
<https://www.w3.org/International/questions/qa-bidi-unicode-controls>`_ that are
inserted by Fluent to ensure that the layout of text behaves correctly in case
substitutions are in a different script to the surrounding text.

That's it for the basic case. See :meth:`~django_ftl.bundles.Bundle.format` for
further info about passing numbers and datetimes, and about how errors are
handled.

Lazy translations
~~~~~~~~~~~~~~~~~

Sometimes you need to translate a string lazily. This happens when you have a
string that is defined at module load time (see the Django `lazy translation
docs
<https://docs.djangoproject.com/en/stable/topics/i18n/translation/#lazy-translation>`_
for more info). For this situation, you can use
:meth:`~django_ftl.bundles.Bundle.format_lazy` instead of ``format``. It takes
the same parameters, but doesn't generate the translation until the value is
used in a string context, such as in template rendering.

For example, the ``verbose_name`` and ``help_text`` attributes of a model field
could be done this way:

.. code-block:: python

   from django.db import models
   from myapp.ftl_bundles import main as ftl_bundle

   class Kitten(models.Model):
       name = models.CharField(
           ftl_bundle.format_lazy('kitten-name'),
           help_text=ftl_bundle.format_lazy('kitten-name.help-text'))


::

   # kittens.ftl

   kitten-name = name
       .help-text = Use most recent name if there have been are multiple.

Note that here we have used `attributes
<https://projectfluent.org/fluent/guide/attributes.html>`_ to combine the two
related pieces of text into a single message

If you do not use ``format_lazy``, then the ``verbose_name`` and ``help_text``
attributes will end up always having the text translated into the default
language.

As a more effective way to prevent this from happening, you can also pass
``require_activate=True`` parameter to :class:`~django_ftl.bundles.Bundle`. As
long as there is no ``activate`` call at module level in your project, this will
cause the ``Bundle`` to raise an exception if you attempt to use the ``format``
method at module level.

.. note::

   If you pass ``require_activate=True``, you may have trouble with some
   features like Django migrations which will attempt to serialize model
   and field definitions, which forces lazy strings to be evaluated.

   You can work around this problem by putting the following code in
   your ``ftl_bundles.py`` files:

   .. code-block:: python

      import sys
      import os.path
      from django_ftl import activate

      if any(os.path.split(arg)[-1] == 'manage.py' for arg in sys.argv) and 'makemigrations' in sys.argv:
          activate('en')



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

Put ``{% load ftl %}`` at the top of your template to load the template tag
library. It provides 3 template tags, at least one of which you will need:

``ftlconf``
~~~~~~~~~~~

This is used to set up the configuration needed by ``ftlmsg``, namely the
``bundle`` to be used. It should be used once near the top of a template (before
any translations are needed), and should be used in the situation where most of
the template will use the same bundle. For setting the configuration for just
part of a template, use ``withftl``.

The ``bundle`` argument is either a bundle object (passed in via the template
context), or a string that is a dotted path to a bundle.

(An optional ``mode`` may also be passed, which is currently limited to a single
string value ``'server'`` which is also the default value, so it is currently
not very useful! In the future further options may be added, mainly with the
idea of enabling client-side rendering of the messages.)

Example:

.. code-block:: html+django

   {% load ftl %}
   {% ftlconf bundle='myapp.ftl_bundles.main' %}


Example where we pass in the bundle object from the view:


.. code-block:: python

   # myapp.views

   from myapp.ftl_bundles import main as main_bundle

   def my_view(request):
       # ...
       return render(request, 'myapp/mypage.html',
                     {'ftl_bundle': main_bundle})

.. code-block:: html+django

   {# myapp/events.html #}

   {% load ftl %}
   {% ftlconf bundle=ftl_bundle %}


``withftl``
~~~~~~~~~~~

``withftl`` is similar to ``ftlconf`` in that its purpose is to set
configuration data for generating messages. It differs in that:

1. It sets the data only for the contained template nodes, up to a closing
   ``endwithftl`` node, which is required.

2. It also takes a ``language`` parameter that can be used to override the
   language, in addition to the ``bundle`` and ``mode`` parameters that
   ``ftlconf`` take. This should be a string in BCP 47 format.

Multiple nested ``withftl`` tags can be used, and they can be nested into a
template that has ``ftlconf`` at the top, and their scope will be limited to the
contained template nodes as you would expect.

Example:

.. code-block:: html+django

   {% load ftl %}

   {% withftl bundle='myapp.ftl_bundles.main' %}
      {% ftlmsg 'events-title' %}
   {% endwithftl %}

   {% withftl bundle='myapp.ftl_bundles.other' language='fr' %}
      {% ftlmsg 'other-message' %}
   {% endwithftl %}


As with ``ftlconf``, the parameters do not have to be just literal strings, they
can refer to values in the context as most template tags can. You must supply
one or more of ``mode``, ``bundle`` or ``language``.

``ftlmsg``
~~~~~~~~~~

Finally, to actually render a message, you need to use ``ftlmsg``. It takes one
required parameter, the message ID, and any number of keyword arguments, which
correspond to the parameters you would pass in the arguments dictionary when
calling :meth:`~django_ftl.bundles.Bundle.format` in Python code.

Example:

.. code-block:: html+django

   {% load ftl %}
   {% ftlconf bundle='myapp.ftl_bundles.main' %}

   <body>
      <h1>{% ftlmsg 'events-title' %}</h1>

      <p>{% ftlmsg 'events-greeting' username=request.user.username %}</p>
   </body>

Alternative configuration
~~~~~~~~~~~~~~~~~~~~~~~~~

In some cases, use of ``ftlconf`` or ``withftl`` in templates can be tedious and
you may want to specify configuration of mode/bundle using a more global method.

An alternative is to set some configuration variables in the template context.
You can do this using some manual method, or using a context processor. The
variables you need to set are given by the constants below:

* ``django_ftl.templatetags.ftl.MODE_VAR_NAME`` for mode.
* ``django_ftl.templatetags.ftl.BUNDLE_VAR_NAME`` for the bundle.


For example, the following is a context processor that will return the required
configuration for the ``ftlmsg`` template tag.


.. code-block:: python

   import django_ftl.templatetags.ftl

   from my_app.ftl_bundles import main

   def ftl(request):
       return {
           django_ftl.templatetags.ftl.MODE_VAR_NAME: 'server',
           django_ftl.templatetags.ftl.BUNDLE_VAR_NAME: main,
       }


This could be configured to be used always via your ``TEMPLATES``
`context_processors
<https://docs.djangoproject.com/en/stable/topics/templates/#django.template.backends.django.DjangoTemplates>`_
setting, or invoked manually and merged into a context dictionary.


HTML escaping
-------------

If your messages are plain text, and you use Django templates, then messages
will be HTML-escaped by `Django’s automatic escaping mechanism
<https://docs.djangoproject.com/en/stable/ref/templates/language/#automatic-html-escaping>`_
as normal, as there is nothing more to worry about. If you need to include HTML
fragments in the messages (e.g. to make some text bold or into a link), read on.

django-ftl plugs in to ``fluent_compiler``'s escaping mechanism and provides an
escaper out of the box that allows you to handle HTML embedded in your messages.
To use it, give your message IDs the suffix ``-html``. For example::

   welcome-message-html = Welcome { $name }, you look <i>wonderful</i> today.

In this example, ``$name`` will have HTML escaping applied as you expect and
need, while the ``<i>wonderful</i>`` markup will be left as it is. The whole
message will be returned as a Django ``SafeText`` instance so that further HTML
escaping will not be applied.

It is recommended not to use ``-html`` unless you need it, because that will
limit the use of a message to HTML contexts, and it also requires translators to
write correct HTML (for example, with ampersands written as ``&amp;``).

Note that there are rules regarding how messages with different escapers can be
used. For example::

  -brand = Ali & Alisha's ice cream

  -brand-html = Ali &amp; Alisha's <b>cool</b> ice cream

The ``-brand`` term can be used from any other message, and from a ``…-html``
message it will be correctly escaped. The ``-brand-html`` term, however, can
only be used from other ``…-html`` messages.

Template considerations
-----------------------

A very common mistake in i18n is forgetting to set the ``lang`` tag on HTML
content. In the normal case, each base template that contains an ``<html>`` tag
needs to be modified to add the ``lang`` attribute - assuming you've used
middleware as described above this could be as simple as:


.. code-block:: html+django

   <html lang="{{ request.LANGUAGE_CODE }}">

See `w3c docs on the lang attribute
<https://www.w3.org/International/questions/qa-html-language-declarations>`_ for
more information.

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


Auto-reloading
--------------

By default, django-ftl loads and caches all FTL files on first usage. In
development, this can be annoying as changes are not reflected unless you
restart the development server. To solve this, django-ftl comes with an
auto-reloading mechanism for development mode. To use it, you must install
pyinotify::

    $ pip install pyinotify

By default, if you have ``DEBUG = True`` in your settings (which is normally the
case for development mode), the reloader will be used and any changes to FTL
files references from bundles will be detected and picked up immediately.

You can also control this manually with your ``FTL`` settings in
``settings.py``::

    FTL = {
        'AUTO_RELOAD_BUNDLES': True
    }

Also, you can configure this behavior via the
:class:`~django_ftl.bundles.Bundle` constructor.
