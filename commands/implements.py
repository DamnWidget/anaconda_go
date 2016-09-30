
# Copyright (C) 2016 - Oscar Campos <oscar.campos@member.fsf.org>
# This program is Free Software see LICENSE file for details

import traceback

import sublime
import sublime_plugin

from anaconda_go.lib import go
from anaconda_go.lib.plugin import typing, ExplorerPanel
from anaconda_go.lib.helpers import get_settings, get_scope
from anaconda_go.lib.plugin import Worker, Callback, is_code


class AnacondaGoImplements(sublime_plugin.WindowCommand):
    """Execute guru implements and show it's results in an ExplorerPanel
    """

    def run(self) -> None:
        try:
            view = self.window.active_view()
            self.view = view
            scope = get_settings(view, 'anaconda_go_guru_scope')
            row, col = view.rowcol(view.sel()[0].begin())
            offset = view.text_point(row, col)
            code = view.substr(sublime.Region(0, view.size()))

            data = {
                'vid': view.id(),
                'scope': scope if scope is not None else get_scope(view, go.GOPATH),  # noqa
                'path': view.file_name(),
                'offset': offset,
                'modified_buffer': self._modified_buffer(view, code),
                'go_env': {
                    'GOROOT': go.GOROOT,
                    'GOPATH': go.GOPATH,
                    'CGO_ENABLED': go.CGO_ENABLED
                },
                'method': 'implements',
                'handler': 'anaGonda'
            }
            Worker().execute(
                Callback(
                    on_success=self._on_success,
                    on_failure=self._on_failure,
                    on_timeout=self._on_timeout
                ), **data
            )
        except:
            print('anaconda_go: implements error')
            print(traceback.print_exc())

    def is_enabled(self) -> bool:
        """Determine if this command is enabled or not
        """

        if len(sublime.active_window().views()) == 0:
            return False

        if not go.ANAGONDA_PRESENT:
            return False

        return is_code(self.window.active_view(), lang='go')

    def _on_success(self, data: typing.Dict) -> None:
        """Process result and normalize it for anaconda's ExplorerPanel
        """

        if not data['result']:
            sublime.status_message('Uable to find symbol data')
            return

        symbols = []
        _imp = {
            'implements': data['result'].get('from'),
            'implemented_by': data['result'].get('to')
        }
        for k, v in _imp.items():
            if v is not None:
                interfaces = []
                for interface in v:
                    interfaces.append({
                        'title': interface['name'],
                        'position': interface['pos'],
                        'location': 'File: {} Line: {} Column: {}'.format(
                            *interface['pos'].split(':')
                        )
                    })
                symbols.append({
                    'title': k.capitalize().replace('_', ' '),
                    'options': interfaces
                })

        if not symbols:
            sublime.status_message(
                '{} does not implements or is an interface'.format(
                    data['result'].get('type', {}).get('name', 'Symbol')
                )
            )
        else:
            ExplorerPanel(self.view, symbols).show([], True)

    def _on_failure(self, data: typing.Dict) -> None:
        """Fired on failures from the callback
        """

        print('anaconda_go: implements error')
        print(data['error'])
        sublime.status_message(data['error'])

    def _on_timeout(self, data: typing.Dict) -> None:
        """Fired when the callback times out
        """

        print('Golang implements timed out')

    def _modified_buffer(self, view: sublime.View, code: str) -> str:
        """Guru needs this to use unsaved buffers instead of files
        """

        return '\n'.join([
            view.file_name(), str(len(code.encode('utf8'))), code
        ])
