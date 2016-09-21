

# Copyright (C) 2013 - 2016 - Oscar Campos <oscar.campos@member.fsf.org>
# This program is Free Software see LICENSE file for details

import logging
import traceback

from ..anagonda.context import gogetdoc
from commands.base import Command


class GoGetDoc(Command):
    """Run go doc for the given expr
    """

    def __init__(self, callback, uid, vid, path, offset, buf, go_env):
        self.vid = vid
        self.path = path
        self.offset = offset
        self.buf = buf
        self.go_env = go_env
        super(GoGetDoc, self).__init__(callback, uid)

    def run(self):
        """Run the command
        """

        try:
            with gogetdoc.GoGetDoc(
                    self.path, self.offset, self.buf, self.go_env) as docs:
                self.callback({
                    'success': True,
                    'result': docs,
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
