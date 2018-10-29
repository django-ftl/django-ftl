# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

from django_ftl.bundles import Bundle

simple_view = Bundle(['tests/simple_view.ftl'],
                     default_locale='en',
                     use_isolating=False,
                     require_activate=True)
