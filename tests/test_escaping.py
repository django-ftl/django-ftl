# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

from django.utils.html import mark_safe

from django_ftl.bundles import Bundle

from .base import TestBase

try:
    from django.utils.html import SafeText as SafeString
except ImportError:
    from django.utils.html import SafeString


bundle = Bundle(['tests/escaping.ftl'],
                default_locale='en')


class TestBundles(TestBase):
    maxDiff = None

    def test_html(self):
        val = bundle.format('my-test-item-html', {'name': 'Me & My Friends'})
        self.assertEqual(val, 'Welcome to Jack &amp; Jill. Jack &amp; Jill <i>ROCK</i> - <b>Yeah!</b>. Your name is Me &amp; My Friends.')
        self.assertEqual(type(val), SafeString)

    def test_html_mark_safe(self):
        val = bundle.format('my-test-item-html', {'name': mark_safe('<b>Me</b>')})
        self.assertEqual(val, 'Welcome to Jack &amp; Jill. Jack &amp; Jill <i>ROCK</i> - <b>Yeah!</b>. Your name is <b>Me</b>.')
        self.assertEqual(type(val), SafeString)

    def test_plain(self):
        val = bundle.format('my-test-item-plain', {'name': 'Me & My Friends'})
        self.assertEqual(val, 'Welcome to \u2068Jack & Jill\u2069. Your name is \u2068Me & My Friends\u2069.')
        self.assertEqual(type(val), str)

    def test_isolating(self):
        # We need use_isolating=False otherwise the link won't work
        val = bundle.format('link-html', {'url': 'http://example.com'})
        self.assertEqual(val, 'This is <a href="http://example.com">a link</a>')
