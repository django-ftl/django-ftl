# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, unicode_literals

from django_ftl import activate
from django_ftl.bundles import Bundle

from .base import TestBase

ftl_bundle = Bundle(['tests/docs.ftl'])


class TestDocs(TestBase):

    def test_usage_docs(self):
        # These tests parallel the code in the usage.rst docs
        activate('en')
        title = ftl_bundle.format('events-title')
        self.assertEqual(title, 'MyApp Events!')

        greeting = ftl_bundle.format('events-greeting', {'username': 'boaty mcboatface'})
        self.assertEqual(greeting, 'Hello, \u2068boaty mcboatface\u2069')
