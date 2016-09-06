
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

_go_get = 'github.com/nsf/gocode'


class AutoCompleteError(AnaGondaError):
    """Fired on autocompletion errors
    """


class AutoComplete(AnaGondaContext):
    """Context to run the gocode tool into anaconda_go
    """

    def __init__(self, code, path, offset, env_ctx):
        self._bin_found = None
        self.path = path
        self.offset = offset
        self.code = code.encode() if sys.version_info >= (3,) else code
        super(AutoComplete, self).__init__(_go_get, env_ctx)

    def __enter__(self):
        """Check binary existence and perform the command
        """

        super(AutoComplete, self).__enter__()
        if self._bin_found is False:
            raise AutoCompleteError('{} not found...'.format(self.binary))

        return self.autocomplete()

    def autocomplete(self):
        """Autocomplete the word under cursor using the given data
        """

        args = shlex.split('{0} -f json autocomplete {1} {2}'.format(
            self.binary, self.path, self.offset), posix=os.name != 'nt'
        )
        gocode = spawn(
            args, stdin=PIPE, stdout=PIPE, stderr=PIPE, env=self.env
        )
        out, err = gocode.communicate(self.code)
        if err is not None and len(err) > 0:
            if sys.version_info >= (3):
                err = err.decode('utf8')
            raise AutoCompleteError(err)

        if sys.version_info >= (3,):
            out = out.decode('utf8')

        try:
            completions = json.loads(out)
        except Exception as error:
            raise AutoCompleteError(error)

        if len(completions) > 0:
            return completions[1]

    @property
    def binary(self):
        """Return back the binary path
        """

        return os.path.join(os.environ['GOPATH'], 'bin', 'gocode')
