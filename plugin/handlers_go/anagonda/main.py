
# Copyright (C) 2013 - 2016 - Oscar Campos <oscar.campos@member.fsf.org>
# This program is Free Software see LICENSE file for details

import os
import glob
import logging
from collections import namedtuple

_cffi = None
try:
    from cffi import FFI
    _cffi = FFI
except ImportError:
    msg = 'cffi is not available...'
    print(msg)
    logging.info(msg)

from compilation import Target, AnagondaCompileError


class anaGonda(object):
    """This object controls the anaGonda Go wrapper
    """

    _library_path = os.path.join(os.path.dirname(__file__), 'lib')
    _named_tuples = {
        'env': namedtuple('Environ', 'goroot gopath cgo_enabled'),
        'compiler': namedtuple('Compiler', 'ver type steps')
    }

    def __init__(self, goroot, gopath, cgo=True):
        self._env = self._ctx_named_tuples.get('env')(
            goroot, gopath, cgo
        )

    @property
    def nt(self):
        """Return named tuples value
        """
        return self._named_tuples.values()

    def prepare_env(self, version):
        """Prepare the anaGonda environment, compile the binary if necessary
        """

        try:
            self._check_binary(version)
            self._check_library(version)
            if _cffi is not None:
                from compilation import CFFIOffLine
                with CFFIOffLine(Target._library_path) as cffi_compiler:
                    cffi_compiler.compile()
        except AnagondaCompileError as error:
            print(error)
            logging.error(error)
            return False

        return True

    def _check_binary(self, ver):
        """Check for the existence of anaGonda binary or compile it
        """

        ctx = namedtuple('Context', (i for i in (e._fields for e in self._nt)))
        target = Target(ctx(
            self._env.goroot, self._env.gopath, self._env.cgo_enabled,
            ver, 'bin', []
        ))

        path = os.path.join(Target._binary_path, target.bin_name)
        if os.path.exists(path):
            msg = 'found {0} skipping compilation...'.format(path)
            print(msg)
            logging.info(msg)
            return

        # delete any previous version
        [os.unlink(f)
            for f in glob.glob(os.path.join(Target._binary_path, '*.bin'))]
        target.compile()

    def _check_library(self, ver):
        """Check for the existence of anaGonda library or compile it
        """

        ctx = namedtuple('Context', (i for i in (e._fields for e in self._nt)))
        target = Target(ctx(
            self._env.goroot, self._env.gopath, self._env.cgo_enabled,
            ver, 'lib', [{'cmd': 'go generate {0}'.format(
                os.path.relpath(Target._src_path))}
            ]
        ))

        path = os.path.join(Target._library_path, target.lib_name)
        if os.path.exists(path):
            msg = 'found {0} skipping compilation...'.format(path)
            print(msg)
            logging.info(msg)
            return

        # delete any previous version
        [os.unlink(f) for f in glob.glob(
            os.path.join(Target._library_path, target.lib_ext))]
        target.compile()
