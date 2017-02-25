
# Copyright (C) 2013 - 2016 - Oscar Campos <oscar.campos@member.fsf.org>
# This program is Free Software see LICENSE file for details

import sys
from subprocess import PIPE

from process import spawn

from .error import AnaGondaError
from .base import AnaGondaContext

_go_get = 'golang.org/x/tools/cmd/goimports'


class GoimportsError(AnaGondaError):
    """Fired on Goimports errors
    """


class Goimports(AnaGondaContext):
    """Context to run Goimports tool into anaconda_go
    """

    def __init__(self, code, path, env_ctx):
        self.code = code if sys.version_info < (3,) else code.encode('utf8')
        self.path = path
        super(Goimports, self).__init__(env_ctx, _go_get)

    def __enter__(self):
        """Check binary existence and perform command
        """

        super(Goimports, self).__enter__()
        if not self._bin_found:
            raise GoimportsError('{0} not found...'.format(self.binary))

        return self.goimports()

    def goimports(self):
        """Run the goimports command and return back a string with the code
        """

        args = [self.binary, self.path]
        goimports = spawn(
            args, stdout=PIPE, stderr=PIPE, stdin=PIPE, env=self.env)
        out, err = goimports.communicate(self.code)
        if err is not None and len(err) > 0:
            if sys.version_info >= (3,):
                err = err.decode('utf8')
            raise GoimportsError(err)

        if sys.version_info >= (3,):
            out = out.decode('utf8')

        return out

    @property
    def binary(self):
        """Return back the binary path
        """

        return self.get_binary('goimports')
