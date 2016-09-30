
# Copyright (C) 2016 - Oscar Campos <oscar.campos@member.fsf.org>
# This program is Free Software see LICENSE file for details

import traceback

import sublime
import sublime_plugin

from anaconda_go.lib import go
from anaconda_go.lib.plugin import typing
from anaconda_go.lib.helpers import get_symbol, get_settings
from anaconda_go.lib.plugin import Worker, Callback, ExplorerPanel, is_code


class AnacondaGoGoto(sublime_plugin.WindowCommand):
    """Execute godef/guru or both and goto any returnd definition
    """

    def run(self) -> None:
        try:
            view = self.window.active_view()
            self.view = view
            row, col = view.rowcol(view.sel()[0].begin())
            offset = view.text_point(row, col)

            code = view.substr(sublime.Region(0, view.size()))
            data = {
                'vid': view.id(),
                'code': code,
                'path': view.file_name(),
                'settings': {
                    'offset': offset,
                    'expr': get_symbol(code, row, col),
                    'modified_buffer': self._modified_buffer(view, code),
                    'guru_usage': get_settings(
                        view, 'anaconda_go_guru_usage', 'always'
                    )
                },
                'go_env': {
                    'GOROOT': go.GOROOT,
                    'GOPATH': go.GOPATH,
                    'CGO_ENABLED': go.CGO_ENABLED
                },
                'method': 'goto',
                'handler': 'anaGonda'
            }
            Worker().execute(
                Callback(
                    on_success=self._on_success,
                    on_failure=self._on_failure,
                    on_timeout=self._on_timeout
                ),
                **data
            )
        except Exception as err:
            print('anaconda_go: goto error')
            print(traceback.print_exc())

    def is_enabled(self) -> bool:
        """Determine if this command is enabled or not
        """

        if len(sublime.active_window().views()) == 0:
            return False

        if not go.ANAGONDA_PRESENT:
            return False

        return is_code(self.window.active_view(), lang='go')

    def _on_success(self, data):
        """Called when we have a result from the query
        """

        if not data['result']:
            sublime.status_message('Unable to find symbol')
            return

        ExplorerPanel(self.view, data['result']).show([])

    def _on_failure(self, data: typing.Dict) -> None:
        """Fired on failures from the callback
        """

        print('anaconda_go: goto error')
        print(data['error'])
        sublime.status_message(data['error'])

    def _on_timeout(self, data: typing.Dict) -> None:
        """Fired when the callback times out
        """

        print('Golang goto definition timed out')

    def _modified_buffer(self, view: sublime.View, code: str) -> str:
        """Guru needs this to use unsaved buffers instead of files
        """

        return '\n'.join([
            view.file_name(), str(len(code.encode('utf8'))), code
        ])
