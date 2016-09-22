
# Copyright (C) 2016 - Oscar Campos <oscar.campos@member.fsf.org>
# This program is Free Software see LICENSE file for details

import traceback

import sublime
import sublime_plugin
from Default.exec import ExecCommand

from anaconda_go.lib import go
from anaconda_go.lib.plugin import typing
from anaconda_go.lib.helpers import get_symbol, get_settings
from anaconda_go.lib.plugin import Worker, Callback, is_code


class AnacondaGoDoc(sublime_plugin.WindowCommand):
    """Execute godef/guru or both and goto any returnd definition
    """

    @property
    def go_version(self):
        """Return back a tuple containing the go version
        """

        ver = go._detector.go_version
        if ver == b'':
            return (0, 0)

        ver = ver.decode('utf8')
        return tuple(int(v) for v in ver.replace('go', '').split('.'))

    def run(self) -> None:
        try:
            view = self.window.active_view()
            self.view = view
            row, col = view.rowcol(view.sel()[0].begin())
            code = view.substr(sublime.Region(0, view.size()))
            data = {
                'vid': view.id(),
                'path': view.file_name(),
                'expr': get_symbol(code, row, col),
                'private': get_settings(
                    view, 'anaconda_go_doc_private_symbols', False),
                'force': get_settings(
                    view, 'anaconda_go_force_go_doc_usage', False),
                'offset': view.text_point(*view.rowcol(view.sel()[0].begin())),
                'buf': self.modified_buffer(view),
                'go_env': {
                    'GOROOT': go.GOROOT,
                    'GOPATH': go.GOPATH,
                    'CGO_ENABLED': go.CGO_ENABLED,
                    'GO_VERSION': self.go_version
                },
                'method': 'doc',
                'handler': 'anaGonda'
            }
            Worker().execute(
                Callback(
                    on_success=self.on_success,
                    on_failure=self._on_failure,
                    on_timeout=self._on_timeout
                ),
                **data
            )
        except Exception as err:
            print('anaconda_go: go doc error')
            print(traceback.print_exc())

    def is_enabled(self) -> bool:
        """Determine if this command is enabled or not
        """

        if len(sublime.active_window().views()) == 0:
            return False

        if not go.ANAGONDA_PRESENT:
            return False

        view = self.window.active_view()
        return is_code(view, lang='go', ignore_comments=True)

    def modified_buffer(self, view: sublime.View) -> str:
        """Guru needs this to use unsaved buffers instead of files
        """

        code = view.substr(sublime.Region(0, view.size()))
        return '\n'.join([
            view.file_name(), str(len(code.encode('utf8'))), code
        ])

    def on_success(self, data):
        """Process the results and show them into the exec panel
        """

        exe = ExecCommand(self.window)
        exe.run(
            shell_cmd='echo "{}\n"'.format(data['result']),
            file_regex=r'(...*?):([0-9]*):([0-9]*)',
            quiet=True,
        )
        exe.hide_phantoms()

    def _on_failure(self, data: typing.Dict) -> None:
        """Fired on failures from the callback
        """

        print('anaconda_go: go doc error')
        print(data['error'])

    def _on_timeout(self, data: typing.Dict) -> None:
        """Fired when the callback times out
        """

        print('Golang go doc definition timed out')
