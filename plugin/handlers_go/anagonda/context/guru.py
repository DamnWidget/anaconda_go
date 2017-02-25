
# Copyright (C) 2013 - 2016 - Oscar Campos <oscar.campos@member.fsf.org>
# This program is Free Software see LICENSE file for details

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

    def __init__(self, sc, mode, path, offset, modified_buffer, env_ctx):
        self.scope = sc
        self.mode = mode
        self.path = path
        self.offset = offset
        self.modified_buffer = modified_buffer
        self.modified_buffer = modified_buffer.encode('utf8')

        super(Guru, self).__init__(env_ctx, _go_get)

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

        scope = ''
        if self.scope is not None and self.scope != '':
            scope = ' -scope {0}'.format(self.scope)

        args = shlex.split('"{0}"{1} -json -modified {2} "{3}:#{4}"'.format(
            self.binary, scope,
            self.mode, self.path, self.offset)
        )
        print(' '.join(args))
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

        try:
            data = json.loads(out)
        except:
            data = json.loads(
                '[' + out.replace('}\n{', '},\n{').replace('\t', '') + ']'
            )

        if type(data) is dict:
            data['tool'] = 'guru'
        return data

    @property
    def binary(self):
        """Return back the binary path
        """

        return self.get_binary('guru')
