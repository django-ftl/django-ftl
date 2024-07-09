import logging
import os
from collections import OrderedDict
from threading import Lock, local

from babel.core import UnknownLocaleError
from django.conf import settings
from django.utils.functional import cached_property, lazy
from django.utils.html import conditional_escape as conditional_html_escape
from django.utils.html import mark_safe as mark_html_escaped
from fluent_compiler.compiler import compile_messages
from fluent_compiler.resource import FtlResource

from .conf import get_setting
from .utils import make_namespace

try:
    from functools import lru_cache
except ImportError:
    # Older versions of Django have an implementation we can use
    from django.utils.lru_cache import lru_cache

try:
    from django.utils.html import SafeText as SafeString
except ImportError:
    from django.utils.html import SafeString


_active_locale = local()

ftl_logger = logging.getLogger("django_ftl.message_errors")


class NoLocaleSet(AssertionError):
    pass


def get_app_locale_dirs():
    from django.apps import apps

    dirs = []
    for app_config in apps.get_app_configs():
        if not app_config.path:
            continue
        locales_dir = os.path.join(app_config.path, "locales")
        if os.path.isdir(locales_dir):
            dirs.append(locales_dir)
    return dirs


class FileNotFoundError(RuntimeError):
    pass


class MessageFinderBase:
    @property
    def locale_base_dirs(self):
        raise NotImplementedError()

    def load(self, locale, path, reloader=None):
        locale = normalize_bcp47(locale)
        all_bases = self.locale_base_dirs
        resources = []
        tried = []
        for i, base in enumerate(all_bases):
            try:
                locale_dir = locale_dirs_at_path(base)[locale]
            except KeyError:
                tried.append(base + "/")
                continue

            full_path = os.path.join(locale_dir, path)
            if os.path.exists(full_path):
                if reloader is not None:
                    reloader.add_watched_path(full_path)
                resources.append(FtlResource.from_file(full_path))
            else:
                tried.append(full_path)

        if not resources:
            raise FileNotFoundError(
                f"Could not find locate FTL file {locale}/{path}. Tried: {', '.join(tried)}"
            )

        return resources


def normalize_bcp47(locale):
    return locale.lower().replace("_", "-")


@lru_cache(maxsize=None)
def locale_dirs_at_path(base):
    dirs_found = [
        p for p in [os.path.join(base, e) for e in os.listdir(base)] if os.path.isdir(p)
    ]

    # Apply normalization and return mapping from locale nane to directory.
    return {normalize_bcp47(os.path.basename(p)): p for p in dirs_found}


class DjangoMessageFinder(MessageFinderBase):
    @cached_property
    def locale_base_dirs(self):
        return get_app_locale_dirs()


default_finder = DjangoMessageFinder()


class LanguageActivator:
    def activate(self, locale):
        old_value = self.get_current_value()
        if old_value == locale:
            return
        _active_locale.value = locale

    def deactivate(self):
        self.activate(None)

    def get_current_value(self):
        return getattr(_active_locale, "value", None)


activator = LanguageActivator()


html_escaper = make_namespace(
    name="django_html_escaper",
    select=lambda message_id=None, **hints: message_id.endswith("-html"),
    output_type=SafeString,
    mark_escaped=mark_html_escaped,
    escape=conditional_html_escape,
    join=lambda parts: mark_html_escaped(
        "".join(conditional_html_escape(p) for p in parts)
    ),
    use_isolating=False,
)


class Bundle:
    def __init__(
        self,
        paths,
        default_locale=None,
        use_isolating=True,
        require_activate=False,
        auto_reload=None,
        finder=default_finder,
        functions=None,
    ):

        self._paths = paths
        self._finder = finder
        self._default_locale = default_locale
        self._use_isolating = use_isolating
        self._require_activate = require_activate
        self._lock = Lock()
        self._functions = functions or {}

        if auto_reload is None:
            auto_reload = get_setting("AUTO_RELOAD_BUNDLES", None)

        if auto_reload is None:
            if settings.DEBUG:
                try:
                    import pyinotify  # noqa
                except ImportError:
                    ftl_logger.warning(
                        "Not using django_ftl autoreloader because pyinotify is not installed. Set `Bundle.auto_reload` or `AUTO_RELOAD_BUNDLES` to `False` to disable this warning."
                    )
                else:
                    auto_reload = True

        if auto_reload:
            # import at this point to avoid importing pyinotify if we don't need it.
            from .autoreload import create_bundle_reloader

            self._reloader = create_bundle_reloader(self)
        else:
            self._reloader = None
        self.reload()

    def reload(self):
        with self._lock:
            self._message_function_cache = {}
            self._compiled_unit_for_locale = {}

    def _get_default_locale(self):
        default_locale = self._default_locale
        if default_locale is not None:
            return default_locale

        return get_setting("LANGUAGE_CODE")

    def get_compiled_unit_for_locale_list(self, locales):
        for locale in locales:
            try:
                unit = self.get_compiled_unit_for_locale(locale)
            except UnknownLocaleError:
                continue
            yield unit

    def get_compiled_unit_for_locale(self, locale):
        try:
            return self._compiled_unit_for_locale[locale]
        except KeyError:
            pass

        # Fill out _compiled_unit_for_locale
        # necessary, but do this synchronized for all threads.
        with self._lock:
            # Double checked locking pattern.
            try:
                return self._compiled_unit_for_locale[locale]
            except KeyError:
                pass

            # Do the compilation:
            resources = []
            for path in self._paths:
                try:
                    resources += self._finder.load(
                        locale, path, reloader=self._reloader
                    )
                except FileNotFoundError:
                    if locale == self._get_default_locale():
                        # Can't find any FTL with the specified filename, we
                        # want to bail early and alert developer.
                        raise
                    # Allow missing files otherwise

            unit = compile_messages(
                locale,
                resources,
                use_isolating=self._use_isolating,
                escapers=[html_escaper],
                functions=self._functions,
            )
            errors = unit.errors
            for msg_id, error in errors:
                self._log_error(locale, msg_id, {}, error)
            self._compiled_unit_for_locale[locale] = unit
            return unit

    def format(self, message_id, args=None):
        # This is the hot path for performance, so we try to optimise,
        # especially the 'happy path' which will hit caches.

        # FAST PATH:
        # Avoid Activator.get_current_value() here because it adds measurable
        # overhead.
        current_locale = getattr(_active_locale, "value", None)
        errors = []
        try:
            func = self._message_function_cache[current_locale, message_id]
        except KeyError:
            # SLOW PATH:
            if current_locale is None:
                if self._require_activate:
                    raise NoLocaleSet(
                        "activate() must be used before using Bundle.format "
                        "- or, use Bundle(require_activate=False)"
                    )

            # current_locale can be `None`, and we will create cache entries
            # against (None, message_id). This gives us small performance
            # improvement by moving `if current_locale is None` check out of the
            # hot path.
            locale_to_use = current_locale or self._get_default_locale()
            to_try = list(locale_lookups(locale_to_use))
            default_locale = self._get_default_locale()
            if default_locale is not None:
                to_try = uniquify(to_try + [default_locale])

            func = None
            for unit in self.get_compiled_unit_for_locale_list(to_try):
                try:
                    func = unit.message_functions[message_id]
                    break
                except LookupError as e:
                    self._log_error(unit.locale, message_id, args, e)
                    continue
            if func is None:
                func = _missing_message
            self._message_function_cache[current_locale, message_id] = func
            # SLOW PATH END

        value = func(args, errors)
        if errors:
            for e in errors:
                self._log_error(current_locale, message_id, args, e)
        return value

    format_lazy = lazy(format, str)

    def _log_error(self, locale, message_id, args, exception):
        ftl_logger.error(
            "FTL exception for locale [%s], message '%s', args %r: %s",
            locale,
            message_id,
            args,
            repr(exception),
        )

    def check_all(self, locales):
        errors = []
        for l in locales:
            unit = self.get_compiled_unit_for_locale(l)
            errors.extend(unit.errors)
        return errors


def _missing_message(args, errors):
    return "???"


def locale_lookups(locale):
    """
    Utility for implementing RFC 4647 lookup algorithm
    """
    if "," in locale:
        locales = [l.strip() for l in locale.split(",")]
        return uniquify(sum(map(locale_lookups, locales), []))

    parts = locale.split("-")
    locales = []
    current = None
    for p in parts:
        if current is None:
            current = p
            locales.append(current)
        else:
            current = current + "-" + p
            if len(p) == 1:
                # Skip single letter/digit bits
                continue
            locales.append(current)

    return list(reversed(locales))


def uniquify(l):
    return list(OrderedDict.fromkeys(l))
