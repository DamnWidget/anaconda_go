
# Copyright (C) 2013 - 2016 - Oscar Campos <oscar.campos@member.fsf.org>
# This program is Free Software see LICENSE file for details

import sys
import json
from collections import namedtuple

try:
    from _anagonda import ffi, lib as cffi_lib
    CFFI_SUPPORTED = True
except ImportError:
    import ctypes
    CFFI_SUPPORTED = False

lib = None


def load_lib(library_file):
    """Load the given library file
    """

    global lib

    if CFFI_SUPPORTED:
        lib = cffi_lib
        return

    lib = ctypes.cdll.LoadLibrary(library_file)


class Command(object):
    """All commands that allocate memory must inherit from this class
    """

    def __init__(self):
        self._ptr = None

    def __exit__(self, *exc):
        """Free the Go allocated memory
        """

        lib.FreeMemory(self._ptr)

    def cast(self):
        """Cast the internal pointer to Python str type
        """

        if CFFI_SUPPORTED:
            return self.__cffi_cast()

        return self.__ctypes_cast()

    def __cffi_cast(self):
        """Cast the pointer to Python str using CFFI
        """

        return ffi.string(self._ptr)

    def __ctypes_cast(self):
        """Cast the pointer to Python str using Ctypes
        """

        return ctypes.cast(self._ptr, ctypes.c_char_p).value


class GetEnv(Command):
    """
    Call Go library GetEnv stores the retuned value in a
    Python owned dict and free the Go allocated memory
    """

    def __enter__(self):
        """
        Call the GetEnv method in the underlying
        Go library and return a  Python memory owned string
        """

        self._ptr = lib.GetEnv()
        if sys.version_info >= (3,):
            return json.loads(self.cast().decode())

        return json.loads(self.cast())


class SetEnvironment(object):
    """Call Go library SetEnvironment
    """

    def __init__(self, goroot, gopath, cgo_enabled=True):
        Context = namedtuple('Context', 'goroot gopath cgo_enabled')
        self.ctx = Context(
            goroot=goroot, gopath=gopath, cgo_enabled=cgo_enabled)

    def __enter__(self):
        """Call the command and return a bool for success status
        """

        return bool(lib.SetEnvironment(
            self.ctx.goroot, self.ctx.gopath, self.ctx.cgo_enabled)
        )

    def __exit__(self, *ext):
        """Do nothing
        """

        pass


class CleanSocket(object):
    """Call Go library CleanSocket to remove the gocode socket
    """

    def __enter__(self):
        """Call the command and return a bool for success status
        """

        return bool(lib.CleanSocket())

    def __exit__(self, *ext):
        """Do nothing
        """

        pass


class AutoComplete(Command):
    """
    Call Go library AutoComplete function and return a Python
    memory owned dictionary, frees any Go allocated memory on exit
    """

    def __init__(self, code, file_path, offset):
        Context = namedtuple('Context', 'code file_path offset')
        self.ctx = Context(code=code, file_path=file_path, offset=offset)

    def __enter__(self):
        """Call the function and return a Python owned string
        """

        self._ptr = lib.AutoComplete(
            self.ctx.code, self.ctx.file_path, self.ctx.offset
        )
        if sys.version_info >= (3,):
            return json.loads(self.cast().decode())

        return json.loads(self.cast())


__all__ = ['lib', 'GetEnv', 'SetEnvironment', 'AutoComplete']
