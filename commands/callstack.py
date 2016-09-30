
# Copyright (C) 2016 - Oscar Campos <oscar.campos@member.fsf.org>
# This program is Free Software see LICENSE file for details

import traceback

import sublime
import sublime_plugin

from anaconda_go.lib import go, panels
from anaconda_go.lib.plugin import typing
from anaconda_go.lib.helpers import get_settings, get_scope
from anaconda_go.lib.plugin import Worker, Callback, ExplorerPanel, is_code


class AnacondaGoCallstack(sublime_plugin.TextCommand):
    """Execute guru and callers any returnd definition
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
                'method': 'callstack',
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
            print('anaconda_go: callers error')
            print(traceback.print_exc())

    def is_enabled(self) -> bool:
        """Determine if this command is enabled or not
        """

        if len(sublime.active_window().views()) == 0:
            return False

        if not go.ANAGONDA_PRESENT:
            return False

        return is_code(self.view, lang='go')

    def _on_success(self, data):
        """Process result and normalize it for anaconda's goto
        """

        if get_settings(self.view, 'anaconda_go_print_callstack', True):
            # print the callstack in a doc panel
            panel = panels.DocPanel(self.view)
            panel.show()
            panel.print(self._pretiffy(data))

        callstack = []
        for result in data['result'].get('callers', []):
            f, l, c = result['pos'].split(':')
            callstack.append({
                'title': result['caller'],
                'location': 'File: {} Line: {} Column: {}'.format(f, l, c),
                'position': result['pos']
            })

        ExplorerPanel(self.view, callstack).show([])

    def _on_failure(self, data: typing.Dict) -> None:
        """Fired on failures from the callback
        """

        print('anaconda_go: callers error')
        print(data['error'])
        sublime.status_message(data['error'])

    def _on_timeout(self, data: typing.Dict) -> None:
        """Fired when the callback times out
        """

        print('Golang callers definition timed out')

    def _modified_buffer(self, view: sublime.View, code: str) -> str:
        """Guru needs this to use unsaved buffers instead of files
        """

        return '\n'.join([
            view.file_name(), str(len(code.encode('utf8'))), code
        ])

    def _pretiffy(self, data: typing.Dict) -> str:
        """Pretiffy callstack for print into panel
        """

        callstack = []
        callers = data['result'].get('callers', [])
        for i in range(len(callers)):
            callstack.append('{0}{3}{1}\n{0}{3}{2}'.format(
                '\t' * i,
                callers[i]['caller'],
                callers[i]['pos'],
                '|_ ' if i > 0 else ''
            ))

        return '\n'.join(callstack)
