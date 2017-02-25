
# Copyright (C) 2013 - 2016 - Oscar Campos <oscar.campos@member.fsf.org>
# This program is Free Software see LICENSE file for details

import os
import sys
import shlex
from subprocess import PIPE

from process import spawn

from .error import AnaGondaError, GoGetError


class AnaGondaContext(object):
    """Every anaGonda context must inherit from this class
    """

    def __init__(self, env_ctx, go_get_url):
        self.__go_get_url = go_get_url
        self.__env = env_ctx
        self._bin_found = None

    def __enter__(self):
        """Check binary existence or run go get
        """

        if self._bin_found is None:
            if not os.path.exists(self.binary):
                try:
                    self.go_get()
                except AnaGondaError:
                    import traceback
                    print(traceback.print_exc())
                    self._bin_found = False
                    raise
            else:
                self._bin_found = True

    def __exit__(self, *ext):
        """Do nothing
        """

    @property
    def go(self):
        """Return the Go binary for this GOROOT
        """

        if self.__env['GOROOT'] == "":
            return "go"  # pray for it being in the PATH

        return os.path.join(self.__env['GOROOT'], 'bin', 'go')

    @property
    def env(self):
        """Prepare the environ with go vars and sanitization
        """

        env = {}
        curenv = os.environ.copy()
        for key in curenv:
            env[str(key)] = str(curenv[key])

        env.update(self.__env)
        return env

    def go_get(self):
        """Go get the code to execute the scoped context
        """

        args = shlex.split('{0} get {1}'.format(
            self.go, self.__go_get_url), posix=os.name != 'nt')
        go = spawn(args, stdout=PIPE, stderr=PIPE, env=self.env)
        out, err = go.communicate()
        if err is not None and len(err) > 0:
            if sys.version_info >= (3, 0):
                err = err.decode('utf8')
            raise GoGetError(err)
        self._bin_found = True

    def get_binary(self, binary):
        """Get a binary from the GOBIN/GOPATH
        """

        if self.env.get('GOBIN') is not None:
            binary_path = os.path.join(self.env['GOBIN'], binary)
            if os.path.exists(binary_path):
                return binary_path

        for path in self.env['GOPATH'].split(':'):
            binary_path = os.path.join(path, 'bin', binary)
            if os.path.exists(binary_path):
                return binary_path

        return '/not/found'
