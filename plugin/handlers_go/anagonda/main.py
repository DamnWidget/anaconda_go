
# Copyright (C) 2013 - 2016 - Oscar Campos <oscar.campos@member.fsf.org>
# This program is Free Software see LICENSE file for details

from collections import namedtuple

from .context import Registry


class anaGonda(object):
    """This object controls the anaGonda Go wrapper
    """

    _named_tuples = {
        'env': namedtuple('Environ', 'goroot gopath cgo_enabled'),
    }
    __version = None

    def __init__(self, goroot, gopath, cgo=True):
        self._env = self._ctx_named_tuples.get('env')(
            goroot, gopath, cgo
        )

    @property
    def nt(self):
        """Return named tuples value
        """
        return self._named_tuples.values()

    def autocomplete(self, code, path, offset):
        """Autocomplete the word under cursor using the given data
        """

        return Registry('autocomplete', code, path, offset, self._env)
