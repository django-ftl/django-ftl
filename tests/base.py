# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

from django.test import TestCase
from django_functest import FuncWebTestMixin

from django_ftl import deactivate


class TestBase(TestCase):
    def setUp(self):
        super(TestBase, self).setUp()
        deactivate()


class WebTestBase(FuncWebTestMixin, TestBase):
    setup_auth = False
