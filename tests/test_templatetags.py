# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

import re

from django.template import Context, Template

from django_ftl import activate
from django_ftl.bundles import Bundle

from .base import TestBase

main_bundle = Bundle(['tests/main.ftl'],
                     use_isolating=False,
                     default_locale='en')

other_bundle = Bundle(['tests/other.ftl'],
                      use_isolating=False,
                      default_locale='en')


class TestFtlConfTag(TestBase):
    def setUp(self):
        activate('en')

    def test_good(self):
        t = Template("""
        {% load ftl %}
        {% ftlconf mode='server' bundle='tests.test_templatetags.main_bundle' %}
        {% ftlmsg 'simple' %}
        """)
        self.assertEqual(t.render(Context({})).strip(),
                         "Simple")

    def test_good_split(self):
        t = Template("""
        {% load ftl %}
        {% ftlconf mode='server' %}
        {% ftlconf bundle='tests.test_templatetags.main_bundle' %}
        {% ftlmsg 'simple' %}
        """)
        self.assertEqual(t.render(Context({})).strip(),
                         "Simple")

    def test_missing(self):
        t = Template("""
        {% load ftl %}
        {% ftlconf mode='server' bundle='tests.test_templatetags.main_bundle' %}
        {% ftlmsg 'missing-message' %}
        """)
        self.assertEqual(t.render(Context({})).strip(),
                         "???")

    def test_args(self):
        t = Template("""
        {% load ftl %}
        {% ftlconf mode='server' bundle='tests.test_templatetags.main_bundle' %}
        {% ftlmsg 'with-argument' user=user %}
        """)
        self.assertEqual(t.render(Context({'user': 'Mary'})).strip(),
                         "Hello to Mary.")

    def test_xss(self):
        t = Template("""
        {% load ftl %}
        {% ftlconf mode='server' bundle='tests.test_templatetags.main_bundle' %}
        {% ftlmsg 'with-argument' user=user %}
        """)
        self.assertEqual(t.render(Context({'user': 'Mary & Jane'})).strip(),
                         "Hello to Mary &amp; Jane.")


class TestWithFtlTag(TestBase):
    def setUp(self):
        activate('en')

    def test_good(self):
        t = Template("""
        {% load ftl %}
        {% withftl mode='server' bundle='tests.test_templatetags.main_bundle' %}
           {% ftlmsg 'simple' %}
        {% endwithftl %}
        """)
        self.assertEqual(t.render(Context({})).strip(),
                         "Simple")

    def test_override_bundle(self):
        t = Template("""
        {% load ftl %}
        {% ftlconf mode='server' bundle='tests.test_templatetags.main_bundle' %}
        {% ftlmsg 'simple' %}
        {% withftl bundle='tests.test_templatetags.other_bundle' %}
           {% ftlmsg 'other-message' %}
        {% endwithftl %}
        {% ftlmsg 'simple' %}
        """)
        self.assertEqual(re.split(r'\s+', t.render(Context({})).strip()),
                         ["Simple", "Other-message", "Simple"])

    def test_override_language(self):
        t = Template("""
        {% load ftl %}
        {% ftlconf mode='server' bundle='tests.test_templatetags.main_bundle' %}
        {% ftlmsg 'simple' %}
        {% withftl language='fr-FR' %}
           {% ftlmsg 'simple' %}
        {% endwithftl %}
        {% ftlmsg 'simple' %}
        """)
        self.assertEqual(re.split(r'\s+', t.render(Context({})).strip()),
                         ["Simple", "Facile", "Simple"])

    def test_override_bundle_and_language(self):
        t = Template("""
        {% load ftl %}
        {% ftlconf mode='server' bundle='tests.test_templatetags.main_bundle' %}
        {% ftlmsg 'simple' %}
        {% withftl bundle='tests.test_templatetags.other_bundle' language='tr' %}
           {% ftlmsg 'other-message' %}
        {% endwithftl %}
        {% ftlmsg 'simple' %}
        """)
        self.assertEqual(re.split(r'\s+', t.render(Context({})).strip()),
                         ["Simple", "Başka-mesaj", "Simple"])

    def test_bad_kwarg(self):
        t = """
        {% load ftl %}
        {% withftl xyz='abc' %}
           {% ftlmsg 'simple' %}
        {% endwithftl %}
        """
        self.assertRaises(ValueError, Template, t)

    def test_good_with_variables(self):
        t = Template("""
        {% load ftl %}
        {% withftl mode=my_mode bundle=my_bundle %}
           {% ftlmsg 'simple' %}
        {% endwithftl %}
        """)
        context = Context({
            'my_mode': 'server',
            'my_bundle': main_bundle,
        })
        self.assertEqual(t.render(context).strip(),
                         "Simple")

    def test_nesting(self):
        t = Template("""
        {% load ftl %}
        {% withftl mode='server' bundle='tests.test_templatetags.main_bundle' %}
          {% ftlmsg 'simple' %}
          {% withftl language='fr-FR' %}
            {% ftlmsg 'simple' %}
            {% withftl language='tr' %}
              {% ftlmsg 'simple' %}
            {% endwithftl %}
            {% ftlmsg 'simple' %}
          {% endwithftl %}
          {% ftlmsg 'simple' %}
        {% endwithftl %}
        """)
        self.assertEqual(re.split(r'\s+', t.render(Context({})).strip()),
                         ["Simple", "Facile", "Basit", "Facile", "Simple"])

    def test_withftl_bad_mode(self):
        t = Template("""
        {% load ftl %}
        {% withftl mode='xxx' bundle='tests.test_templatetags.main_bundle' %}
          {% ftlmsg 'simple' %}
        {% endwithftl %}
        """)
        self.assertRaises(ValueError, t.render, Context({}))

    def test_ftlconf_bad_mode(self):
        t = Template("""
        {% load ftl %}
        {% ftlconf mode='xxx' bundle='tests.test_templatetags.main_bundle' %}
        {% ftlmsg 'simple' %}
        """)
        self.assertRaises(ValueError, t.render, Context({}))
