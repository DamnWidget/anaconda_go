
# Copyright (C) 2016 - Oscar Campos <oscar.campos@member.fsf.org>
# This program is Free Software see LICENSE file for details

import traceback
from functools import partial

import sublime
import sublime_plugin

from anaconda_go.lib import go
from anaconda_go.lib.plugin import typing
from anaconda_go.lib.plugin import Worker, Callback, is_code


class AnacondaGoImpl(sublime_plugin.TextCommand):
    """Execute Impl command and insert the returned implemntation
    """

    impl = None

    def run(self, edit: sublime.Edit) -> None:

        if self.impl is not None:
            self.view.insert(edit, self.view.sel()[0].begin(), self.impl)
            self.impl = None
            return

        sublime.active_window().show_input_panel(
            "Struct Name:", "Receiver",
            partial(self._receiver_done, edit), None, None
        )

    def _receiver_done(self, edit: sublime.Edit, receiver: str) -> None:

        if receiver is None or receiver == '':
            return

        sublime.active_window().show_input_panel(
            "Interface to Implement:", "",
            partial(self._exec, edit, receiver), None, None
        )

    def _exec(self, edit: sublime.Edit, receiver: str, iface: str) -> None:

        if iface is None or iface == '':
            return

        try:
            data = {
                'vid': self.view.id(),
                'receiver': receiver,
                'iface': iface,
                'go_env': {
                    'GOROOT': go.GOROOT,
                    'GOPATH': go.GOPATH,
                    'CGO_ENABLED': go.CGO_ENABLED
                },
                'method': 'impl',
                'handler': 'anaGonda'
            }
            Worker().execute(
                Callback(
                    on_success=self.update_buffer,
                    on_failure=self.on_failure,
                    on_timeout=self.on_timeout
                ),
                **data
            )
        except:
            print('anaconda_go error: {}'.format(traceback.format_exc()))

    def is_enabled(self) -> bool:
        """Determine if this command is enabled or not
        """

        if not go.ANAGONDA_PRESENT:
            return False

        return is_code(self.view, lang='go', ignore_comments=True)

    def on_failure(self, data: typing.Dict) -> None:
        """Fired on failures from the callback
        """

        print('anaconda_go: impl error')
        print(data['error'])
        sublime.status_message(data['error'])

    def on_timeout(self, data):
        """Fired on timeouts from the callback
        """

        print('anaconda_go: impl timed out')

    def update_buffer(self, data):
        """Update the buffer with the interface implementation
        """

        self.impl = data['result']
        sublime.set_timeout(self.view.run_command('anaconda_go_impl', 0))
