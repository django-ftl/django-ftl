# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals


def make_namespace(**attributes):
    class namespace(object):
        pass

    namespace = namespace()
    for k, v in attributes.items():
        setattr(namespace, k, v)

    return namespace
