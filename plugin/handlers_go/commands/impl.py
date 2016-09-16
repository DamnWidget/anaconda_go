
# Copyright (C) 2013 - 2016 - Oscar Campos <oscar.campos@member.fsf.org>
# This program is Free Software see LICENSE file for details

import logging
import traceback

from ..anagonda.context import impl
from commands.base import Command


class Impl(Command):
    """Run impl
    """

    def __init__(self, callback, uid, vid, receiver, iface, go_env):
        self.vid = vid
        self.receiver = receiver
        self.iface = iface
        self.go_env = go_env
        super(Impl, self).__init__(callback, uid)

    def run(self):
        """Run the command
        """

        try:
            with impl.Impl(self.receiver, self.iface, self.go_env) as data:
                self.callback({
                    'success': True,
                    'result': data,
                    'uid': self.uid,
                    'vid': self.vid
                })
        except Exception as error:
            logging.error(error)
            logging.debug(traceback.format_exc())
            self.callback({
                'success': False,
                'error': error,
                'uid': self.uid,
                'vid': self.vid
            })
