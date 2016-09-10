
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

_go_get = 'gopkg.in/alecthomas/gometalinter.v1'


class GometaLinterError(AnaGondaError):
    """Fires on GometaLinter errors
    """


class GometaLinter(AnaGondaContext):
    """Context to run gometalinter tool into anaconda_go
    """

    def __init__(self, options, env_ctx):
        self.options = options
        self.option.append('--json')
        super(GometaLinter, self).__init__(env_ctx)

    def __enter__(self):
        """Check binary existence and perform command
        """

        if self._bin_found is None:
            if not os.path.exists(self.binary):
                try:
                    self.go_get()
                    self._install_linters()
                except AnaGondaError:
                    self._bin_found = False
                    raise

        if not self._bin_found:
            raise GometaLinterError('{0} not found...'.format(self.binary))

        return self.gometalinter()

    def gometalinter(self):
        """Run gometalinter and return back a JSON object with it's results
        """

        args = shlex.split(
            '{0} {1}'.format(self.binary, self.options), posix=os.name != 'nt'
        )
        gometalinter = spawn(args, stdout=PIPE, stderr=PIPE, env=self.env)
        out, err = gometalinter.communicate()
        if err is not None and len(err) > 0:
            if sys.version_info >= (3,):
                err = err.decode('utf8')
            raise GometaLinterError(err)

        if sys.version_info >= (3,):
            out = out.decode('utf8')

        return json.loads(out)

    def _install_linters(self):
        """Install gometalinter linters
        """

        args = shlex.split('{0} --install'.format(self.binary))
        gometalinter = spawn(args, stdout=PIPE, stderr=PIPE, env=self.env)
        _, err = gometalinter.communicate()
        if err is not None and len(err) > 0:
            if sys.version_info >= (3,):
                err = err.decode('utf8')
            raise GometaLinterError(err)

    @property
    def binary(self):
        """Return back the binary path
        """

        return os.path.join(self.env['GOPATH'], 'bin', 'gometalinter.v1')
