from django.test import TestCase
from django_functest import FuncWebTestMixin

from django_ftl import deactivate


class TestBase(TestCase):
    def setUp(self):
        super().setUp()
        deactivate()


class WebTestBase(FuncWebTestMixin, TestBase):
    setup_auth = False
