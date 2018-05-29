from __future__ import absolute_import, unicode_literals, print_function


from django.test import TestCase

from django_ftl import activate_locale, deactivate_locale
from django_ftl.bundles import Bundle, NoLocaleSet, FileNotFoundError, locale_lookups


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

    def test_locale_matching_case_insensitive(self):
        activate_locale('fr-fr')
        bundle = Bundle(['tests/main.ftl'])
        self.assertEqual(bundle.format('simple'), 'Facile')

        activate_locale('EN')
        bundle = Bundle(['tests/main.ftl'])
        self.assertEqual(bundle.format('simple'), 'Simple')

    def test_handle_underscores_in_locale_name(self):
        activate_locale('fr_FR')
        bundle = Bundle(['tests/main.ftl'])
        self.assertEqual(bundle.format('simple'), 'Facile')

    def test_normalization_for_fallback_locale(self):
        activate_locale('zh')
        bundle = Bundle(['tests/main.ftl'], fallback_locale='EN')
        self.assertEqual(bundle.format('simple'), 'Simple')

    def test_locale_range_lookup(self):
        # en-US does not exist, but 'en' does and should be found
        activate_locale('en-US')
        bundle = Bundle(['tests/main.ftl'])
        self.assertEqual(bundle.format('simple'), 'Simple')

    def test_locale_range_lookup_missing(self):
        # There is no fr or fr-XY (only fr-FR), neither of these should fallback
        # to fr-FR
        activate_locale('fr')
        bundle = Bundle(['tests/main.ftl'])
        self.assertRaises(FileNotFoundError, bundle.format, 'simple')

        activate_locale('fr-XY')
        bundle = Bundle(['tests/main.ftl'])
        self.assertRaises(FileNotFoundError, bundle.format, 'simple')

    def test_locale_range_lookup_list(self):
        # fr-XY doesn't exist, fr-FR does
        activate_locale('fr-XY, fr-FR')
        bundle = Bundle(['tests/main.ftl'])
        self.assertEqual(bundle.format('simple'), 'Facile')

        # en-GB doesn't exist, en does
        activate_locale('en-GB, en')
        bundle = Bundle(['tests/main.ftl'])
        self.assertEqual(bundle.format('simple'), 'Simple')

    def test_missing_ftl_file(self):
        activate_locale('en')
        bundle = Bundle(['tests/non-existant.ftl'])
        self.assertRaises(FileNotFoundError, bundle.format, 'simple')

    # TODO - check caches are actually working

    # TODO lazy strings


class TestLocaleLookups(TestCase):
    # See https://tools.ietf.org/html/rfc4647#section-3.4

    def test_language(self):
        self.assertEqual(list(locale_lookups("en")),
                         ["en"])

    def test_language_and_region(self):
        self.assertEqual(list(locale_lookups("en-US")),
                         ["en-US", "en"])

    def test_extra_subtags(self):
        self.assertEqual(list(locale_lookups("zh-Hant-CN-x-private1-private2")),
                         ["zh-Hant-CN-x-private1-private2",
                          "zh-Hant-CN-x-private1",
                          "zh-Hant-CN",
                          "zh-Hant",
                          "zh"])

    def test_list(self):
        self.assertEqual(list(locale_lookups("en-US, fr-FR")),
                         ["en-US", "en", "fr-FR", "fr"])

    def test_eliminates_dupes(self):
        # This would be en-GB, en, en without dupe elimination
        self.assertEqual(list(locale_lookups("en-GB, en")),
                         ["en-GB",
                          "en"])
