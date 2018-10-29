# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

from django.shortcuts import render
from django.template.response import TemplateResponse
from django.test import override_settings
from django.utils.translation import override as dj_override

from django_ftl.bundles import NoLocaleSet

from .base import WebTestBase
from .ftl_bundles import simple_view as simple_view_bundle


def simple_view(request):
    return render(request, 'tests/simple_view.html', {})


def simple_template_response_view(request):
    return TemplateResponse(request, 'tests/simple_view.html', {})


@override_settings(
    MIDDLEWARE=[
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django_ftl.middleware.activate_from_request_session',
    ],
)
class TestActivateFromSessionMiddleware(WebTestBase):
    def test_default(self):
        self.get_url('test_middleware.simple_view')
        self.assertTextPresent("A Web Page Title")
        self.assertTextPresent("The current language code is en")

    def test_set_language(self):
        self.get_url('test_middleware.simple_view')
        self.fill({'[name=language]': 'tr'})
        self.submit('[type=submit]')
        self.assertTextPresent("Şimdiki dil kodu tr")

    def test_request_isolation(self):
        self.get_url('test_middleware.simple_view')
        self.fill({'[name=language]': 'tr'})
        self.submit('[type=submit]')

        self.assertRaises(NoLocaleSet, simple_view_bundle.format, 'simple-title')

    def test_template_response(self):
        # We are checking that the middleware mechanism that finalizes and
        # renders templates works with our use of an 'override' context manager.
        self.get_url('test_middleware.simple_view_template_response')
        self.assertTextPresent("A Web Page Title")
        self.assertTextPresent("The current language code is en")
        self.fill({'[name=language]': 'tr'})
        self.submit('[type=submit]')
        self.assertTextPresent("Şimdiki dil kodu tr")


@override_settings(
    MIDDLEWARE=[
        'django.middleware.locale.LocaleMiddleware',
        'django_ftl.middleware.activate_from_request_language_code',
    ],
)
class TestActivateFromLanguageCodeMiddleware(WebTestBase):
    def test_default(self):
        with dj_override('en'):
            self.get_url('test_middleware.simple_view_prefixed')
        self.assertTextPresent("A Web Page Title")
        self.assertTextPresent("The current language code is en")

    def test_other(self):
        with dj_override('tr'):
            self.get_url('test_middleware.simple_view_prefixed')
        self.assertTextPresent("Şimdiki dil kodu tr")

    def test_request_isolation(self):
        with dj_override('en'):
            self.get_url('test_middleware.simple_view')

        self.assertRaises(NoLocaleSet, simple_view_bundle.format, 'simple-title')

    def test_template_response(self):
        # We are checking that the middleware mechanism that finalizes and
        # renders templates works with our use of an 'override' context manager.
        with dj_override('en'):
            self.get_url('test_middleware.simple_view_template_response_prefixed')
            self.assertTextPresent("A Web Page Title")
            self.assertTextPresent("The current language code is en")
        with dj_override('tr'):
            self.get_url('test_middleware.simple_view_template_response_prefixed')
            self.assertTextPresent("Şimdiki dil kodu tr")
