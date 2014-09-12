
# Copyright (C) 2014 - Oscar Campos <oscar.campos@member.fsf.org>
# This program is Free Software see LICENSE file for details

import os
import time
import sublime
import subprocess

from ..anaconda_plugin import create_subprocess


class GolangDetector:

    """Detect the local golang installation (if any)
    """

    _detected = False
    GOROOT = None
    GOPATH = None
    CGO_ENABLED = None

    def __call__(self):
        start = time.time()
        if self._detect_in_environment():
            self._detected = True

        if not self._detected and self._detect_in_shell():
            self._detected = True

        if self._detected:
            print('AnacondaGO: finished detecting environment in {}s'.format(
                time.time() - start
            ))
        else:
            sublime.error_message(
                'AnacondaGO has been unable to determine the following '
                'required environment variables:\n'
                '\tGOROOT {}\n\tGOPATH {}\n\tCGO_ENABLED {}\n\n'
                'AnacondaGO can\'t work without those variables, that means '
                'that the plugin is not going to work out of the box and you '
                'will provide the correct values for these variables in any '
                'configuration level (project settings or AnacondaGO settings)'
                ''.format(self.GOROOT, self.GOPATH, self.CGO_ENABLED)
            )

        return (self.GOROOT, self.GOPATH, self.CGO_ENABLED)

    @property
    def go_binary(self):
        """Return back the go binary location if Go is detected
        """

        if self._detected:
            return os.path.join(self.GOROOT, 'bin', 'go')

    @property
    def go_version(self):
        """Return back the version of the go compiler/runtime
        """

    def _detect_in_environment(self):
        """Detect Go parameters in the inheritted shell environemnt vars
        """

        environ = os.environ
        self.GOROOT = environ.get('GOROOT')
        self.GOPATH = environ.get('GOPATH')
        self.CGO_ENABLED = environ.get('CGO_ENABLED')

        if self.GOROOT is None or self.GOPATH is None:
            return False

        self._normalize_cgo()
        return True

    def _detect_in_shell(self):
        """Detect Go parameters using the shell directly
        """

        if sublime.platform() == 'windows':
            return self._detect_in_windows_shell()

        return self._detect_in_unix_shell()

    def _detect_in_windows_shell(self):
        """Detect Go parameters in windows shell (normally cmd)
        """

        shell = os.environ.get('COMSPEC', 'cmd')
        self._spawn_processes(shell, '/C')
        if self.GOROOT is None or self.GOPATH is None:
            return False

        self._normalize_cgo()
        return True

    def _detect_in_unix_shell(self):
        """Deect Go parameters in unix shell (normally sh)
        """

        shell = os.environ.get('SHELL', 'sh')
        self._spawn_processes(shell, '-l', '-c')
        if self.GOROOT is None or self.GOPATH is None:
            return False

        self._normalize_cgo()
        return True

    def _spawn_processes(self, *args):
        """Spawn a shell process and ask for go environment variables
        """

        for var in ['GOROOT', 'GOPATH', 'CGO_ENABLED']:
            targs = args + ['go', 'env', var]
            try:
                proc = create_subprocess(*targs, stdout=subprocess.PIPE)
            except:
                print('AnacondaGO: go binary is not in your PATH')
                return

            output, _ = proc.communicate()
            if output != '':
                setattr(self, var, output)

    def _normalize_cgo(self):
        """Set CGO_ENABLED to False if is not set
        """

        if self.CGO_ENABLED is None:
            self.CGO_ENABLED = False
