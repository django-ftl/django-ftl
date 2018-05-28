from __future__ import absolute_import, print_function, unicode_literals

import os
from threading import local
import logging

from django.dispatch import Signal
from django.utils.functional import cached_property
from django.utils import lru_cache
from fluent.context import MessageContext

_active_locale = local()

ftl_logger = logging.getLogger('django_ftl.message_errors')


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

    def load(self, locale, path):
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
        # We reverse to give priority to later apps
        return list(reversed(get_app_locale_dirs()))


default_finder = DjangoMessageFinder()


class LanguageActivator(object):
    locale_changed = Signal()

    def activate(self, locale):
        old_value = self.get_current_value()
        if old_value == locale:
            return
        _active_locale.value = locale

        self.locale_changed.send(self, old_value=old_value, new_value=locale)

    def deactivate(self):
        self.activate(None)

    def get_current_value(self):
        return getattr(_active_locale, 'value', None)


activator = LanguageActivator()


class Bundle(object):
    def __init__(self, paths,
                 finder=default_finder,
                 fallback_locale=None,
                 use_isolating=True,
                 activator=activator):
        self._paths = paths
        self._finder = finder
        self._loaded = False
        self._all_message_contexts = {}  # dict from locale to MessageContext
        self._fallback_locale = fallback_locale
        self._use_isolating = use_isolating

        self.current_locale = activator.get_current_value()
        activator.locale_changed.connect(self.locale_changed_receiver)

    def _make_message_context(self, locale):
        return MessageContext([locale], use_isolating=self._use_isolating)

    @property
    def current_locale(self):
        return getattr(self, '_current_locale', None)

    @current_locale.setter
    def current_locale(self, value):
        old_value = self.current_locale
        self._current_locale = value
        if old_value != value:
            try:
                del self._current_message_contexts
            except AttributeError:
                pass

    def locale_changed_receiver(self, sender, new_value=None, **kwargs):
        self.current_locale = new_value

    @property
    def current_message_contexts(self):
        try:
            return self._current_message_contexts
        except AttributeError:
            pass

        current_locale = self.current_locale
        if current_locale is None:
            raise NoLocaleSet("Bundle.current_locale must be set "
                              "(or passed as 'default_locale' to the constructor) "
                              "before using Bundle.format")

        to_try = [current_locale]
        if self._fallback_locale is not None:
            to_try.append(self._fallback_locale)

        contexts = []
        for i, locale in enumerate(to_try):
            last_item = i == len(to_try)
            try:
                context = self._all_message_contexts[locale]
                if context is not None:
                    contexts.append(context)
            except KeyError:
                context = self._make_message_context(locale)

                for path in self._paths:
                    try:
                        contents = self._finder.load(locale, path)
                    except FileNotFoundError:
                        if last_item:
                            # Can't find any FTL with the name, we want to bail
                            # early and alert developer.
                            raise
                        else:
                            # Allow it, because we will use later ones as fallbacks.
                            # Mark the fact that we failed to find the file,
                            # to avoid file system lookups next time.
                            self._all_message_contexts[locale] = None
                    else:
                        context.add_messages(contents)
                        self._all_message_contexts[locale] = context
                        contexts.append(context)

        # Shortcut next time
        self._current_message_contexts = contexts
        return contexts

    def format(self, message_id, args=None,
               lazy=False):
        message_contexts = self.current_message_contexts
        for i, context in enumerate(message_contexts):
            try:
                value, errors = context.format(message_id, args=args)
                for e in errors:
                    self._log_error(context, message_id, args, e)
                return value
            except LookupError as e:
                self._log_error(context, message_id, args, e)

        # None were successful, return default
        return '???'

    def _log_error(self,
                   context,
                   message_id,
                   args,
                   exception):
        ftl_logger.error("FTL exception for locale [%s], message '%s', args %r: %s",
                         ", ".join(context.locales),
                         message_id,
                         args,
                         repr(exception))
