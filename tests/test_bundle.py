# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

import threading
import time

import six
from django.test import override_settings
from django.utils.encoding import force_text

from django_ftl import activate, deactivate, override
from django_ftl.bundles import Bundle, FileNotFoundError, NoLocaleSet, locale_lookups

from .base import TestBase

text_type = six.text_type


class TestBundles(TestBase):
    def test_no_locale_set_with_require_activate(self):
        bundle = Bundle(['tests/main.ftl'],
                        default_locale='en',
                        require_activate=True)
        self.assertRaises(NoLocaleSet, bundle.format, 'simple')

    def test_require_activate_after_activate(self):
        bundle = Bundle(['tests/main.ftl'],
                        default_locale='en',
                        require_activate=True)
        activate('en')
        self.assertEqual(bundle.format('simple'), 'Simple')
        deactivate()
        self.assertRaises(NoLocaleSet, bundle.format, 'simple')

    def test_no_locale_set_with_default_set(self):
        bundle = Bundle(['tests/main.ftl'],
                        require_activate=True,
                        default_locale='en')
        self.assertRaises(NoLocaleSet, bundle.format, 'simple')

    def test_no_locale_set_with_good_default(self):
        bundle = Bundle(['tests/main.ftl'],
                        default_locale='en')
        self.assertEqual(bundle.format('simple'), 'Simple')

    @override_settings(FTL={'LANGUAGE_CODE': 'en'})
    def test_no_locale_set_with_good_default_from_settings(self):
        bundle = Bundle(['tests/main.ftl'])
        self.assertEqual(bundle.format('simple'), 'Simple')

    @override_settings(FTL={'LANGUAGE_CODE': 'zh'})
    def test_no_locale_set_with_missing_default(self):
        bundle = Bundle(['tests/main.ftl'])
        self.assertRaises(FileNotFoundError, bundle.format, 'simple')

    def test_default_locale_lazy(self):
        # Ensure that bundle is retrieving LANGUAGE_CODE lazily. (The only real
        # reason for this at the moment is to make testing easier).
        bundle = Bundle(['tests/main.ftl'])
        with override_settings(LANGUAGE_CODE='fr-FR'):
            self.assertEqual(bundle.format('simple'), 'Facile')

    def test_find_messages(self):
        bundle = Bundle(['tests/main.ftl'])
        activate('en')
        self.assertEqual(bundle.format('simple'), "Simple")

    def test_load_multiple_with_some_missing(self):
        bundle = Bundle(['tests/only_in_en.ftl',
                         'tests/main.ftl'],
                        default_locale='en')
        activate('fr-FR')
        self.assertEqual(bundle.format('simple'), "Facile")

    def test_switch_locale(self):
        bundle = Bundle(['tests/main.ftl'], default_locale='en')
        self.assertEqual(bundle.format('simple'), "Simple")
        activate('tr')
        self.assertEqual(bundle.format('simple'), "Basit")
        deactivate()
        self.assertEqual(bundle.format('simple'), "Simple")

    def test_override(self):
        bundle = Bundle(['tests/main.ftl'], default_locale='en')
        self.assertEqual(bundle.format('simple'), "Simple")
        with override('tr'):
            self.assertEqual(bundle.format('simple'), "Basit")
            with override('fr-FR'):
                self.assertEqual(bundle.format('simple'), "Facile")
            self.assertEqual(bundle.format('simple'), "Basit")
        self.assertEqual(bundle.format('simple'), "Simple")

    def test_fallback(self):
        activate('tr')
        bundle = Bundle(['tests/main.ftl'], default_locale='en')
        self.assertEqual(bundle.format('missing-from-others'), "Missing from others")

    def test_missing(self):
        activate('en')
        bundle = Bundle(['tests/main.ftl'], default_locale='en')
        self.assertEqual(bundle.format('missing-from-all'), "???")

    def test_locale_matching_case_insensitive(self):
        activate('fr-fr')
        bundle = Bundle(['tests/main.ftl'], default_locale='en')
        self.assertEqual(bundle.format('simple'), 'Facile')

        activate('EN')
        bundle = Bundle(['tests/main.ftl'], default_locale='en')
        self.assertEqual(bundle.format('simple'), 'Simple')

    def test_handle_underscores_in_locale_name(self):
        activate('fr_FR')
        bundle = Bundle(['tests/main.ftl'], default_locale='en')
        self.assertEqual(bundle.format('simple'), 'Facile')

    def test_locale_matching_for_default_locale(self):
        activate('zh')
        bundle = Bundle(['tests/main.ftl'], default_locale='EN')  # 'EN' not 'en'
        self.assertEqual(bundle.format('simple'), 'Simple')

    def test_locale_range_lookup(self):
        # en-US does not exist, but 'en' does and should be found
        activate('en-US')
        bundle = Bundle(['tests/main.ftl'], default_locale='en')
        self.assertEqual(bundle.format('simple'), 'Simple')

    def test_locale_range_lookup_missing(self):
        # There is no fr or fr-XY (only fr-FR), neither of these should fallback
        # to fr-FR
        activate('fr')
        bundle = Bundle(['tests/main.ftl'], default_locale='en')
        self.assertEqual(bundle.format('simple'), 'Simple')

        activate('fr-XY')
        bundle = Bundle(['tests/main.ftl'])
        self.assertEqual(bundle.format('simple'), 'Simple')

    def test_locale_range_lookup_list(self):
        # fr-XY doesn't exist, fr-FR does
        activate('fr-XY, fr-FR')
        bundle = Bundle(['tests/main.ftl'], default_locale='en')
        self.assertEqual(bundle.format('simple'), 'Facile')

        # en-GB doesn't exist, en does
        activate('en-GB, en')
        bundle = Bundle(['tests/main.ftl'], default_locale='en')
        self.assertEqual(bundle.format('simple'), 'Simple')

    def test_missing_ftl_file(self):
        activate('en')
        bundle = Bundle(['tests/non-existant.ftl'], default_locale='en')
        self.assertRaises(FileNotFoundError, bundle.format, 'simple')

    def test_number_formatting(self):
        bundle = Bundle(['tests/main.ftl'], default_locale='en')
        self.assertEqual(bundle.format('with-number-argument', {'points': 1234567}),
                         'Score: \u20681,234,567\u2069')
        activate('fr-FR')
        self.assertEqual(bundle.format('with-number-argument', {'points': 1234567}),
                         'Points: \u20681\xa0234\xa0567\u2069')
        deactivate()
        self.assertEqual(bundle.format('with-number-argument', {'points': 1234567}),
                         'Score: \u20681,234,567\u2069')

    def test_number_formatting_for_fallback(self):
        # When we fall back to a default, number formatting
        # should be consistent with the language.
        # German locale: 1.234.567
        # System locale  (would probably be 'en',): 1,234,567
        # French locale: 1 234 567⁩

        bundle = Bundle(['tests/main.ftl'], default_locale='fr-FR')
        activate('de')
        # Should get French words and formatting
        self.assertEqual(bundle.format('with-number-argument', {'points': 1234567}),
                         'Points: \u20681\xa0234\xa0567\u2069')

    # TODO - check caches are actually working

    def test_lazy(self):
        bundle = Bundle(['tests/main.ftl'], default_locale='en')

        l = bundle.format_lazy('simple')
        self.assertEqual(force_text(l), 'Simple')
        activate('fr-FR')
        self.assertEqual(force_text(l), 'Facile')
        deactivate()
        self.assertEqual(force_text(l), 'Simple')

    def test_lazy_with_require_activate(self):
        bundle = Bundle(['tests/main.ftl'],
                        default_locale='en',
                        require_activate=True)
        self.assertRaises(NoLocaleSet, bundle.format, 'simple')
        msg = bundle.format_lazy('simple')

        self.assertRaises(NoLocaleSet, force_text, msg)

        activate('en')
        self.assertEqual(force_text(msg), 'Simple')
        activate('fr-FR')
        self.assertEqual(force_text(msg), 'Facile')

    def test_prevent_module_level_format(self):
        try:
            import tests.prevent_module_level_format  # noqa
        except NoLocaleSet:
            pass
        else:
            self.fail("Expected NoLocaleSet error")

    def test_allow_module_level_format_lazy(self):
        import tests.allow_module_level_format_lazy
        self.assertRaises(NoLocaleSet,
                          text_type,
                          tests.allow_module_level_format_lazy.MyThing.my_label)
        activate('fr-FR')
        self.assertEqual(force_text(tests.allow_module_level_format_lazy.MyThing.my_label),
                         'Facile')

    def test_use_isolating(self):
        bundle_1 = Bundle(['tests/main.ftl'], default_locale='en')
        self.assertEqual(bundle_1.format('with-argument', {'user': 'Horace'}),
                         'Hello to \u2068Horace\u2069.')

        bundle_2 = Bundle(['tests/main.ftl'], default_locale='en', use_isolating=False)
        self.assertEqual(bundle_2.format('with-argument', {'user': 'Horace'}),
                         'Hello to Horace.')


class TestLocaleLookups(TestBase):
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


class TestBundleThreadSafe(TestBase):
    def test_two_threads(self):
        # Not a proof, but a demonstration that a single Bundle can handle
        # threads with different locale values without getting confused.

        bundle = Bundle(['tests/main.ftl'],
                        default_locale='en',
                        require_activate=True)
        lock = threading.Lock()

        output = []

        # Primitive coordination mechanism to ensure we
        # are getting interleaving.
        def wait_until_output(length):
            while True:
                with lock:
                    if len(output) < length:
                        time.sleep(0)
                    else:
                        return

        def thread_1():
            with lock:
                activate('en')
                output.append((1, bundle.format('simple')))
            wait_until_output(2)
            with lock:
                # Should still be in English,
                output.append((1, bundle.format('simple')))

        def thread_2():
            # Make sure thread_1 goes first:
            wait_until_output(1)
            with lock:
                activate('fr-FR')
                output.append((2, bundle.format('simple')))
            wait_until_output(3)
            with lock:
                # Should still be French
                output.append((2, bundle.format('simple')))
                activate('en')
                # Should allow switching
                output.append((2, bundle.format('simple')))

        t1 = threading.Thread(target=thread_1)
        t2 = threading.Thread(target=thread_2)
        t1.start()
        t2.start()
        t1.join()
        t2.join()

        self.assertEqual(output,
                         [
                             (1, 'Simple'),
                             (2, 'Facile'),
                             (1, 'Simple'),
                             (2, 'Facile'),
                             (2, 'Simple'),
                         ])
