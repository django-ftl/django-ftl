.. currentmodule:: django_ftl.bundles


.. class:: Bundle(files, fallback_locale=None)

   Create a bundle from a list of files, which are specified as relative paths that
   start from a specific locale directory.

   For example, if you are writing ``myapp``, and you have
   ``myapp/locales/en/myapp/main.ftl`` for English and
   ``myapp/locales/de/myapp/main.ftl`` for German, then you would pass
   ``myapp/main.ftl`` which will refer to either of these files depending on the
   active language.

   You may pass keyword argument ``fallback_locale`` (as a BCP47 string e.g.
   "en-US"), which will be used as a default locale if an unavailable locale is
   activated. This should be the default language of your site.
