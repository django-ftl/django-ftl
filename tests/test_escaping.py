# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

import six
from django.utils.html import SafeText, mark_safe

from django_ftl.bundles import Bundle

from .base import TestBase

text_type = six.text_type


bundle = Bundle(['tests/escaping.ftl'],
                default_locale='en')


class TestBundles(TestBase):
    maxDiff = None

    def test_html(self):
        val = bundle.format('my-test-item-html', {'name': 'Me & My Friends'})
        self.assertEqual(val, 'Welcome to \u2068Jack &amp; Jill\u2069. \u2068Jack &amp; Jill <i>ROCK</i> - <b>Yeah!</b>\u2069. Your name is \u2068Me &amp; My Friends\u2069.')
        self.assertEqual(type(val), SafeText)

    def test_html_mark_safe(self):
        val = bundle.format('my-test-item-html', {'name': mark_safe('<b>Me</b>')})
        self.assertEqual(val, 'Welcome to \u2068Jack &amp; Jill\u2069. \u2068Jack &amp; Jill <i>ROCK</i> - <b>Yeah!</b>\u2069. Your name is \u2068<b>Me</b>\u2069.')
        self.assertEqual(type(val), SafeText)

    def test_plain(self):
        val = bundle.format('my-test-item-plain', {'name': 'Me & My Friends'})
        self.assertEqual(val, 'Welcome to \u2068Jack & Jill\u2069. Your name is \u2068Me & My Friends\u2069.')
        self.assertEqual(type(val), text_type)
