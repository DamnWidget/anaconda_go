
# Copyright (C) 2013 - 2016 - Oscar Campos <oscar.campos@member.fsf.org>
# This program is Free Software see LICENSE file for details

from collections import namedtuple

from .context import Registry
from .context.error import AnaGondaError


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

    def definitions(self, code, path, settings):
        """Run Godef, Guru or both and return a JSON object
        """

        guru_usage = settings.get('anaconda_go_guru_usage', 'fallback')
        if guru_usage == 'always':
            return self._run_guru(code, path, settings)

        definitions = []
        try:
            expr = settings.get('expr', '')
            ext = settings.get('extended', False)
            definitions = Registry('godef', code, path, expr, ext, self._env)
        except AnaGondaError as e:
            if guru_usage == 'fallback':
                return self._run_guru(code, path, settings)
        else:
            if len(definitions) == 0 and guru_usage == 'fallback':
                return self._run_guru(code, path, settings)

        return definitions

    def motion(self, fp, dp, offset, mode, include, parse_comments):
        """Run Motion and return back a dictionary with results
        """

        return Registry(
            'motion', fp, dp, offset, mode,
            inlcude, parse_comments, self._env
        )

    def lint(self, options):
        """Run gometalinter with the given options
        """

        return Registry('gometalinter', options, self._env)

    def impl(self, receiver, iface):
        """Run Impl and return back a string with the implementation
        """

        return Registry('impl', receiver, iface, self._env)

    def _run_guru(self, code, path, settings):
        """Run the Guru context
        """

        offset = settings.get('offset', 0)
        buf = settings.get('modified_buffer')
        return Regisrty('guru', code, path, offset, buf, self._env)

