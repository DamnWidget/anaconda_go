
# Copyright (C) 2013 - 2016 - Oscar Campos <oscar.campos@member.fsf.org>
# This program is Free Software see LICENSE file for details

import logging
import traceback

from ..anagonda.context import guru
from commands.base import Command


class Referrers(Command):
    """Run guru or godef
    """

    def __init__(self, callback, uid, vid, scope, path, offset, buf, go_env):
        self.vid = vid
        self.scope = scope
        self.path = path
        self.offset = offset
        self.modified_buffer = buf
        self.go_env = go_env
        super(Referrers, self).__init__(callback, uid)

    def run(self):
        """Run the command
        """

        try:
            with guru.Guru(
                self.scope, 'referrers', self.path,
                    self.offset, self.modified_buffer, self.go_env) as result:

                self.callback({
                    'success': True,
                    'result': result,
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
