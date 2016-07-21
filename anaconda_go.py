
# Copyright (C) 2013 - 2016 - Oscar Campos <oscar.campos@member.fsf.org>
# This program is Free Software see LICENSE file for details

"""AnacondaGO is a Go linting/autocompleter/IDE for Sublime Text 3
"""

import time
import sublime

from anaconda_go.lib.plugin import Worker, Callback, typing
from anaconda_go.plugin_version import anaconda_required_version, ver

from anaconda_go.lib import go
from anaconda_go.lib.plugin import anaconda_version

if anaconda_required_version > anaconda_version:
    raise RuntimeError(
        'AnacondaGO requires version {} or better of anaconda but {} '
        'is installed'.format(
            '.'.join(str(i) for i in anaconda_required_version), ver
        )
    )

CFFI_PRESENT = False


def plugin_loaded() -> None:
    """Sublime Text 3 calls this function automatically after load the plugin
    """

    go.init(ver)
    if go.AVAILABLE is True:
        _attempt_prepare_call()


def _on_success(data: typing.Dict) -> None:
    """Called when prepare call is successful
    """

    global CFFI_PRESENT
    CFFI_PRESENT = True


def _on_failure(data: typing.Dict) -> None:
    """Called when prepare call fails
    """

    sublime.error_message(data['error'])


def _on_timeout(*data):
    """Called when prepare call times out
    """

    print('Prepare remote call timed out, re-attempting in 1s')
    time.sleep(1)
    _attempt_prepare_call()


def _attempt_prepare_call():
    """Attempt a remote call to prepare
    """

    data_tmp = {
        'vid': sublime.active_window().active_view().id(),
        'version': ver,
        'settings': {
            'goroot': go.GOROOT,
            'gopath': go.GOPATH,
            'cgo': go.CGO_ENABLED
        },
        "method": "prepare",
        "handler": "cffi"
    }
    Worker.execute(
        Callback(
            on_success=_on_success,
            on_failure=_on_failure,
            on_timeout=_on_timeout
        ),
        **data_tmp
    )

    # make sure our on_timeout gets called if our request got swallow
    # because the JsonServer was not ready yet and the callback could
    # not be registered as there were no JsonClient yet
    sublime.set_timeout(_on_timeout, 1000)
