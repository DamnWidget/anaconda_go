
# Copyright (C) 2016 - Oscar Campos <oscar.campos@member.fsf.org>
# This program is Free Software see LICENSE file for details

import traceback

import sublime
import sublime_plugin

from anaconda_go.lib import go
from anaconda_go.lib.plugin import typing, ExplorerPanel
from anaconda_go.lib.helpers import get_settings, get_scope
from anaconda_go.lib.plugin import Worker, Callback, is_code


class AnacondaGoReferrers(sublime_plugin.TextCommand):
    """Execute guru referrers and return it's results
    """

    def run(self, edit: sublime.Edit) -> None:
        try:
            view = self.view
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
                'method': 'referrers',
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
        except:
            print('anaconda_go: referrers error')
            print(traceback.print_exc())

    def is_enabled(self) -> bool:
        """Determine if this command is enabled or not
        """

        if len(sublime.active_window().views()) == 0:
            return False

        if not go.ANAGONDA_PRESENT:
            return False

        return is_code(self.view, lang='go')

    def _on_success(self, data: typing.Dict) -> None:
        """Process result and normalize it for anaconda's ExplorerPanel
        """

        if not data['result']:
            sublime.status_message('Unable to find symbol')
            return

        symbols = []
        if len(data['result']) > 1:
            for result in data['result'][1:]:
                refs = []
                for ref in result.get('refs', []):
                    path, line, col = ref['pos'].split(':')
                    refs.append({
                        'title': ref['text'].replace('\t', ''),
                        'position': ref['pos'],
                        'location': 'File: {} Line: {} Column: {}'.format(
                            path, line, col
                        )
                    })
                symbols.append({
                    'title': result['package'],
                    'options': refs
                })

        ExplorerPanel(self.view, symbols).show([], True)

    def _on_failure(self, data: typing.Dict) -> None:
        """Fired on failures from the callback
        """

        print('anaconda_go: referrers error')
        print(data['error'])
        sublime.status_message(data['error'])

    def _on_timeout(self, data: typing.Dict) -> None:
        """Fired when the callback times out
        """

        print('Golang referrers timed out')

    def _modified_buffer(self, view: sublime.View, code: str) -> str:
        """Guru needs this to use unsaved buffers instead of files
        """

        return '\n'.join([
            view.file_name(), str(len(code.encode('utf8'))), code
        ])
