.. :changelog:

History
-------

0.13 (2021-09-16)
+++++++++++++++++

* Dropped support for Python 2.7
* Added support for Django 3.2
* Added support for custom functions to the Bundle constructor
* Dropped useless mandatory configuration of ``mode`` parameter for template
  tags - it now defaults to ``'server'`` which is the only allowed option
  anyway.

0.12.1 (2020-05-09)
+++++++++++++++++++

* Fixed broken (and undocumented) ``check_all`` method.

0.12 (2020-04-02)
+++++++++++++++++

* Switch to the new APIs available in ``fluent_compiler`` 0.2.
* Performance improvements - large reduction in the percentage overhead
  introduced by django-ftl (compared to raw ``fluent_compiler`` performance).
* Undocumented ``MessageFinderBase`` class has changed slightly: its ``load``
  method now returns a ``fluent_compiler.resource.FtlResource`` object instead
  of a string. If you used a custom ``finder`` for ``Bundle`` you may need to
  update it for this change.

0.11 (2020-03-24)
+++++++++++++++++

* Switched to using ``fluent_compiler`` as backend instead of experimental branch
  in ``fluent.runtime``. This means **import changes are required**:

  * ``fluent_number`` and ``fluent_date``, if you are using them, should be
    imported from ``fluent_compiler.types`` instead of ``fluent.runtime.types``

* Added ``Bundle.check_all`` method.
* Django 3.0 support
* Dropped support for Python 3.4 (it may work, but recent versions of lxml
  do not install on it, which made running tests harder).

0.10 (2019-05-23)
+++++++++++++++++

* Upgraded to more recent version of fluent.runtime (0.1 with modifications)
* Fixed ``use_isolating`` behavior (BDI characters are now inserted for HTML messages)
* Thread-safety fixes for loading bundles.
* Corrected order of using 'locales' directories found via ``INSTALLED_APPS`` to
  be consistent with normal Django convention.


0.9.1 (2019-03-02)
++++++++++++++++++

* Changed development autoreload mechanism to not interfere with Django's
  development server autoreload.
* Bug fix for case when invalid mode is specified in template tag.
* Various fixes and improvements to middlewares (plus tests)
* Thread-safe Bundle
* Method for configuring ``ftlmsg`` via context processor.

0.9 (2018-09-10)
++++++++++++++++

* Working version
* Depends on our version of python-fluent

0.0.1 (2018-05-19)
++++++++++++++++++

* First release on PyPI - empty placeholder package
