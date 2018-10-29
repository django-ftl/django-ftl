# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

from django.conf.urls import url
from django.conf.urls.i18n import i18n_patterns
from django.views import i18n as i18n_views

from . import test_middleware

urlpatterns = [
    url(r'^set_language/$', i18n_views.set_language, name='set_language'),
    url(r'^test_middleware/simple_view/$', test_middleware.simple_view, name='test_middleware.simple_view'),
    url(r'^test_middleware/simple_view_template_response/$', test_middleware.simple_view, name='test_middleware.simple_view_template_response'),
] + i18n_patterns(
    url(r'^test_middleware/simple_view/$', test_middleware.simple_view, name='test_middleware.simple_view_prefixed'),
    url(r'^test_middleware/simple_view_template_response/$', test_middleware.simple_view, name='test_middleware.simple_view_template_response_prefixed'),
)
