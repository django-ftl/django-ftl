=====
Usage
=====

To use django-ftl in a project, add it to your `INSTALLED_APPS`:

.. code-block:: python

    INSTALLED_APPS = (
        ...
        'django_ftl.apps.DjangoFtlConfig',
        ...
    )

Add django-ftl's URL patterns:

.. code-block:: python

    from django_ftl import urls as django_ftl_urls


    urlpatterns = [
        ...
        url(r'^', include(django_ftl_urls)),
        ...
    ]
