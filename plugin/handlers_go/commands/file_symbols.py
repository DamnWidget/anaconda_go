
# Copyright (C) 2013 - 2016 - Oscar Campos <oscar.campos@member.fsf.org>
# This program is Free Software see LICENSE file for details

import logging
import traceback

from ..anagonda.context import motion
from commands.base import Command


class FileSymbols(Command):
    """Run motion -i mode decls -include func,type
    """

    def __init__(self, callback, uid, vid, path, parse_comments, go_env):
        self.vid = vid
        self.path = path
        self.parse_comments = parse_comments
        self.go_env = go_env
        super(FileSymbols, self).__init__(callback, uid)

    def run(self):
        """Run the command
        """

        try:
            with motion.Motion(
                self.path, None, None, 'decls', 'func,type',
                    self.parse_comments, self.go_env) as data:

                if 'decls' not in data:
                    self.callback({
                        'success': True,
                        'result': [],
                        'uid': self.uid,
                        'vid': self.vid
                    })
                    return

                decls = [d for d in data['decls'] if d['keyword'] == 'type']
                decls += [d for d in data['decls'] if d['keyword'] != 'type']
                self.callback({
                    'success': True,
                    'result': decls or [],
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
