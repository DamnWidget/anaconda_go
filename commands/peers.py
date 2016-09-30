
# Copyright (C) 2016 - Oscar Campos <oscar.campos@member.fsf.org>
# This program is Free Software see LICENSE file for details

import traceback

import sublime
import sublime_plugin

from anaconda_go.lib import go
from anaconda_go.lib.plugin import typing, ExplorerPanel
from anaconda_go.lib.helpers import get_settings, get_scope
from anaconda_go.lib.plugin import Worker, Callback, is_code


class AnacondaGoPeers(sublime_plugin.WindowCommand):
    """Execute guru peers and show it's results in an ExplorerPanel
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
                'method': 'peers',
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
            'sends': data['result'].get('sends'),
            'allocs': data['result'].get('allocs'),
            'closes': data['result'].get('closes'),
            'receives': data['result'].get('receives')
        }
        for k, v in _imp.items():
            if v is not None:
                refs = []
                for ref in v:
                    title = data['result']['type']
                    if k in ('receives', 'sends'):
                        name = data['result']['type'].replace('<-', '')
                        title = '{} {}'.format(
                            '<-' if k == 'receives' else name,
                            '<-' if k == 'sends' else name
                        )
                    refs.append({
                        'title': title,
                        'position': ref,
                        'location': 'File: {} Line: {} Column: {}'.format(
                            *ref.split(':')
                        )
                    })
                symbols.append({
                    'title': k.capitalize().replace('_', ' '),
                    'options': refs
                })

        ExplorerPanel(self.view, symbols).show([], True)

    def _on_failure(self, data: typing.Dict) -> None:
        """Fired on failures from the callback
        """

        print('anaconda_go: peers error')
        print(data['error'])
        sublime.status_message(data['error'])

    def _on_timeout(self, data: typing.Dict) -> None:
        """Fired when the callback times out
        """

        print('Golang peers timed out')

    def _modified_buffer(self, view: sublime.View, code: str) -> str:
        """Guru needs this to use unsaved buffers instead of files
        """

        return '\n'.join([
            view.file_name(), str(len(code.encode('utf8'))), code
        ])
