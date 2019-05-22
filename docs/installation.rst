============
Installation
============

At the command line::

    $ pip install django-ftl

You can also install from latest master on GitHub.

It's recommended to do this in a virtualenv. Check the version that got
installed, and adjust instructions below accordingly.

At the time of writing, django-ftl requires a version of fluent.runtime that is
not yet released, or even merged to master. Uninstall the version that just got
installed and install our version.

For latest::

    $ pip uninstall fluent.runtime
    $ pip install -e 'git+https://github.com/django-ftl/python-fluent@django-ftl-0.11#egg=fluent.runtime&subdirectory=fluent.runtime'

For older versions of django-ftl, see below:

0.10::

    $ pip uninstall fluent.runtime
    $ pip install -e 'git+https://github.com/django-ftl/python-fluent@django-ftl-0.10#egg=fluent.runtime&subdirectory=fluent.runtime'

0.9.1 and earlier::

    $ pip uninstall fluent
    $ pip install -e git+https://github.com/django-ftl/python-fluent@django-ftl-0.9.1#egg=fluent
