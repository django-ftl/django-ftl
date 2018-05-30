.. currentmodule:: django_ftl.bundles


.. class:: Bundle(files, default_locale=None, require_activate=False

   Create a bundle from a list of files

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
      paths that use Bundles are setting a language first.
