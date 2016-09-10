
# Copyright (C) 2013 - 2016 - Oscar Campos <oscar.campos@member.fsf.org>
# This program is Free Software see LICENSE file for details

"""AnacondaGO is a Go linting/autocompleter/IDE for Sublime Text 3
"""

import os
import sublime

from anaconda_go.lib.plugin import typing
from anaconda_go.plugin_version import anaconda_required_version, ver

from anaconda_go.lib import go
from anaconda_go.lib.async_proc import AsyncProc
from anaconda_go.lib.plugin import anaconda_version

if anaconda_required_version > anaconda_version:
    raise RuntimeError(
        'AnacondaGO requires version {} or better of anaconda but {} '
        'is installed'.format(
            '.'.join(str(i) for i in anaconda_required_version), ver
        )
    )
else:
    from anaconda_go.commands import importer
    importer()


def plugin_loaded() -> None:
    """Sublime Text 3 calls this function automatically after load the plugin
    """

    go.init(ver)
    if go.AVAILABLE is True:
        _install_go_tools()


def _on_success(proc: AsyncProc) -> None:
    """Called when prepare call is successful
    """

    go.ANAGONDA_PRESENT = True
    proc.broadcast('Finished in {}s'.format(proc.elapsed))


def _on_failure(data: typing.Dict) -> None:
    """Called when prepare call fails
    """

    sublime.error_message(data['error'])


def _on_rtfailure(proc: AsyncProc):
    """Called when prepare call times out
    """

    proc.broadcast('Finished with errors: {} in {}s'.format(
        proc.error, proc.elapsed)
    )


def _install_go_tools():
    """Chec if the go tools are installed and install them if they are not
    """

    if os.path.exists(os.path.join(go.GOPATH, 'bin', 'gometalinter.v1')):
        return

    _go_dependencies = [
        'github.com/DamnWidget/godef',
        'golang.org/x/tools/cmd/guru',
        'github.com/fatih/motion',
        'github.com/josharian/impl',
        'github.com/nsf/gocode',
        'gopkg.in/alecthomas/gometalinter.v1'
    ]

    panel = sublime.active_window().get_output_panel('exec')
    panel.settings().set('wrap_width', 160)
    env = os.environ.copy()
    env.update({'GOPATH': go.GOPATH, 'GOROOT': go.GOROOT})
    sublime.active_window().run_command(
        'exec', {
            'shell_cmd': '{} get -x -u {}'.format(
                go._detector.go_binary, ' '.join(_go_dependencies)
            ),
            'file_regex': r'[ ]*File \"(...*?)\", line ([0-9]*)',
            'env': env

        }
    )
