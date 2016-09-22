
# Copyright (C) 2014 - Oscar Campos <oscar.campos@member.fsf.org>
# This program is Free Software see LICENSE file for details

from anaconda_go.lib.go.detector import GolangDetector

AVAILABLE = False
GOROOT = None  # type: str
GOPATH = None  # type: str
CGO_ENABLED = False  # type: bool
ANAGONDA_PRESENT = False  # type: bool
PACKAGE_BROWSE = {}  # type: Dict


_detector = GolangDetector()


def init(version) -> None:
    """Initialize go sub systems
    """
    global AVAILABLE, GOROOT, GOPATH, CGO_ENABLED, _detector

    GOROOT, GOPATH, CGO_ENABLED = _detector()
    if GOROOT is not None and GOPATH is not None:
        AVAILABLE = True
