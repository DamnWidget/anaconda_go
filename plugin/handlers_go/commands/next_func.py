
# Copyright (C) 2013 - 2016 - Oscar Campos <oscar.campos@member.fsf.org>
# This program is Free Software see LICENSE file for details

import logging
import traceback

from ..anagonda.context import motion
from commands.base import Command


class NextFunc(Command):
    """Run motion -mode next
    """

    def __init__(self, callback, uid, vid, f, off, pcomments, go_env):
        self.vid = vid
        self.path = f
        self.offset = off
        self.parse_comments = pcomments
        self.go_env = go_env
        super(NextFunc, self).__init__(callback, uid)

    def run(self):
        """Run the command
        """

        try:
            with motion.Motion(
                self.path, None, self.offset, 'next',
                    None, self.parse_comments, self.go_env) as data:
                result = []
                if 'err' not in data:
                    g = data['func']['func']
                    result = [
                        {
                            'title': g['filename'],
                            'position': '{}:{}:{}'.format(
                                g['filename'], g['line'], g['col']
                            )
                        }
                    ]
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
