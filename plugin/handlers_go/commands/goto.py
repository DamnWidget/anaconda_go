
# Copyright (C) 2013 - 2016 - Oscar Campos <oscar.campos@member.fsf.org>
# This program is Free Software see LICENSE file for details

import logging
import traceback

from ..anagonda.context import guru, godef
from ..anagonda.context.error import AnaGondaError
from commands.base import Command


class Goto(Command):
    """Run guru or godef
    """

    def __init__(self, callback, uid, vid, code, filename, settings, go_env):
        self.vid = vid
        self.code = code
        self.path = filename
        self.settings = settings
        self.go_env = go_env
        super(Goto, self).__init__(callback, uid)

    def run(self):
        """Run the command
        """

        try:
            self.callback({
                'success': True,
                'result': self.goto(),
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

    def goto(self):
        """Run GoDef, GuRu or both and return back a ready to use result
        """

        guru_usage = self.settings.get('guru_usage', 'always')
        if guru_usage == 'always':
            return self._normalize(self.guru())

        defs = []
        try:
            defs = self._normalize(self.godef())
        except AnaGondaError as err:
            logging.error('GoDef failed with error: {0}'.format(err))
            if guru_usage == 'fallback':
                defs = self._normalize(self.guru())
        else:
            if len(defs) == 0 and guru_usage == 'fallback':
                defs = self._normalize(self.guru())

        return defs

    def guru(self):
        """Use Guru context and return back the result
        """

        with guru.Guru(
            None, 'definition', self.path,
            self.settings.get('offset', 0),
                self.settings.get('modified_buffer'), self.go_env) as defs:
            return defs

    def godef(self):
        """Use GoDef context and return back the result
        """

        with godef.GoDef(
            self.code, self.path,
                self.settings.get('expr', ''), False, self.go_env) as defs:
            return defs

    def _normalize(self, defs):
        """Normalize tools output into anaconda's goto format
        """

        if defs['tool'] == 'guru':
            try:
                return [{
                    'title': defs['objpos'].split(':')[0],
                    'position': defs['objpos']
                }]
            except:
                return []

        return [{
            'title': defs['filename'],
            'position': '{}:{}:{}'.format(
                defs['filename'], defs['line'], defs['column']
            )
        }]
