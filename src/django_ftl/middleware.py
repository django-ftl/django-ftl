from __future__ import absolute_import, print_function, unicode_literals

from django.conf import settings
from django.utils.translation import LANGUAGE_SESSION_KEY

from django_ftl import override


def activate_from_request_session(get_response):
    """
    Middleware that can be placed after django.middleware.session.SessionMiddleware,
    used in conjunction with `set_language` Django view, and uses
    request.session[LANGUAGE_SESSION_KEY] for Fluent translations.
    """
    def middleware(request):
        language_code = request.session.get(LANGUAGE_SESSION_KEY, settings.LANGUAGE_CODE)
        request.LANGUAGE_CODE = language_code
        with override(language_code):
            return get_response(request)

    return middleware


def activate_from_request_language_code(get_response):
    """
    Middleware that can be placed after django.middleware.locale.LocaleMiddleware,
    and uses the request.LANGUAGE_CODE to activate the same language
    for Fluent translations.

    Requires USE_I18N = True.
    """
    def middleware(request):
        with override(request.LANGUAGE_CODE):
            return get_response(request)

    return middleware
