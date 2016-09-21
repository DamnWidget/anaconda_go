
# Copyright (C) 2013 - 2016 - Oscar Campos <oscar.campos@member.fsf.org>
# This program is Free Software see LICENSE file for details

import logging
import traceback

from ..anagonda.context import godoc
from commands.base import Command


class Doc(Command):
    """Run go doc for the given expr
    """

    def __init__(self, callback, uid, vid, path, expr, private, go_env):
        self.vid = vid
        self.path = path
        self.expr = expr
        self.private = private
        self.go_env = go_env
        super(Doc, self).__init__(callback, uid)

    def run(self):
        """Run the command
        """

        try:
            with godoc.Doc(
                    self.path, self.expr, self.private, self.go_env) as docs:
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
