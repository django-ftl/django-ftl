from __future__ import absolute_import, print_function, unicode_literals

from .bundles import activator

__version__ = '0.0.2-dev'


def activate(locale):
    activator.activate(locale)


def deactivate():
    activator.deactivate()
