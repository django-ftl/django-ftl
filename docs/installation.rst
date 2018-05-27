============
Installation
============

At the command line::

    $ pip install django-ftl

It's recommended to do this in a virtualenv.

At the time of writing, django-ftl requires a version of python-fluent
that is not yet released, or even merged to master. Uninstall the version
that just got installed::

    $ pip uninstall fluent

And install the bleeding edge version::


    $ pip install -e git+https://github.com/django-ftl/python-fluent@implement_format#egg=fluent
