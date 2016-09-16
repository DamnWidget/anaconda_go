
# Copyright (C) 2013 - 2016 - Oscar Campos <oscar.campos@member.fsf.org>
# This program is Free Software see LICENSE file for details

import logging
import traceback

from ..anagonda.context import motion
from commands.base import Command


class PackageFuncs(Command):
    """Run motion -mode decls -include func
    """

    def __init__(self, callback, uid, vid, path, parse_comments, go_env):
        self.vid = vid
        self.path = path
        self.parse_comments = parse_comments
        self.go_env = go_env
        super(PackageFuncs, self).__init__(callback, uid)

    def run(self):
        """Run the command
        """

        try:
            with motion.Motion(
                None, self.path, None, 'decls', 'func',
                    self.parse_comments, self.go_env) as data:
                self.callback({
                    'success': True,
                    'result': data.get('decls', []),
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
