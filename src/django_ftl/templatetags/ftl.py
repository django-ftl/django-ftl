from __future__ import absolute_import, print_function, unicode_literals

import contextlib

import six
from django import template
from django.template.base import token_kwargs
from django.utils.module_loading import import_string

import django_ftl

register = template.Library()

MODE_SERVER = 'server'
MODES = [
    MODE_SERVER
]

MODE_VAR_NAME = '__ftl_mode'
BUNDLE_VAR_NAME = '__ftl_bundle'


@register.simple_tag(takes_context=True)
def ftlconf(context, mode=None, bundle=None):
    if mode is not None:
        validate_mode(mode)
        context[MODE_VAR_NAME] = mode
    if bundle is not None:
        context[BUNDLE_VAR_NAME] = resolve_bundle(bundle)
    return ''


def resolve_bundle(bundle):
    if isinstance(bundle, six.text_type):
        return import_string(bundle)
    else:
        return bundle


@register.simple_tag(takes_context=True)
def ftlmsg(context, message_id, **kwargs):
    try:
        mode = context[MODE_VAR_NAME]
    except KeyError:
        raise ValueError("No mode set for ftl - use ftlconf/withftl to set mode")
    try:
        bundle = context[BUNDLE_VAR_NAME]
    except KeyError:
        raise ValueError("No bundle set for ftl - use ftlconf/withftl to set bundle")
    if mode == MODE_SERVER:
        return bundle.format(message_id, kwargs)
    raise AssertionError("Not reached")


def validate_mode(mode):
    if mode not in MODES:
        raise ValueError("mode '{0}' not understood, must be one of {1}"
                         .format(mode, MODES))


class WithFtlNode(template.Node):
    def __init__(self, nodelist, language=None, mode=None, bundle=None):
        self.nodelist = nodelist
        self.language = language
        self.mode = mode
        self.bundle = bundle

    def __repr__(self):
        return '<%s>' % self.__class__.__name__

    def render(self, context):
        language = None if self.language is None else self.language.resolve(context)
        mode = None if self.mode is None else self.mode.resolve(context)
        if mode is not None:
            validate_mode(mode)
        bundle = None if self.bundle is None else resolve_bundle(self.bundle.resolve(context))
        new_context = {}
        if mode is not None:
            new_context[MODE_VAR_NAME] = mode
        if bundle is not None:
            new_context[BUNDLE_VAR_NAME] = bundle
        if language is not None:
            lang_ctx = django_ftl.override(language)
        else:
            lang_ctx = null_ctx()

        with context.push(**new_context):
            with lang_ctx:
                return self.nodelist.render(context)


@register.tag('withftl')
def withftl(parser, token):
    conf = token_kwargs(token.split_contents()[1:], parser, support_legacy=False)
    language = conf.pop('language', None)
    mode = conf.pop('mode', None)
    bundle = conf.pop('bundle', None)
    if conf:
        raise ValueError("withftl tag received unexpected keyword arguments: {0}"
                         .format(", ".join(conf.keys())))
    nodelist = parser.parse(('endwithftl',))
    parser.delete_first_token()

    return WithFtlNode(nodelist,
                       language=language,
                       mode=mode,
                       bundle=bundle)


@contextlib.contextmanager
def null_ctx():
    yield
