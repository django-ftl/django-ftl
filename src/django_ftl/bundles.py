from __future__ import absolute_import, print_function, unicode_literals

import logging
import os
from collections import OrderedDict
from threading import Lock, local

import six
from django.conf import settings
from django.utils import lru_cache
from django.utils.functional import cached_property, lazy
from django.utils.html import SafeText
from django.utils.html import conditional_escape as conditional_html_escape
from django.utils.html import mark_safe as mark_html_escaped
from fluent.runtime import CompilingFluentBundle as FluentBundle

from .conf import get_setting
from .utils import make_namespace

_active_locale = local()

ftl_logger = logging.getLogger('django_ftl.message_errors')

text_type = six.text_type


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


class MessageFinderBase(object):

    @property
    def locale_base_dirs(self):
        raise NotImplementedError()

    def load(self, locale, path, reloader=None):
        locale = normalize_bcp47(locale)
        all_bases = self.locale_base_dirs
        tried = []
        for i, base in enumerate(all_bases):
            try:
                locale_dir = locale_dirs_at_path(base)[locale]
            except KeyError:
                tried.append(base + "/")
                continue

            full_path = os.path.join(locale_dir, path)
            try:
                with open(full_path, "rb") as f:
                    if reloader is not None:
                        reloader.add_watched_path(full_path)
                    return f.read().decode('utf-8')

            except (IOError, OSError):
                tried.append(full_path)

        raise FileNotFoundError("Could not find locate FTL file {0}/{1}. Tried: {2}"
                                .format(locale, path,
                                        ", ".join(tried)))


def normalize_bcp47(locale):
    return locale.lower().replace('_', '-')


@lru_cache.lru_cache(maxsize=None)
def locale_dirs_at_path(base):
    dirs_found = [p for p in
                  [os.path.join(base, e) for e in os.listdir(base)]
                  if os.path.isdir(p)]

    # Apply normalization and return mapping from locale nane to directory.
    return {normalize_bcp47(os.path.basename(p)): p
            for p in dirs_found}


class DjangoMessageFinder(MessageFinderBase):

    @cached_property
    def locale_base_dirs(self):
        return get_app_locale_dirs()


default_finder = DjangoMessageFinder()


class LanguageActivator(object):

    def activate(self, locale):
        old_value = self.get_current_value()
        if old_value == locale:
            return
        _active_locale.value = locale

    def deactivate(self):
        self.activate(None)

    def get_current_value(self):
        return getattr(_active_locale, 'value', None)


activator = LanguageActivator()


html_escaper = make_namespace(
    name="django_html_escaper",
    select=lambda message_id=None, **hints: message_id.endswith('-html'),
    output_type=SafeText,
    mark_escaped=mark_html_escaped,
    escape=conditional_html_escape,
    join=lambda parts: mark_html_escaped(''.join(conditional_html_escape(p) for p in parts)),
    use_isolating=True,
)


class Bundle(object):
    def __init__(self, paths,
                 finder=default_finder,
                 default_locale=None,
                 use_isolating=True,
                 require_activate=False,
                 auto_reload=None):

        self._paths = paths
        self._finder = finder
        self._default_locale = default_locale
        self._use_isolating = use_isolating
        self._require_activate = require_activate
        self._lock = Lock()

        if auto_reload is None:
            auto_reload = get_setting('AUTO_RELOAD_BUNDLES', None)

        if auto_reload is None:
            if settings.DEBUG:
                try:
                    import pyinotify  # noqa
                except ImportError:
                    ftl_logger.warning("Not using django_ftl autoreloader because pyinotify is not installed. Set `Bundle.auto_reload` or `AUTO_RELOAD_BUNDLES` to `False` to disable this warning.")
                else:
                    auto_reload = True

        if auto_reload:
            # import at this point to avoid importing pyinotify if we don't need it.
            from .autoreload import create_bundle_reloader
            self._reloader = create_bundle_reloader(self)
        else:
            self._reloader = None
        self.reload()

    def _make_fluent_bundle(self, locale):
        return FluentBundle([locale], use_isolating=self._use_isolating,
                            escapers=[html_escaper])

    def reload(self):
        with self._lock:
            self._all_fluent_bundles = {}  # dict from available locale to FluentBundle
            self._fluent_bundles_for_current_locale = {}  # dict from chosen locale to list of FluentBundle

    def _get_default_locale(self):
        default_locale = self._default_locale
        if default_locale is not None:
            return default_locale

        return get_setting('LANGUAGE_CODE')

    def get_fluent_bundles_for_current_locale(self):
        current_locale = activator.get_current_value()
        if current_locale is None:
            if self._require_activate:
                raise NoLocaleSet("activate() must be used before using Bundle.format "
                                  "- or, use Bundle(require_activate=False)")
        try:
            return self._fluent_bundles_for_current_locale[current_locale]
        except KeyError:
            pass

        # Fill out _fluent_bundles_for_current_locale and _all_fluent_bundles as
        # necessary, but do this synchronized for all threads.
        with self._lock:
            # Double checked locking pattern.
            try:
                return self._fluent_bundles_for_current_locale[current_locale]
            except KeyError:
                pass

            to_try = list(locale_lookups(current_locale)) if current_locale is not None else []
            default_locale = self._get_default_locale()
            if default_locale is not None:
                to_try = uniquify(to_try + [default_locale])

            bundles = []
            for i, locale in enumerate(to_try):
                try:
                    bundle = self._all_fluent_bundles[locale]
                    if bundle is not None:
                        bundles.append(bundle)
                except KeyError:
                    # Create the FluentBundle on demand
                    bundle = self._make_fluent_bundle(locale)

                    for path in self._paths:
                        try:
                            contents = self._finder.load(locale, path, reloader=self._reloader)
                        except FileNotFoundError:
                            if locale == default_locale:
                                # Can't find any FTL with the specified filename, we
                                # want to bail early and alert developer.
                                raise
                            # Allow missing files otherwise
                        else:
                            bundle.add_messages(contents)
                    errors = bundle.check_messages()
                    for msg_id, error in errors:
                        self._log_error(bundle, msg_id, {}, error)
                    bundles.append(bundle)
                    self._all_fluent_bundles[locale] = bundle

            # Shortcut next time
            self._fluent_bundles_for_current_locale[current_locale] = bundles
            return bundles

    def format(self, message_id, args=None):
        fluent_bundles = self.get_fluent_bundles_for_current_locale()
        for i, bundle in enumerate(fluent_bundles):
            try:
                value, errors = bundle.format(message_id, args=args)
                for e in errors:
                    self._log_error(bundle, message_id, args, e)
                return value
            except LookupError as e:
                self._log_error(bundle, message_id, args, e)

        # None were successful, return default
        return '???'

    format_lazy = lazy(format, text_type)

    def _log_error(self,
                   bundle,
                   message_id,
                   args,
                   exception):
        # TODO - nicer error that includes path and source line
        ftl_logger.error("FTL exception for locale [%s], message '%s', args %r: %s",
                         ", ".join(bundle.locales),
                         message_id,
                         args,
                         repr(exception))


def locale_lookups(locale):
    """
    Utility for implementing RFC 4647 lookup algorithm
    """
    if ',' in locale:
        locales = [l.strip() for l in locale.split(",")]
        return uniquify(sum(map(locale_lookups, locales), []))

    parts = locale.split('-')
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
