from __future__ import absolute_import, print_function, unicode_literals

from django.conf import settings

NOT_PROVIDED = object()


def get_setting(name, default=NOT_PROVIDED):
    # Look in FTL dict for setting, otherwise fallback to settings module,
    # otherwise fallback to default
    setting_dict = getattr(settings, 'FTL', {})

    if default is NOT_PROVIDED:
        fallback = getattr(settings, name)
    else:
        fallback = getattr(settings, name, default)
    return setting_dict.get(name, fallback)
