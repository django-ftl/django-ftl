from __future__ import absolute_import, print_function, unicode_literals

from django.utils.decorators import ContextDecorator

from .bundles import activator

__version__ = '0.10'


def activate(locale):
    """
    Activate a given locale/language. Bundles will
    use this locale for translation.
    """
    activator.activate(locale)


def deactivate():
    """
    Deactivate the current locale/language. Bundles will
    fall back to the default locale (if require_activate=False)
    """
    activator.deactivate()


class override(ContextDecorator):
    def __init__(self, locale, deactivate=False):
        self.locale = locale
        self.deactivate = deactivate

    def __enter__(self):
        self.old_locale = activator.get_current_value()
        activator.activate(self.locale)

    def __exit__(self, exc_type, exc_value, traceback):
        if self.deactivate:
            activator.deactivate()
        else:
            activator.activate(self.old_locale)
