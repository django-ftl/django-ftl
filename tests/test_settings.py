from __future__ import absolute_import, print_function, unicode_literals

from django.test import override_settings

from django_ftl.conf import get_setting

from .base import TestBase


class TestSettings(TestBase):

    def test_default_fallback(self):
        self.assertEqual(get_setting('LANGUAGE_CODE'), 'en')

    @override_settings(FTL={'LANGUAGE_CODE': 'fr'})
    def test_ftl_override(self):
        self.assertEqual(get_setting('LANGUAGE_CODE'), 'fr')

    @override_settings(FTL={'LANGUAGE_CODE': 'fr'},
                       LANGUAGE_COOKIE_NAME='xxxx')
    def test_ftl_partial_override(self):
        self.assertEqual(get_setting('LANGUAGE_COOKIE_NAME'), 'xxxx')
