
# Copyright (C) 2013 - 2016 - Oscar Campos <oscar.campos@member.fsf.org>
# This program is Free Software see LICENSE file for details

import logging
from .error import RegistryError, GoGetError


class Registry(object):
    """Just a convenience proxy class
    """

    __ctxs = {}

    def __call__(self, ctx_id, *args, **kwargs):
        """Invoque a context from the registry
        """

        ctx = Registry.__ctxs.get(ctx_id)
        if ctx is None:
            _registry_not_found(ctx_id)
        try:
            with ctx as result:
                return result
        except GoGetError as error:
            msg = 'while `go get {0}`: {1}'.format(ctx.binary, error)
            print(msg)
            logging.error(msg)
            raise RegistryError(msg)

    @classmethod
    def register(cls, ctx):
        """Register a context into the registry
        """

        Registry.__ctxs[ctx.__name__.lower()] = ctx

    @classmethod
    def is_healhy(cls, ctx):
        """Check if a context in the registry is healthy
        """

        ctx = Registry.__ctxs.get(ctx.__name__.lower())
        if ctx is None:
            _registry_not_found(ctx.__name__.lower())


def _registry_not_found(ctx_id):
    """Just raise the exception
    """

    raise RegistryError(
        '{0} not found in registry, did you forgot '
        'to run Registry.register?'.format(ctx_id)
    )
