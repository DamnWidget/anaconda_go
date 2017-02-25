
# Copyright (C) 2013 - 2016 - Oscar Campos <oscar.campos@member.fsf.org>
# This program is Free Software see LICENSE file for details

import sys
import json
import shlex
from subprocess import PIPE

from process import spawn

from .error import AnaGondaError
from .base import AnaGondaContext

_go_get = 'github.com/fatih/motion'


class MotionError(AnaGondaError):
    """Fires on Motion errors
    """


class Motion(AnaGondaContext):
    """Context to run motion tool into anaconda_go
    """

    def __init__(self, fp, dp, offset, mode, include, pc, env_ctx):
        self.file_path = fp
        self.dir_path = dp
        self._offset = offset
        self.mode = mode
        self._include = include
        self._parse_comments = pc
        super(Motion, self).__init__(env_ctx, _go_get)

    def __enter__(self):
        """Check binary existence and perform command
        """

        super(Motion, self).__enter__()
        if not self._bin_found:
            raise MotionError('{0} not found...'.format(self.binary))

        return self.motion()

    @property
    def scope(self):
        """Determine the motion scope infering from arguments passed to
        """

        if self.file_path is None and self.dir_path is not None:
            return '-dir'
        if self.file_path is not None and self.dir_path is None:
            return '-file'
        if self.file_path is not None and self.dir_path is not None:
            if self.mode == 'decls':
                return '-dir'
            return '-file'

    @property
    def path(self):
        """Return the right path based in the scope
        """

        return {
            '-dir': self.dir_path, '-file': self.file_path
        }.get(self.scope)

    @property
    def offset(self):
        """Return the offset always that -file scope is in use
        """

        offset = {'-file': self._offset, '-dir': ''}.get(self.scope)
        if offset is not None and offset != '':
            offset = '-offset {0}'.format(offset)
        return offset if offset is not None else ''

    @property
    def parse_comments(self):
        """If parse comments is active add it to the command
        """

        return {True: '-parse-comments'}.get(self._parse_comments, '')

    @property
    def include(self):
        """If include is set return the whole syntax
        """

        return '-include {0}'.format(self._include) \
               if self._include is not None else ''

    def motion(self):
        """Run the motion command and return back json object with the results
        """

        args = shlex.split('"{0}" {1} \'{2}\' {3} -mode {4} {5}{6}{7}'.format(
            self.binary, self.scope, self.path,
            self.offset, self.mode, self.include, self.parse_comments,
            ' -shift 1' if self.mode == 'prev' else ''
        ))
        motion = spawn(args, stdout=PIPE, stderr=PIPE, env=self.env)
        out, err = motion.communicate()
        if err is not None and len(err) > 0:
            if sys.version_info >= (3,):
                err = err.decode('utf8')
            raise MotionError(err)

        if sys.version_info >= (3,):
            out = out.decode('utf8')

        return json.loads(out)

    @property
    def binary(self):
        """Return back the binary path
        """

        return self.get_binary('motion')
