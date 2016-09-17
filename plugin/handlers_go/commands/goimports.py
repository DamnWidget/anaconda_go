

# Copyright (C) 2013 - 2016 - Oscar Campos <oscar.campos@member.fsf.org>
# This program is Free Software see LICENSE file for details

import logging
import traceback

from ..anagonda.context import goimports
from commands.base import Command


class Goimports(Command):
    """Run goimports
    """

    def __init__(self, callback, uid, vid, code, go_env):
        self.vid = vid
        self.code = code
        self.go_env = go_env
        super(Goimports, self).__init__(callback, uid)

    def run(self):
        """Run the command
        """

        try:
            with goimports.Goimports(self.code, self.go_env) as text:
                self.callback({
                    'success': True,
                    'result': text,
                    'uid': self.uid,
                    'vid': self.vid
                })
        except Exception as error:
            logging.error(error)
            logging.debug(traceback.format_exc())
            self.callback({
                'succes': False,
                'error': str(error),
                'uid': self.uid,
                'vid': self.vid
            })
