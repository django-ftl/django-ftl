from __future__ import absolute_import, print_function, unicode_literals

from django.conf import settings
try:
    from django.utils.translation import LANGUAGE_SESSION_KEY
except ImportError:
    LANGUAGE_SESSION_KEY = None

try:
    from django.utils.translation import get_language_from_request
except ImportError:
    get_language_from_request = None

from django_ftl import override


def activate_from_request_session(get_response):
    """
    Middleware that can be placed after django.middleware.session.SessionMiddleware,
    used in conjunction with `set_language` Django view.
    Internally uses request.session and/or cookies for Fluent translations.
    """
    def middleware(request):
        if LANGUAGE_SESSION_KEY is not None:
            # Django < 4
            language_code = request.session.get(LANGUAGE_SESSION_KEY, settings.LANGUAGE_CODE)
        else:
            language_code = get_language_from_request(request)
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
