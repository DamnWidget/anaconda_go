
# Copyright (C) 2013 - 2016 - Oscar Campos <oscar.campos@member.fsf.org>
# This program is Free Software see LICENSE file for details

import logging
import traceback

from ..anagonda.context import guru
from commands.base import Command


class AnalyzeSymbol(Command):
    """Run guru to get a detailed description of the symbol
    """

    def __init__(
            self, callback, uid, vid, scope, offset, path, buf, go_env):
        self.vid = vid
        self.scope = scope
        self.offset = offset
        self.path = path
        self.buf = buf
        self.go_env = go_env
        super(AnalyzeSymbol, self).__init__(callback, uid)

    def run(self):
        """Run the command
        """

        try:
            with guru.Guru(
                self.scope, 'describe', self.path,
                    self.offset, self.buf, self.go_env) as desc:

                self.callback({
                    'success': True,
                    'result': desc,
                    'uid': self.uid,
                    'vid': self.vid
                })
        except Exception as error:
            logging.error(error)
            logging.debug(traceback.format_exc())
            self.callback({
                'success': False,
                'error': str(error),
                'uid': self.uid,
                'vid': self.vid
            })
