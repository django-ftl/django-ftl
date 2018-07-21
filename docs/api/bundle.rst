=========
 Bundles
=========

.. currentmodule:: django_ftl.bundles

.. class:: Bundle(files, default_locale=None, require_activate=False, use_isolating=True)

   Create a bundle from a list of files.

   :param files list(str):

      Files are specified as relative paths that start from a specific locale
      directory.

      For example, if you are writing ``myapp``, and you have
      ``myapp/locales/en/myapp/main.ftl`` for English and
      ``myapp/locales/de/myapp/main.ftl`` for German, then you would pass
      ``["myapp/main.ftl"]`` which will refer to either of these files depending
      on the active language.

      If multiple paths are given, they will be added in order. This means that
      if later files contain the same message IDs as earlier files, the later
      definitions will shadow and take precedence over earlier ones.

   :param str default_locale:

      You may pass keyword argument ``default_locale`` (as a BCP47 string e.g.
      "en-US"), which will be used as a fallback if an unavailable locale is
      activated, or if a message ID is not found in the current locale. By
      default, your ``LANGUAGE_CODE`` setting will be used (see :ref:`settings`)
      if nothing is passed.

   :param bool require_activate:

      By default the ``default_locale`` will be used as a fallback if no
      language has been activated. By passing ``require_activate=True``,
      :meth:`format` will raise an exception if you attempt to use it without
      first activating a language. This can be helpful to ensure that all code
      paths that use Bundles are setting a language first, and especially for
      ensuring that all module level uses of a ``Bundle`` use
      :meth:`format_lazy` instead of :meth:`format`.

   :param bool use_isolating:

      Controls whether substitutions in messages should be surrounded with bidi
      isolation characters. Defaults to ``True``. Pass ``False`` to disable this
      (if, for example, all your text and substitutions are in scripts that go
      in the same direction).

   .. method:: format(message_id, args=None)

      Generate a translation of the message specified by the message ID,
      in the currently activated locale.

      ``args`` is an optional dictionary of parameters for the message. These
      will normally be:

      * strings
      * integers or floating point numbers (which will be formatted according to
        locale rules)
      * datetime objects (which will be formatted according to locale rules)

      To specify or partially specify your own formatting choices for numbers
      and datetime objects, see the python-fluent docs for
      ``fluent.types.fluent_number`` and ``fluent.types.fluent_datetime``.
      (TODO LINK)

      The arguments passed in may also be strings or numbers that are used to
      select variants.

   .. method:: format_lazy(message_id, args=None)

      Same as :meth:`format`, but returns an object that delays translation
      until the object is used in a string context.

      This is important when defining strings at module level which
      should be translated later, when the required locale is known.


Error handling in Bundle
========================

Fluent's philosophy is that in general, when generating translations, something
is usually better than nothing, and therefore it attempts to recover as much as
possible from error conditions. For example, if there are syntax errors in
``.ftl`` files, it will try to find as many correct messages as possible and
pass over the incorrect ones. Or, if a message is formatted but it is missing an
argument, the string ``'???'`` will be used rather than turning the whole
message into an error of some kind. At the same time, these errors should be
reported somehow.

django-ftl in general follows the same principle. This means that things like
missing ``.ftl`` files are tolerated, and most ``Bundle`` methods rarely throw
exceptions.

Instead, when errors occur they are collected and then logged. Errors found in
``.ftl`` message files, or generated at runtime due to bad arguments, for
example, will be logged at ``ERROR`` level use the stdlib logging framework, to
the ``django_ftl.message_errors`` logger. Ensure that these errors are visible
in your logs, and this should make these problems more visible to you.

If a message is missing entirely, for instance, you will get ``'???'`` returned
from ``Bundle.format`` rather than an exception (but the error will be logged).
If the message is missing from the requested locale, but available in the
default locale, the default will be used (but you will still get an error
logged). Therefore, you don't need to add ``try`` / ``except`` around calls to
``Bundle.format`` to provide a fallback, because that is done for you.

There are some places where django-ftl does throw exceptions, however. These
include:

* ``Bundle.format``: If any of the bundle's specified ``.ftl`` are missing from
  the default locale, a ``django_ftl.bundles.FileNotFoundError`` exception will
  be raised. It is assumed that such a problem with the default locale is a
  result of a typo, rather than just a locale than has not been fully translated
  yet, and so the developer is warned early. An empty ``.ftl`` file at the
  correct path is sufficient to silence this error.

* ``Bundle.format``: If ``require_activate`` is True, this method will raise a
  ``django_ftl.bundles.NoLocaleSet`` exception if you attempt to use it before
  calling ``activate``. This is a deliberate feature to help flush out
  cases where you are using :meth:`Bundle.format` before setting a locale,
  instead of :meth:`Bundle.format_lazy`.

These are deliberately intended to cause crashes, because you have a developer
error that should cause failure as early and as loudly as possible.
