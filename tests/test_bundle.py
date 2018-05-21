from __future__ import absolute_import, unicode_literals, print_function


from django.test import TestCase

from django_ftl import activate_locale, deactivate_locale
from django_ftl.bundle import Bundle, NoLocaleSet


class TestBundles(TestCase):

    def setUp(self):
        deactivate_locale()

    def test_no_locale(self):
        bundle = Bundle(['tests/main.ftl'])

        self.assertRaises(NoLocaleSet, bundle.format, 'a-message-id')

    def test_find_messages(self):
        bundle = Bundle(['tests/main.ftl'])
        activate_locale('en')
        self.assertEqual(bundle.format('simple'), "Simple")

    def test_switch_locale(self):
        activate_locale('en')
        bundle = Bundle(['tests/main.ftl'])
        self.assertEqual(bundle.format('simple'), "Simple")
        activate_locale('tr')
        self.assertEqual(bundle.format('simple'), "Basit")

    def test_fallback(self):
        activate_locale('tr')
        bundle = Bundle(['tests/main.ftl'], fallback_locale='en')
        self.assertEqual(bundle.format('missing-from-others'), "Missing from others")

    def test_missing(self):
        activate_locale('en')
        bundle = Bundle(['tests/main.ftl'], fallback_locale='en')
        self.assertEqual(bundle.format('missing-from-all'), "???")

        # TODO - check caches are actually working

    # TODO fallbacks - manual and auto

    # TODO lazy strings

    # TODO should format log errors and just return the string?
