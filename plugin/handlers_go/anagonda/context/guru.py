
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

_go_get = 'golang.org/x/tools/cmd/guru'


class GuruError(AnaGondaError):
    """Fired on Guru errors
    """


class Guru(AnaGondaContext):
    """Context to run the guru tool into anaconda_go
    """

    _bin_found = False

    def __init__(self, code, path, offset, modified_buffer, env_ctx):
        self.path = path
        self.offset = offset
        self.code = code.encode() if sys.version_info >= (3,) else code
        self.modified_buffer = modified_buffer
        super(Guru, self).__init__(_go_get, env_ctx)

    def __enter__(self):
        """Check binary existence and perform command
        """

        super(Guru, self).__enter__()
        if not self._bin_found:
            raise GuruError('{0} not found...'.format(self.binary))

        return self.guru()

    def guru(self):
        """Use Guru to look for the definition of the word under the cursor
        """

        args = shlex.split('{0} -json -modified describe {1}:#{2}'.format(
            self.binary, self.path, self.offset),
            posix=os.name != 'nt'
        )
        guru = spawn(
            args, stdin=PIPE, stdout=PIPE, stderr=PIPE, env=self.env
        )
        out, err = guru.communicate(self.modified_buffer)
        if err is not None and len(err) > 0:
            if sys.version_info >= (3,):
                err = err.decode('utf8')
            raise GuruError(err)

        if sys.version_info >= (3,):
            out = out.decode('utf8')

        return json.loads(out)

    @property
    def binary(self):
        """Return back the binary path
        """

        return os.path.join(os.environ['GOPATH'], 'bin', 'guru')
