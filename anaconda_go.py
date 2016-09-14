
# Copyright (C) 2013 - 2016 - Oscar Campos <oscar.campos@member.fsf.org>
# This program is Free Software see LICENSE file for details

"""AnacondaGO is a Go linting/autocompleter/IDE for Sublime Text 3
"""

import os
import sublime

from anaconda_go.plugin_version import anaconda_required_version, ver

from anaconda_go.lib import go
from Default.exec import ExecCommand
from anaconda_go.lib.plugin import anaconda_version

if anaconda_required_version > anaconda_version:
    raise RuntimeError(
        'AnacondaGO requires version {} or better of anaconda but {} '
        'is installed'.format(
            '.'.join(str(i) for i in anaconda_required_version), ver
        )
    )
else:
    from anaconda_go.commands import *
    from anaconda_go.listeners import *


def plugin_loaded() -> None:
    """Sublime Text 3 calls this function automatically after load the plugin
    """

    go.init(ver)
    if go.AVAILABLE is True:
        _install_go_tools()
        if os.path.exists(os.path.join(go.GOPATH, 'bin', 'gometalinter.v1')):
            go.ANAGONDA_PRESENT = True


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
    exe = ExecCommand(sublime.active_window())
    exe.run(
        shell_cmd='{} get -x -u {}'.format(
            go._detector.go_binary, ' '.join(_go_dependencies)
        ),
        file_regex=r'[ ]*File \"(...*?)\", line ([0-9]*)',
        env=env
    )
