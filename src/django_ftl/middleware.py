from __future__ import absolute_import, print_function, unicode_literals

from django.utils.translation import LANGUAGE_SESSION_KEY

from django_ftl import activate


def activate_from_request_session(get_response):
    """
    Middleware that can be placed after django.middleware.session.SessionMiddleware,
    used in conjunction with `set_language` Django view, and uses
    request.session[LANGUAGE_SESSION_KEY] for Fluent translations.
    """
    def middleware(request):
        if LANGUAGE_SESSION_KEY in request.session:
            language_code = request.session[LANGUAGE_SESSION_KEY]
            request.LANGUAGE_CODE = language_code
            activate(language_code)
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
        activate(request.LANGUAGE_CODE)
        return get_response(request)

    return middleware
