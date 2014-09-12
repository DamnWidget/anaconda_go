
# Copyright (C) 2014 - Oscar Campos <oscar.campos@member.fsf.org>
# This program is Free Software see LICENSE file for details

from .runtime import Runtime
from .detector import GolangDetector


GO_AVAILABLE = False
GOROOT = None
GOPATH = None
CGO_ENABLED = None

_detector = GolangDetector()
runtime = None


def init(version):
    """Initialize go sub systems
    """
    global GO_AVAILABLE, GOROOT, GOPATH, CGO_ENABLED, runtime

    GO_ROOT, GOPATH, CGO_ENABLED = _detector()
    if GOROOT is not None and GOPATH is not None:
        GO_AVAILABLE = True
        runtime = Runtime(GO_ROOT, GOPATH, CGO_ENABLED, version)
