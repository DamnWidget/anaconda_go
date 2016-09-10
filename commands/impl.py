
# Copyright (C) 2016 - Oscar Campos <oscar.campos@member.fsf.org>
# This program is Free Software see LICENSE file for details

import traceback
from functools import partial

import sublime
import sublime_plugin

from anaconda_go.lib import go
from anaconda_go.lib.plugin import typing
from anaconda_go.lib.helpers import get_window_view
from anaconda_go.lib.plugin import Worker, Callback, is_code


class AnacondaGoImpl(sublime_plugin.TextCommand):
    """Execute Impl command and insert the returned implemntation
    """

    def __init__(self, edit: sublime.Edit):
        super(AnacondaGoImpl, self).__init__(edit)
        self.impl = None

    def run(self, edit: sublime.Edit) -> None:

        receiver, iface = None, None

        def receiver_done(data):
            global receiver
            receiver = data

        def iface_done(data):
            global iface
            iface = data

        try:
            sublime.active_window().show_input_panel(
                "Struct Name:", "Receiver", receiver_done, None, None
            )
            if receiver is None:
                return

            sublime.active_window().show_input_panel(
                "Interface to Implement:", "", iface_done, None, None
            )
            if iface is None:
                return

            data = {
                'vid': self.view.id(),
                'settings': {
                    'receiver': receiver,
                    'iface': iface
                },
                'go_env': {
                    'GOROOT': go.GOROOT,
                    'GOPATH': go.GOPATH,
                    'CGO_ENABLED': go.CGO_ENABLED
                },
                'method': 'impl',
                'handler': 'anaGonda',
            }
            Worker().execute(
                Callback(
                    on_success=partial(self.update_buffer, edit),
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

    def on_timeout(self, data):
        """Fired on timeouts from the callback
        """

        print('anaconda_go: impl timed out')

    def update_buffer(self, data, edit):
        """Update the buffer with the interface implementation
        """

        view = get_window_view(self.data['vid'])
        view.insert(edit, self.view.sel()[0].begin(), data['result'])
        self.data = None
