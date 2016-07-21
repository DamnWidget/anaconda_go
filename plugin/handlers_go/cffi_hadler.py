
# Copyright (C) 2013 - 2016 - Oscar Campos <oscar.campos@member.fsf.org>
# This program is Free Software see LICENSE file for details

import logging

from lib import anaconda_handler

__cffi_found__ = False
__cffi_error__ = ''

try:
    from .anagonda import anaGonda
    __cffi_found__ = True
except ImportError as e:
    __cffi_error__ = 'Could not import cffi: {0}'.format(e)
    logging.error(__cffi_error__)


class CFFIHandler(anaconda_handler.AnacondaHandler):
    """Handle requests to manage CFFI related operations
    """

    __handler_type__ = 'cffi'

    def available(self):
        """Check if CFFI is available (this is called from ST3)
        """

        self._errback()

    def prepare(self, version, settings):
        """Prepare the CFFI environment or return if already prepared
        """

        if not __cffi_found__:
            return self._errback()

        anagonda = anaGonda(**settings)
        if anagonda.prepare_env(version):
            self.callback({
                'success': True,
                'uid': self.uid,
                'vid': self.vid
            })
        else:
            self.callback({
                'success': False,
                'error': anagonda.error,
                'uid': self.uid,
                'vid': self.vid
            })

    def _errback(self):
        """Common errback to use on errors
        """

        self.callback({
            'success': __cffi_found__,
            'error': __cffi_error__,
            'uid': self.uid,
            'vid': self.vid
        })
