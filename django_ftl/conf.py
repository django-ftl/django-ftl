from django.conf import settings


def get_setting(name):
    # Look in FTL dict for setting, otherwise fallback to settings module. e.g.
    setting_dict = getattr(settings, 'FTL', {})

    return setting_dict.get(name, getattr(settings, name))
