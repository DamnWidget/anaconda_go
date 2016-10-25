
# Copyright (C) 2013 - 2016 - Oscar Campos <oscar.campos@member.fsf.org>
# This program is Free Software see LICENSE file for details

import os
import sys
import json
import shlex
from subprocess import PIPE

from process import spawn

from .error import AnaGondaError
from .base import AnaGondaContext

_go_get = 'github.com/DamnWidget/godef'


class GoDefError(AnaGondaError):
    """Fired on godef errors
    """


class GoDef(AnaGondaContext):
    """Context to run the godef tool into anaconda_go
    """

    _bin_found = False

    def __init__(self, code, path, expr, extended, env_ctx):
        self.expr = expr
        self.path = path
        self.extended = extended
        self.code = code.encode() if sys.version_info >= (3,) else code
        super(GoDef, self).__init__(env_ctx, _go_get)

    def __enter__(self):
        """Check binary existence and perform the command
        """

        super(GoDef, self).__enter__()
        if not self._bin_found:
            raise GoDefError('{0} not found...'.format(self.binary))

        return self.godef()

    def godef(self):
        """Use godef to look for the definition of the word under the cursor
        """

        args = shlex.split('\'{0}\' -json -i -p \'{1}\' {2}{3}'.format(
            self.binary, self.path, '-A' if self.extended else '', self.expr)
        )
        godef = spawn(
            args, stdin=PIPE, stdout=PIPE, stderr=PIPE, env=self.env
        )
        out, err = godef.communicate(self.code)
        if err is not None and len(err) > 0:
            if sys.version_info >= (3,):
                err = err.decode('utf8')
            raise GoDefError(err)

        if sys.version_info >= (3,):
            out = out.decode('utf8')

        if not self.extended:
            if out == '{}':
                return {'src': 'builtin', 'line': 0, 'col': 0}

        data = json.loads(out)
        data['tool'] = 'godef'
        return data

    @property
    def binary(self):
        """Return back the binary path
        """

        return os.path.join(self.env['GOPATH'], 'bin', 'godef')
