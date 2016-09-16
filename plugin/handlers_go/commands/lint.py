
# Copyright (C) 2013 - 2016 - Oscar Campos <oscar.campos@member.fsf.org>
# This program is Free Software see LICENSE file for details

import logging
import traceback

from ..anagonda.context.gometalinter import GometaLinter
from commands.base import Command


class Lint(Command):
    """Run gometalinter
    """

    def __init__(self, callback, uid, vid, path, cmdline, go_env):
        self.vid = vid
        self.path = path
        self.cmdline = cmdline
        self.go_env = go_env
        super(Lint, self).__init__(callback, uid)

    def run(self):
        """Run the command
        """

        try:
            with GometaLinter(self.cmdline, self.path, self.go_env) as lint:
                self.callback({
                    'success': True,
                    'errors': lint,
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
