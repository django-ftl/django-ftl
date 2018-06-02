# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

# This module should not raise an exception if you try to import it

from django_ftl.bundles import Bundle

main = Bundle(['tests/main.ftl'],
              default_locale='en',
              require_activate=True)


class MyThing(object):
    my_label = main.format_lazy('simple')
