
# Copyright (C) 2013 - 2016 - Oscar Campos <oscar.campos@member.fsf.org>
# This program is Free Software see LICENSE file for details

import sys
import shlex
from subprocess import PIPE

from process import spawn

from .error import AnaGondaError
from .base import AnaGondaContext

_go_get = 'github.com/josharian/impl'


class ImplError(AnaGondaError):
    """Fired on Impl errors
    """


class Impl(AnaGondaContext):
    """Context to run Impl tool into anaconda_go
    """

    def __init__(self, receiver, iface, env_ctx):
        self.receiver = receiver
        self.iface = iface
        super(Impl, self).__init__(env_ctx, _go_get)

    def __enter__(self):
        """Check binary existence and perform command
        """

        super(Impl, self).__enter__()
        if not self._bin_found:
            raise ImplError('{0} not found...'.format(self.binary))

        return self.impl()

    def impl(self):
        """Run the impl command and return back a string with the code
        """

        args = shlex.split('\'{0}\' \'{1}\' {2}'.format(
            self.binary, self.receiver, self.iface)
        )
        impl = spawn(args, stdout=PIPE, stderr=PIPE, env=self.env)
        out, err = impl.communicate()
        if err is not None and len(err) > 0:
            if sys.version_info >= (3,):
                err = err.decode('utf8')
            raise ImplError(err)

        if sys.version_info >= (3,):
            out = out.decode('utf8')

        return out

    @property
    def binary(self):
        """Return back the binary path
        """

        return self.get_binary('impl')
