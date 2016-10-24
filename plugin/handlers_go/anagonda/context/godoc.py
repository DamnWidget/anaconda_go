
# Copyright (C) 2013 - 2016 - Oscar Campos <oscar.campos@member.fsf.org>
# This program is Free Software see LICENSE file for details

import os
import sys
import shlex
from subprocess import PIPE

from process import spawn

from .error import AnaGondaError
from .base import AnaGondaContext

_go_get = 'golang.org/x/tools/cmd/godoc'


class DocError(AnaGondaError):
    """Fires on Doc errors
    """


class Doc(AnaGondaContext):
    """Context to run go doc cmd into anaconda_go
    """

    def __init__(self, path, expr, private, env_ctx):
        self.path = path
        self.expr = expr
        self.private = private
        super(Doc, self).__init__(env_ctx, _go_get)

    def __enter__(self):
        """Check binary existence and perform command
        """

        super(Doc, self).__enter__()
        if not self._bin_found:
            raise DocError('{0} not found...'.format(self.binary))

        return self.doc()

    def doc(self):
        """Run the doc command and return back the results as a string
        """

        args = shlex.split('\'{0}\' doc {1}{2}'.format(
            self.binary, '-u ' if self.private else '', self.expr
        ))
        print(' '.join(args))
        godoc = spawn(
            args, stdout=PIPE, stderr=PIPE, env=self.env,
            cwd=os.path.dirname(self.path)
        )
        out, err = godoc.communicate()
        if err is not None and len(err) > 0:
            if sys.version_info >= (3,):
                err = err.decode('utf8')
            raise DocError(err)

        if sys.version_info >= (3,):
            out = out.decode('utf8')

        return out

    @property
    def binary(self):
        """Return back the binary path
        """

        return os.path.join(self.env['GOROOT'], 'bin', 'go')
