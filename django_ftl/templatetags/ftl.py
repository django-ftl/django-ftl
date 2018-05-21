from __future__ import absolute_import, print_function, unicode_literals

from django import template
from django.utils.module_loading import import_string

register = template.Library()

MODE_SERVER = 'server'
MODES = [
    MODE_SERVER
]


@register.simple_tag
def ftl(mode, bundle_id, message_id, **kwargs):
    bundle = import_string(bundle_id)
    return do_render(mode, bundle, message_id, kwargs)


@register.simple_tag(takes_context=True)
def ftl_conf(context, mode, bundle_id):
    context['__ftl_mode'] = mode
    context['__ftl_bundle'] = import_string(bundle_id)
    return ''


@register.simple_tag(takes_context=True)
def ftl_message(context, message_id, **kwargs):
    return do_render(context['__ftl_mode'],
                     context['__ftl_bundle'],
                     message_id,
                     kwargs)


def do_render(mode, bundle, message_id, kwargs):
    if mode not in MODES:
        raise ValueError("mode '{0}' not understood, must be one of {2}"
                         .format(mode, MODES))
    if mode == MODE_SERVER:
        return bundle.format(message_id, kwargs)
