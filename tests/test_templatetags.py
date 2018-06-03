from __future__ import absolute_import, unicode_literals, print_function


from django.test import TestCase
from django.template import Template, Context

from django_ftl import activate
from django_ftl.bundles import Bundle


main_bundle = Bundle(['tests/main.ftl'],
                     use_isolating=False,
                     default_locale='en')


class TestFtlTag(TestCase):
    def setUp(self):
        activate('en')

    def test_good(self):
        t = Template("""
        {% load ftl %}
        {% ftl 'server' 'tests.test_templatetags.main_bundle' 'simple' %}
        """)
        self.assertEqual(t.render(Context({})).strip(),
                         "Simple")

    def test_missing(self):
        t = Template("""
        {% load ftl %}
        {% ftl 'server' 'tests.test_templatetags.main_bundle' 'missing-message' %}
        """)
        self.assertEqual(t.render(Context({})).strip(),
                         "???")

    def test_args(self):
        t = Template("""
        {% load ftl %}
        {% ftl 'server' 'tests.test_templatetags.main_bundle' 'with-argument' user=user %}
        """)
        self.assertEqual(t.render(Context({'user': 'Mary'})).strip(),
                         "Hello to Mary.")

    def test_xss(self):
        t = Template("""
        {% load ftl %}
        {% ftl 'server' 'tests.test_templatetags.main_bundle' 'with-argument' user=user %}
        """)
        self.assertEqual(t.render(Context({'user': 'Mary & Jane'})).strip(),
                         "Hello to Mary &amp; Jane.")


class TestFtlConfTag(TestCase):
    def setUp(self):
        activate('en')

    def test_good(self):
        t = Template("""
        {% load ftl %}
        {% ftl_conf mode='server' bundle='tests.test_templatetags.main_bundle' %}
        {% ftl_message 'simple' %}
        """)
        self.assertEqual(t.render(Context({})).strip(),
                         "Simple")

    def test_good_split(self):
        t = Template("""
        {% load ftl %}
        {% ftl_conf mode='server' %}
        {% ftl_conf bundle='tests.test_templatetags.main_bundle' %}
        {% ftl_message 'simple' %}
        """)
        self.assertEqual(t.render(Context({})).strip(),
                         "Simple")

    def test_missing(self):
        t = Template("""
        {% load ftl %}
        {% ftl_conf mode='server' bundle='tests.test_templatetags.main_bundle' %}
        {% ftl_message 'missing-message' %}
        """)
        self.assertEqual(t.render(Context({})).strip(),
                         "???")

    def test_args(self):
        t = Template("""
        {% load ftl %}
        {% ftl_conf mode='server' bundle='tests.test_templatetags.main_bundle' %}
        {% ftl_message 'with-argument' user=user %}
        """)
        self.assertEqual(t.render(Context({'user': 'Mary'})).strip(),
                         "Hello to Mary.")

    def test_xss(self):
        t = Template("""
        {% load ftl %}
        {% ftl_conf mode='server' bundle='tests.test_templatetags.main_bundle' %}
        {% ftl_message 'with-argument' user=user %}
        """)
        self.assertEqual(t.render(Context({'user': 'Mary & Jane'})).strip(),
                         "Hello to Mary &amp; Jane.")
