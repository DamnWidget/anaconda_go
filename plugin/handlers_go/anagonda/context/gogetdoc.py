

# Copyright (C) 2013 - 2016 - Oscar Campos <oscar.campos@member.fsf.org>
# This program is Free Software see LICENSE file for details

import sys
import shlex
from subprocess import PIPE

from process import spawn

from .error import AnaGondaError
from .base import AnaGondaContext

_go_get = 'github.com/zmb3/gogetdoc'


class GoGetDocError(AnaGondaError):
    """Fires on GoGetDoc errors
    """


class GoGetDoc(AnaGondaContext):
    """Context to run go doc cmd into anaconda_go
    """

    def __init__(self, path, offset, buf, env_ctx):
        self.path = path
        self.offset = offset
        self.buf = buf
        if sys.version_info >= (3,):
            self.buf = buf.encode('utf8')

        super(GoGetDoc, self).__init__(env_ctx, _go_get)

    def __enter__(self):
        """Check binary existence and perform command
        """

        super(GoGetDoc, self).__enter__()
        if not self._bin_found:
            raise GoGetDocError('{0} not found...'.format(self.binary))

        return self.doc()

    def doc(self):
        """Run the doc command and return back the results as a string
        """

        args = shlex.split('\'{0}\' -modified -pos \'{1}:#{2}\''.format(
            self.binary, self.path, self.offset
        ))
        print(' '.join(args))
        doc = spawn(args, stdin=PIPE, stdout=PIPE, stderr=PIPE, env=self.env)
        out, err = doc.communicate(self.buf)
        if err is not None and len(err) > 0:
            if sys.version_info >= (3,):
                err = err.decode('utf8')
            raise GoGetDocError(err)

        if sys.version_info >= (3,):
            out = out.decode('utf8')

        return out

    @property
    def binary(self):
        """Return back the binary path
        """

        return self.get_binary('gogetdoc')
