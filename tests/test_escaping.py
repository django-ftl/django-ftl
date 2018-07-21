# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

import six
from django.test import TestCase
from django.utils.html import SafeText, mark_safe

from django_ftl.bundles import Bundle

text_type = six.text_type


bundle = Bundle(['tests/escaping.ftl'],
                use_isolating=False,
                default_locale='en')


class TestBundles(TestCase):
    maxDiff = None

    def test_html(self):
        val = bundle.format('my-test-item-html', {'name': 'Me & My Friends'})
        self.assertEqual(val, 'Welcome to Jack &amp; Jill. Jack &amp; Jill <i>ROCK</i> - <b>Yeah!</b>. Your name is Me &amp; My Friends.')
        self.assertEqual(type(val), SafeText)

    def test_html_mark_safe(self):
        val = bundle.format('my-test-item-html', {'name': mark_safe('<b>Me</b>')})
        self.assertEqual(val, 'Welcome to Jack &amp; Jill. Jack &amp; Jill <i>ROCK</i> - <b>Yeah!</b>. Your name is <b>Me</b>.')
        self.assertEqual(type(val), SafeText)

    def test_plain(self):
        val = bundle.format('my-test-item-plain', {'name': 'Me & My Friends'})
        self.assertEqual(val, 'Welcome to Jack & Jill. Your name is Me & My Friends.')
        self.assertEqual(type(val), text_type)
