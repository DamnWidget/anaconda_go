
# Copyright (C) 2013 - 2016 - Oscar Campos <oscar.campos@member.fsf.org>
# This program is Free Software see LICENSE file for details

import os
import sys
import json
import shlex
import logging
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

    def __init__(self, options, filepath, env_ctx):
        self.filepath = filepath
        self.options = options
        super(GometaLinter, self).__init__(env_ctx, _go_get)

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
            elif not os.path.exists(self.golint):
                try:
                    self._install_linters()
                except AnaGondaError:
                    self._bin_found = False
                    raise
            else:
                self._bin_found = True

        if not self._bin_found:
            raise GometaLinterError('{0} not found...'.format(self.binary))

        return self.gometalinter()

    def __exit__(self, *ext):
        """Do nothing
        """

    def gometalinter(self):
        """Run gometalinter and return back a JSON object with it's results
        """

        args = shlex.split(
            '\'{0}\' {1}'.format(self.binary, self.options)
        )
        print(' '.join(args))
        gometalinter = spawn(args, stdout=PIPE, stderr=PIPE, env=self.env)
        out, err = gometalinter.communicate()
        if err is not None and len(err) > 0:
            if sys.version_info >= (3,):
                err = err.decode('utf8')

            if 'deadline' not in err:
                raise GometaLinterError(err)
            else:
                logging.info(
                    'Some linters are running out of time with deadline '
                    'errros, please, consider to run just fast linters as '
                    'your system seems to be a bit slow'
                )

        if sys.version_info >= (3,):
            out = out.decode('utf8')

        return self._normalize(json.loads(out))

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

    def _normalize(self, metaerrors):
        """Normalize output format to be usable by Anaconda's linting frontend
        """

        errors = []
        error_lines = {}
        for error in metaerrors:
            last_path = os.path.join(
                os.path.basename(os.path.dirname(self.filepath)),
                os.path.basename(self.filepath)
            )
            if last_path not in error.get('path', ''):
                continue

            error_type = error.get('severity', 'X').capitalize()[0]
            if error_type == 'X':
                continue
            if error_type not in ['E', 'W']:
                error_type = 'V'

            error_line = error.get('line', 0)
            error_object = {
                'underline_range': True,
                'lineno': error_line,
                'offset': error.get('col', 0),
                'raw_message': error.get('message', ''),
                'code': 0,
                'level': error_type,
                'message': '[{0}] {1} ({2}): {3}'.format(
                    error_type,
                    error.get('linter', 'none'),
                    error.get('severity', 'none'),
                    error.get('message')
                )
            }

            # lots of linters will report the same error so let's clean up
            if error_line in error_lines:
                err = error_lines[error_line]
                if err['level'] == 'W' and error_type == 'E':
                    errors.remove(err)
                    errors.append(error_object)
                    error_lines[error_line] = error
            else:
                errors.append(error_object)
                error_lines[error_line] = error_object

        return errors

    @property
    def golint(self):
        """Return back the golint binary path
        """

        return os.path.join(self.env['GOPATH'], 'bin', 'golint')

    @property
    def binary(self):
        """Return back the binary path
        """

        return os.path.join(self.env['GOPATH'], 'bin', 'gometalinter.v1')
