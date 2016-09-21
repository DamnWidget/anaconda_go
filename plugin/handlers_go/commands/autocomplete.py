
# Copyright (C) 2013 - 2016 - Oscar Campos <oscar.campos@member.fsf.org>
# This program is Free Software see LICENSE file for details

import logging
import traceback

from ..anagonda.context.autocomplete import AutoComplete
from commands.base import Command


class Gocode(Command):
    """Run GoCode
    """

    def __init__(self, callback, uid, vid, code, path, offset, param, go_env):
        self.vid = vid
        self.path = path
        self.code = code
        self.path = path
        self.offset = offset
        self.add_params = param
        self.go_env = go_env
        super(Gocode, self).__init__(callback, uid)

    def run(self):
        """Run the command
        """

        try:
            with AutoComplete(
                    self.code, self.path,
                    self.offset, self.add_params, self.go_env) as comps:
                self.callback({
                    'success': True,
                    'completions': comps,
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
